from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.domain.models import PipelineResult
from app.services.extraction import DEMO_DOCUMENTS, get_extractor
from app.services.pipeline import ingest_document

router = APIRouter()

_MAX_UPLOAD_BYTES = 8 * 1024 * 1024

@router.get("/documents")
def list_documents() -> list[dict]:
    return [
        {
            "supplier_id": d.supplier_id,
            "supplier_name": d.supplier_name,
            "filename": d.filename,
            "media_type": d.media_type,
            "kind": d.kind,
            "doc_number": d.doc_number,
            "doc_date": d.doc_date,
            "product_count": d.product_count,
        }
        for d in sorted(DEMO_DOCUMENTS.values(), key=lambda d: d.supplier_name.lower())
    ]

@router.get("/documents/{supplier_id}/file")
def document_file(supplier_id: str) -> FileResponse:
    demo = DEMO_DOCUMENTS.get(supplier_id.lower())
    if demo is None or not demo.path.exists():
        raise HTTPException(status_code=404, detail=f"No document for {supplier_id!r}.")
    return FileResponse(demo.path, media_type=demo.media_type, filename=demo.filename)

def _analyze(supplier_id: str, document: bytes, media_type: str) -> PipelineResult:
    demo = DEMO_DOCUMENTS.get(supplier_id.lower())
    if demo is None:
        raise HTTPException(status_code=404, detail=f"Unknown supplier: {supplier_id!r}")
    result = ingest_document(
        extractor=get_extractor(settings.document_extractor),
        supplier_id=demo.supplier_id,
        supplier_name=demo.supplier_name,
        document=document,
        media_type=media_type,
        filename=demo.filename,
    )
    if result.count == 0:
        raise HTTPException(status_code=422, detail="No products extracted from the document.")
    return result

@router.post("/documents/{supplier_id}/analyze", response_model=PipelineResult)
def analyze_bundled(supplier_id: str) -> PipelineResult:
    demo = DEMO_DOCUMENTS.get(supplier_id.lower())
    if demo is None or not demo.path.exists():
        raise HTTPException(status_code=404, detail=f"No document for {supplier_id!r}.")
    return _analyze(supplier_id, demo.path.read_bytes(), demo.media_type)

@router.post("/documents/{supplier_id}/extract", response_model=PipelineResult)
async def extract_uploaded(
    supplier_id: str, file: UploadFile = File(...)
) -> PipelineResult:
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Empty file.")
    if len(payload) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 8 MB).")
    return _analyze(
        supplier_id, payload, file.content_type or "application/octet-stream"
    )
