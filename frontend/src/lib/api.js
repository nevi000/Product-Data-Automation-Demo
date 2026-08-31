/**
 * Single typed-ish API layer. Every backend call the app makes goes through here
 * so components never touch `fetch` directly and error handling is uniform.
 *
 * @typedef {Object} Money
 * @property {string} amount
 * @property {string} currency
 *
 * @typedef {Object} Variant
 * @property {string} size
 * @property {string|null} ean
 * @property {boolean} active
 *
 * @typedef {Object} ManufacturerRef
 * @property {string} name
 * @property {string|null} [external_id]
 *
 * @typedef {Object} NormalizedProduct
 * @property {string} supplier_id
 * @property {string} product_number
 * @property {string} name
 * @property {string|null} collection
 * @property {string|null} color
 * @property {ManufacturerRef|null} manufacturer
 * @property {string|null} material
 * @property {Variant[]} variants
 * @property {string|null} ean
 * @property {Money|null} purchase_price
 * @property {Money|null} retail_price
 * @property {string|null} product_type
 * @property {string|null} size_chart
 * @property {string|null} care_instructions
 * @property {string|null} description
 * @property {string[]} categories
 * @property {Object<string,string>} properties
 * @property {string[]} image_urls
 *
 * @typedef {Object} ValidationIssue
 * @property {string} field
 * @property {"error"|"warning"} severity
 * @property {string} message
 * @property {string} code
 * @property {boolean} blocking
 *
 * @typedef {Object} ChecklistItem
 * @property {string} key
 * @property {string} label
 * @property {boolean} done
 * @property {boolean} required
 *
 * @typedef {Object} ReviewProduct
 * @property {NormalizedProduct} product
 * @property {ValidationIssue[]} issues
 * @property {ChecklistItem[]} checklist
 * @property {number} fields_remaining
 * @property {boolean} exportable
 *
 * @typedef {Object} EnrichmentResult
 * @property {string} description
 * @property {string[]} categories
 * @property {Object<string,string>} properties
 *
 * @typedef {Object} SourceDocument
 * @property {string} filename
 * @property {string} media_type
 * @property {string} extractor
 * @property {boolean} is_mock
 * @property {string|null} note
 *
 * @typedef {Object} DemoDocument
 * @property {string} supplier_id
 * @property {string} supplier_name
 * @property {string} filename
 * @property {string} media_type
 * @property {string} kind
 * @property {string} doc_number
 * @property {string} doc_date
 * @property {number} product_count
 *
 * @typedef {Object} PipelineResult
 * @property {string} supplier_id
 * @property {string} supplier_name
 * @property {SourceDocument|null} source_document
 * @property {number} count
 * @property {any[]} raw_products
 * @property {ReviewProduct[]} review_products
 *
 * @typedef {Object} ShopProduct
 * @property {string} id
 * @property {string} product_number
 * @property {string} name
 * @property {number} variant_count
 * @property {string[]} category_paths
 * @property {number} property_count
 * @property {number} image_count
 * @property {string} url
 * @property {Object} payload
 */

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message)
    this.status = status
    this.detail = detail // structured payload for callers that need it (e.g. export)
  }
}

async function request(path, options = {}) {
  const res = await fetch(path, options)
  const isJson = res.headers.get('content-type')?.includes('application/json')
  const body = isJson ? await res.json() : null
  if (!res.ok) {
    const detail = body?.detail
    const message =
      typeof detail === 'string' ? detail : detail?.message || `Request failed (${res.status})`
    throw new ApiError(message, res.status, typeof detail === 'object' ? detail : null)
  }
  return body
}

const json = (body) => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

export const api = {
  // ── primary flow: supplier documents (PDF / image) ────────────────────
  /** @returns {Promise<DemoDocument[]>} */
  listDocuments: () => request('/api/documents'),

  /** URL to open / preview a bundled document. */
  documentUrl: (supplierId) => `/api/documents/${supplierId}/file`,

  /** @returns {Promise<PipelineResult>} — run extraction on the bundled document */
  analyzeDocument: (supplierId) =>
    request(`/api/documents/${supplierId}/analyze`, { method: 'POST' }),

  /** @returns {Promise<PipelineResult>} — run extraction on an uploaded document */
  extractDocument: (supplierId, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/api/documents/${supplierId}/extract`, { method: 'POST', body: form })
  },

  // ── developer flow: structured-file adapters (JSON / CSV / HTML) ───────
  /** @returns {Promise<Array<{id:string,name:string,input_format:string,description:string,sample_count:number}>>} */
  listSuppliers: () => request('/api/suppliers'),

  /** @returns {Promise<PipelineResult>} */
  ingest: (supplierId, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/api/suppliers/${supplierId}/ingest`, { method: 'POST', body: form })
  },

  /** @returns {Promise<NormalizedProduct>} */
  enrich: (product, keywords = '') => request('/api/products/enrich', json({ product, keywords })),

  /** @returns {Promise<EnrichmentResult>} */
  suggest: (product, keywords = '') => request('/api/products/suggest', json({ product, keywords })),

  /** @returns {Promise<ReviewProduct>} — validation + completion checklist */
  review: (product) => request('/api/products/review', json(product)),

  startImageJob: (file, kind) => {
    const form = new FormData()
    form.append('file', file)
    form.append('kind', kind)
    return request('/api/products/images', { method: 'POST', body: form })
  },
  pollImageJob: (jobId) => request(`/api/products/images/${jobId}`),

  /** @returns {Promise<ShopProduct>} */
  exportProduct: (product) => request('/api/products/export', json(product)),

  categories: () => request('/api/catalog/categories'),
  properties: () => request('/api/catalog/properties'),
  productTypes: () => request('/api/catalog/product-types'),
  sizeCharts: () => request('/api/catalog/size-charts'),
  sizesForProductType: (t) => request(`/api/catalog/product-types/${t}/sizes`),

  /** Fetch the bundled sample feed for a supplier as a File, ready to ingest. */
  sampleFile: async (supplierId) => {
    const res = await fetch(`/api/suppliers/${supplierId}/sample`)
    if (!res.ok) throw new ApiError('No sample available', res.status)
    const text = await res.text()
    const ext = { alpinewear: 'json', urbanthreads: 'csv', demoshoes: 'html' }[supplierId] || 'txt'
    return new File([text], `${supplierId}-sample.${ext}`, { type: 'text/plain' })
  },
}

export { ApiError }
