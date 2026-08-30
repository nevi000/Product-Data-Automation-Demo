from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import catalog, documents, errors, products, suppliers
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Demo version of an e-commerce product onboarding platform. "
        "Fictional suppliers, shop/LLM/image providers are mocked. "
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

errors.install(app)

app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(suppliers.router, prefix="/api", tags=["suppliers (developer)"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["catalog"])
app.include_router(products.router, prefix="/api", tags=["products"])

@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
