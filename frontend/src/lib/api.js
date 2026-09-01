// All backend calls go through here so components don't touch fetch directly
// and error handling is in one place.

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message)
    this.status = status
    this.detail = detail // structured body, e.g. the export error with the missing fields
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
  // main flow: supplier documents (PDF / image)
  listDocuments: () => request('/api/documents'),

  documentUrl: (supplierId) => `/api/documents/${supplierId}/file`,

  analyzeDocument: (supplierId) =>
    request(`/api/documents/${supplierId}/analyze`, { method: 'POST' }),

  extractDocument: (supplierId, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/api/documents/${supplierId}/extract`, { method: 'POST', body: form })
  },

  // developer flow: structured-file adapters (JSON / CSV / HTML)
  listSuppliers: () => request('/api/suppliers'),

  ingest: (supplierId, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/api/suppliers/${supplierId}/ingest`, { method: 'POST', body: form })
  },

  enrich: (product, keywords = '') => request('/api/products/enrich', json({ product, keywords })),

  suggest: (product, keywords = '') => request('/api/products/suggest', json({ product, keywords })),

  review: (product) => request('/api/products/review', json(product)),

  startImageJob: (file, kind) => {
    const form = new FormData()
    form.append('file', file)
    form.append('kind', kind)
    return request('/api/products/images', { method: 'POST', body: form })
  },
  pollImageJob: (jobId) => request(`/api/products/images/${jobId}`),

  exportProduct: (product) => request('/api/products/export', json(product)),

  categories: () => request('/api/catalog/categories'),
  properties: () => request('/api/catalog/properties'),
  productTypes: () => request('/api/catalog/product-types'),
  sizeCharts: () => request('/api/catalog/size-charts'),
  sizesForProductType: (t) => request(`/api/catalog/product-types/${t}/sizes`),

  // download a supplier's sample feed as a File, ready to ingest
  sampleFile: async (supplierId) => {
    const res = await fetch(`/api/suppliers/${supplierId}/sample`)
    if (!res.ok) throw new ApiError('No sample available', res.status)
    const text = await res.text()
    const ext = { alpinewear: 'json', urbanthreads: 'csv', demoshoes: 'html' }[supplierId] || 'txt'
    return new File([text], `${supplierId}-sample.${ext}`, { type: 'text/plain' })
  },
}

export { ApiError }
