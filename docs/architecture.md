# Architecture

## Overview

The platform is a linear pipeline with a human review step in the middle:

```
supplier PDF / photo
   → extractor.extract        (DocumentExtractionProvider — production: supplier-specific LLM prompt;
                               demo: MockDocumentExtractor over bundled fictional documents)
   → normalize                (→ NormalizedProduct, supplier-agnostic)
   → validate + checklist     (ValidationIssue[] = bad data; ChecklistItem[] = not done yet)
   ─────────────  human review  ─────────────
   → enrich                    (description + taxonomy, via LLMProvider)
   → images                    (staged jobs, via ImageProvider)
   → shop.create_product       (payload builder + idempotent taxonomy writes)
```

A `SupplierAdapter` (JSON / CSV / HTML) is a second, developer-facing entry
point for suppliers that ship a machine-readable feed; it emits the same
`RawSupplierProduct` and joins the pipeline at `normalize`.

**Two quality gates, deliberately separate.** `validate()` answers "is this data
correct?" and returns typed `ValidationIssue`s (rare on well-formed imports).
`completeness.build_checklist()` answers "is this product ready to publish?" and
returns a typed checklist. The UI shows the first as errors and the second as
completion progress — never as scary warnings on a half-filled product.

## Backend modules

### `app/domain`
Pure data + one policy object. No I/O, no framework imports.

- `models.py` — `Money`, `RawSupplierProduct`, `NormalizedProduct`, `Variant`,
  `ValidationIssue`, `ChecklistItem`, `SourceDocument`, `ReviewProduct`,
  `PipelineResult`. All Pydantic v2. `NormalizedProduct` groups fields by who
  fills them:
  supplier-derived (identity, price, variants, material, care), reviewer-set
  (`product_type`, `size_chart`, final `categories` / `properties`), and
  enrichment (initial `description` + suggestions). `ReviewProduct` carries the
  issues, the checklist, `fields_remaining` and `exportable` (all computed).
- `pricing.py` — `PricingPolicy`: `purchase → landed cost → suggested retail`,
  configurable and per-supplier-overridable. Numbers are illustrative.

### `app/services/extraction`
The first stage — and the production boundary that this repo replaces with a mock.

- `base.py` — `DocumentExtractionProvider` ABC
  (`extract(supplier_id, document, media_type) -> list[RawSupplierProduct]`),
  `UnsupportedMediaType`, `DocumentNotRecognized`.
- `documents.py` — the bundled fictional documents as `DemoDocument`s. Each
  carries its extraction result as `DemoLine`s; this is the single source of
  truth (the extractor returns it, `scripts/generate_demo_documents.py` renders
  it into the PDF / JPG).
- `mock.py` — `MockDocumentExtractor`: deterministic, offline. Accepts only
  PDF / image media types, only recognizes the bundled documents (an arbitrary
  PDF raises `DocumentNotRecognized` — the same failure mode as a real prompt
  returning nothing usable), and returns loosely-typed `RawSupplierProduct`s.

### `app/suppliers`
A second, developer-facing entry point: adapters for suppliers that ship a
machine-readable feed.

- `base.py` — `SupplierAdapter` ABC (`parse(bytes) -> list[RawSupplierProduct]`),
  `SupplierMeta`, `SupplierParseError`.
- `registry.py` — `SupplierRegistry`; adapters register themselves at import.
- `alpinewear.py` — JSON feed. Handles string prices with currency suffixes,
  a `status` filter, size maps vs. bare size lists, colour as object or string.
- `urbanthreads.py` — CSV, one row per size. **Groups** rows back into products
  by article + colour. Drops shipping pseudo-lines and quantity-0 rows; parses
  European decimal commas.
- `demoshoes.py` — HTML catalogue table via stdlib `html.parser`. Reads EANs
  from `data-ean` attributes, skips `class="sold-out"` size cells.

### `app/services`
Stateless transformations + the provider boundaries.

- `normalization.py` — `RawSupplierProduct → NormalizedProduct`. SKU derivation,
  display-name construction (colour appended once), per-size EAN attach, pricing
  fallback.
- `validation.py` — a list of small `Rule` functions checking data correctness
  only (empty name, missing price, duplicate size, implausible EAN, thin margin).
  Each issue has a stable `code`.
- `completeness.py` — `build_checklist()`: required items (basics, variants,
  category, description, care) block export; recommended items (images) don't.
