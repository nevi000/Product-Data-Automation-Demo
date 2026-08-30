"""Edge error mapping.

Internal typed errors are translated to HTTP status codes in exactly one place,
so handlers can raise domain errors and stay readable.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from app.services.extraction.base import (
    DocumentExtractionError,
    DocumentNotRecognized,
    UnsupportedMediaType,
)
from app.services.llm.base import LLMQuotaError
from app.services.shop.base import ShopWriteError
from app.suppliers.base import SupplierParseError


def install(app) -> None:
    @app.exception_handler(SupplierParseError)
    async def _parse(_: Request, exc: SupplierParseError):
        return JSONResponse(status_code=422, content={"detail": f"Could not parse document: {exc}"})

    @app.exception_handler(UnsupportedMediaType)
    async def _media(_: Request, exc: UnsupportedMediaType):
        return JSONResponse(status_code=415, content={"detail": str(exc)})

    @app.exception_handler(DocumentNotRecognized)
    async def _unrecognized(_: Request, exc: DocumentNotRecognized):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(DocumentExtractionError)
    async def _extract(_: Request, exc: DocumentExtractionError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(LLMQuotaError)
    async def _quota(_: Request, exc: LLMQuotaError):
        return JSONResponse(status_code=402, content={"detail": str(exc)})

    @app.exception_handler(ShopWriteError)
    async def _shop(_: Request, exc: ShopWriteError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(KeyError)
    async def _key(_: Request, exc: KeyError):
        return JSONResponse(status_code=404, content={"detail": str(exc).strip("'")})
