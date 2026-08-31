from __future__ import annotations

from app.domain.models import ChecklistItem, NormalizedProduct

_MIN_DESCRIPTION_CHARS = 20

def build_checklist(p: NormalizedProduct) -> list[ChecklistItem]:
    basics_done = bool(
        p.name and p.name.strip()
        and p.product_number
        and p.retail_price is not None
    )

    if p.has_sizes:
        variants_done = any(v.active for v in p.variants)
    else:
        #a product without sizes is already good to go
        variants_done = True

    description_done = bool(
        p.description and len(p.description.strip()) >= _MIN_DESCRIPTION_CHARS
    )

    return [
        ChecklistItem(key="basics", label="Basic information", done=basics_done),
        ChecklistItem(key="variants", label="Sizes & variants", done=variants_done),
        ChecklistItem(key="category", label="Category", done=bool(p.categories)),
        ChecklistItem(key="description", label="Description", done=description_done),
        ChecklistItem(
            key="care", label="Care instructions", done=bool(p.care_instructions)
        ),
        ChecklistItem(
            key="images",
            label="Product images",
            done=bool(p.image_urls),
            required=False,
        ),
    ]