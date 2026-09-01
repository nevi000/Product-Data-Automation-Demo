from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.domain.models import PipelineResult
from app.services.pipeline import ingest
from app.suppliers import registry

router = APIRouter()

_MAX_UPLOAD_BYTES = 5 * 1024 * 1024

_SAMPLE_FILES = {
    "alpinewear": "alpinewear_feed.json",
    "urbanthreads": "urbanthreads_export.csv",
    "demoshoes": "demoshoes_catalog.html",
}

def _sample_count(supplier_id: str) -> int | None:
    name = _SAMPLE_FILES.get(supplier_id)
    if name is None:
        return None
    try:
        adapter = registry.get(supplier_id)
        payload = (settings.demo_data_dir / name).read_bytes()
        return ingest(adapter, payload).count
    except Exception:
        return None

@router.get("/suppliers")
def list_suppliers() -> list[dict]:
    return [
        {
            "id": m.id,
            "name": m.name,
            "input_format": m.input_format,
            "description": m.description,
            "sample_count": _sample_count(m.id),
        }
        for m in registry.list()
    ]

@router.get("/suppliers/{supplier_id}/sample", response_class=PlainTextResponse)
def sample_document(supplier_id: str) -> str:
    """Return the bundled demo feed for a supplier, so the UI has a one-click demo."""
    name = _SAMPLE_FILES.get(supplier_id.lower())
    if name is None:
        raise HTTPException(status_code=404, detail=f"No sample for {supplier_id!r}.")
    return (settings.demo_data_dir / name).read_text(encoding="utf-8")

@router.post("/suppliers/{supplier_id}/ingest", response_model=PipelineResult)
async def ingest_document(
    supplier_id: str,
    file: UploadFile = File(...),
    source_reference: str | None = Form(default=None),
) -> PipelineResult:
    try:
        adapter = registry.get(supplier_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None

    payload = await file.read()
    if len(payload) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 5 MB).")
    if not payload:
        raise HTTPException(status_code=400, detail="Empty file.")

    result = ingest(adapter, payload, source_reference=source_reference)
    if result.count == 0:
        raise HTTPException(
            status_code=422,
            detail="No products found in the document for this supplier.",
        )
    return result
