"""Session auth — sample, NOT wired into the app.

The production system sits behind a signed-cookie session check (and, in
deployment, an SSO gateway). This is a neutral, self-contained version of that
pattern for reference. It is intentionally *not* added to `app.main` — the demo
has no login and no protected routes.

To use it: set a secret, add `SessionAuthMiddleware` in `main.py`, and issue a
cookie from a real login handler.
"""

from __future__ import annotations

import hashlib
import hmac
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_COOKIE = "session"
_MAX_AGE = 12 * 60 * 60


def sign(user: str, secret: str, *, issued_at: float | None = None) -> str:
    issued_at = issued_at if issued_at is not None else time.time()
    payload = f"{user}:{int(issued_at)}"
    mac = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{mac}"


def verify(token: str, secret: str, *, max_age: int = _MAX_AGE) -> str | None:
    try:
        user, issued_at, mac = token.rsplit(":", 2)
    except ValueError:
        return None
    expected = hmac.new(
        secret.encode(), f"{user}:{issued_at}".encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, mac):
        return None
    if time.time() - int(issued_at) > max_age:
        return None
    return user


class SessionAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, secret: str, public_paths: set[str] | None = None):
        super().__init__(app)
        self.secret = secret
        self.public_paths = public_paths or {"/health"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.public_paths:
            return await call_next(request)
        token = request.cookies.get(_COOKIE, "")
        if verify(token, self.secret) is None:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        return await call_next(request)