- `pipeline.py` — `review()` = validate + build checklist. `ingest_document()`
  (extract → normalize → review, sets `PipelineResult.source_document`) and
  `ingest()` (adapter parse → normalize → review) are the two entry points.
- `enrichment.py` — `suggest()` returns an `EnrichmentResult` (description +
  taxonomy) from the LLM provider; `enrich()` merges it into the product
  **non-destructively** (description regenerated; categories unioned; the
  reviewer's property value wins per group).
- `llm/` — `LLMProvider` ABC + `MockLLMProvider` (deterministic templates;
  category matching scores name/leaf/path token overlap, honours product gender,
  and applies a small keyword→category hint map). `LLMQuotaError` → HTTP 402.
- `shop/` — `ShopClient` ABC + `MockShopAdapter`. The adapter keeps the
  interesting parts of the real Shopware client: a single **payload builder**
  (parent + variants + configurator settings + properties + prices +
  `productType` / `sizeChartId` / manufacturer) and **idempotent**
  `upsert_property_option`. `ShopProduct.payload` returns the full write so the
  UI can preview it. The invented category tree and property groups (Color, Fit,
  Sleeve length, Product style, Neckline) live here.
- `images.py` — `ImagePipeline` with a staged job model
  (`generating → removing_bg → done`) and an injectable `JobStore`
  (`InMemoryJobStore` here; production uses an on-disk store re-read on every
  call so jobs survive across worker processes).
- `storage.py` — `ObjectStorage` ABC + `LocalObjectStorage`.
- `auth.py` — signed-cookie session sample. **Not wired into the app.**

### `app/api`
Thin FastAPI routers. Handlers raise domain errors; `errors.py` maps them to
HTTP status codes in one place.

- `documents.py` — the primary flow: list the bundled documents, download one,
  `analyze` the bundled document, or `extract` an uploaded one (which must match
  the bundled bytes, else 422).
- `suppliers.py` — the developer flow: list adapters, fetch a bundled sample
  feed, parse an uploaded structured file.
- `catalog.py` — shop taxonomy, product types, size charts, size presets, and
  the size run for a product type (all read-only, for the UI).
- `products.py` — `suggest`, `enrich`, `review`, image jobs, `export`, fetch
  exported. The `export` 422 payload separates `errors` (bad data) from
  `incomplete` (checklist keys) so the UI can jump to the right section.

## Frontend

`src/components/ui.jsx` is a small design-system kit (buttons, fields, chips,
stepper, completion list, skeletons) built on a restrained token set in
`tailwind.config.js`. `src/lib/api.js` is the single API layer; every endpoint
has a wrapper, errors are normalized to `ApiError` (carrying the structured
`detail`), and JSDoc typedefs document the payload shapes.

`App.jsx` is a 4-state wizard (`Import → Review → Edit & Enrich → Export`) with a
persistent stepper in the header.

- `ImportPage` — three supplier-document cards; **Analyze sample document** runs
  the mock extractor behind an "Analyzing document with AI…" progress state (no
  upload). A "Production vs. this demo" note sits above the cards. The
  structured-file adapters are a *Developer tools* disclosure.
- `ReviewPage` — header shows *Extracted N products from `<filename>`* with an
  "AI extraction · mocked in demo" badge and a link to the document; per product,
  an **extracted (raw)** vs **normalized product** key/value comparison (full
  extractor output behind a toggle) and a completion badge.
- `components/editor/` — the product editor. `EditorWorkspace` holds one editable
  state object per product, tabbed navigation, and a **debounced call to
  `/review`** on every change; on a blocked export it scrolls to and highlights
  the first unfinished section. Sections (`GeneralSection`, `ImagesSection`,
  `VariantsSection`, `CategoriesSection`, `PropertiesSection`) are controlled
  components; `SummaryRail` is a sticky panel with the product summary, a
  completion checklist, and the export action + payload preview.
- `SuccessScreen` — exported products with per-product stats and payload views.

## Why the provider boundaries

Every external dependency (document extraction, LLM, images, storage, shop) is an
ABC with a mock. Consequences:

- the demo runs with no keys and no network,
- tests are fast and deterministic,
- swapping in a real provider is a new class + one registration line,
- no vendor SDK is imported outside its provider module,
- the demo can be *truthful*: `SourceDocument.is_mock` and the UI say plainly
  that extraction is mocked, while the boundary is the real one.
