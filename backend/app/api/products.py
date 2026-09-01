from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.domain.models import NormalizedProduct, ReviewProduct
from app.services.enrichment import enrich, suggest
from app.services.images import ImageJob, ImageKind, pipeline
from app.services.llm import get_provider
from app.services.llm.base import EnrichmentResult
from app.services.pipeline import review as review_product
from app.services.shop import get_shop
from app.services.shop.base import ShopProduct

router = APIRouter()

class EnrichRequest(BaseModel):
    product: NormalizedProduct
    keywords: str = ""

@router.post("/products/enrich", response_model=NormalizedProduct)
def enrich_product(req: EnrichRequest) -> NormalizedProduct:
    """Generate a description and merge suggested taxonomy (non-destructive)."""
    return enrich(req.product, get_shop(), provider=get_provider(), keywords=req.keywords)

@router.post("/products/suggest", response_model=EnrichmentResult)
def suggest_taxonomy(req: EnrichRequest) -> EnrichmentResult:
    """Return description + taxonomy suggestions without applying them."""
    return suggest(req.product, get_shop(), provider=get_provider(), keywords=req.keywords)

@router.post("/products/review", response_model=ReviewProduct)
def review_endpoint(product: NormalizedProduct) -> ReviewProduct:
    """Re-run validation + rebuild the completion checklist after an edit."""
    return review_product(product)

@router.post("/products/images", response_model=ImageJob)
async def create_image_job(
    file: UploadFile = File(...),
    kind: ImageKind = Form(...),
) -> ImageJob:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image.")
    return pipeline.start(data, kind)

@router.get("/products/images/{job_id}", response_model=ImageJob)
def poll_image_job(job_id: str) -> ImageJob:
    job = pipeline.poll(job_id)
    if job.stage.value == "failed" and job.error == "unknown job":
        raise HTTPException(status_code=404, detail="Unknown image job.")
    return job

@router.post("/products/export", response_model=ShopProduct)
def export_product(product: NormalizedProduct) -> ShopProduct:
    r = review_product(product)
    if not r.exportable:
        errors = [i.message for i in r.issues if i.blocking]
        incomplete = [c.key for c in r.checklist if c.required and not c.done]
        message = (
            "Fix the data errors before exporting."
            if errors
            else "Complete the required fields before exporting."
        )
        raise HTTPException(
            status_code=422,
            detail={"message": message, "errors": errors, "incomplete": incomplete},
        )
    return get_shop().create_product(product)

@router.get("/products/{product_number}", response_model=ShopProduct)
def get_exported_product(product_number: str) -> ShopProduct:
    found = get_shop().get_product(product_number)
    if found is None:
        raise HTTPException(status_code=404, detail="Product not found in shop.")
    return found
