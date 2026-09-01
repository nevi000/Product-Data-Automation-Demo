import { useEffect, useState } from 'react'
import { api, ApiError } from '../lib/api'
import { Button, Disclosure, Icon, Overlay, Panel, Select, Spinner } from './ui'

const ANALYZE_STEPS = ['Reading document', 'Running extraction model', 'Parsing structured output']

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms))
}

// "analyzing" modal shown while the mock extractor runs
function AnalyzingOverlay({ doc, step, count }) {
  const done = count != null
  return (
    <Overlay labelledBy="analyze-title">
      <div className="p-6">
        <div className="flex items-center gap-2 text-meta font-medium uppercase tracking-[0.12em] text-ink-faint">
          <Icon name="sparkle" className="h-3.5 w-3.5 text-primary" />
          Document extraction
        </div>
        <p id="analyze-title" className="mt-2 text-title font-semibold text-ink">
          {doc.supplier_name}
        </p>
        <p className="tabular font-mono text-meta text-ink-soft">{doc.filename}</p>

        <ul className="mt-6 space-y-1">
          {ANALYZE_STEPS.map((label, i) => {
            const state = done || i < step ? 'done' : i === step ? 'active' : 'todo'
            return (
              <li key={label} className="flex items-center gap-3 py-1.5 text-body">
                <span
                  className={`grid h-[18px] w-[18px] shrink-0 place-items-center rounded-full transition-colors duration-[var(--dur)] ${
                    state === 'done'
                      ? 'bg-primary text-white'
                      : state === 'active'
                        ? 'bg-primary/10 text-primary'
                        : 'border border-hairline-strong'
                  }`}
                >
                  {state === 'done' ? (
                    <Icon name="check" className="h-2.5 w-2.5" strokeWidth={3} />
                  ) : state === 'active' ? (
                    <Spinner className="h-3 w-3" />
                  ) : null}
                </span>
                <span className={state === 'todo' ? 'text-ink-faint' : 'text-ink'}>{label}</span>
              </li>
            )
          })}
        </ul>

        <div className="disclosure mt-4" data-open={done ? 'true' : 'false'}>
          <div>
            <div className="flex animate-fade-scale items-center gap-2.5 rounded-lg border border-positive-border bg-positive-subtle px-3.5 py-3">
              <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-positive text-white">
                <Icon name="check" className="h-3.5 w-3.5" strokeWidth={2.6} />
              </span>
              <div>
                <p className="text-body font-semibold text-positive">
                  {count} {count === 1 ? 'product' : 'products'} extracted
                </p>
                <p className="text-meta text-positive/80">Opening review…</p>
              </div>
            </div>
          </div>
        </div>

        <p className="mt-4 border-t border-hairline pt-3 text-meta text-ink-faint">
          Deterministic offline mock · no AI call, no network request.
        </p>
      </div>
    </Overlay>
  )
}

// small abstract preview that just hints at the file type
function DocPreview({ doc }) {
  const isPdf = doc.media_type === 'application/pdf'
  const rows = Array.from({ length: Math.min(4, Math.max(3, doc.product_count)) })
  const widths = ['84%', '66%', '78%', '54%']
  return (
    <div className="relative h-[104px] overflow-hidden border-b border-hairline bg-surface-inset">
      <div
        className={`absolute left-1/2 top-[15px] w-[64%] -translate-x-1/2 rounded-[3px] border border-hairline bg-surface p-2.5 ${
          isPdf
            ? 'shadow-[0_1px_2px_rgba(20,26,40,0.06)]'
            : 'rotate-[-1.7deg] shadow-[0_4px_12px_-3px_rgba(20,26,40,0.20)]'
        }`}
      >
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-[2px] bg-primary/70" />
          <span className="h-1.5 w-12 rounded-full bg-ink/25" />
        </div>
        <div className="mt-2 h-px w-full bg-hairline" />
        <div className="mt-2 space-y-[5px]">
          {rows.map((_, i) => (
            <div key={i} className="flex items-center justify-between gap-2">
              <span
                className="h-[3px] rounded-full bg-ink/12"
                style={{ width: widths[i] ?? '60%' }}
              />
              <span className="h-[3px] w-3 shrink-0 rounded-full bg-ink/20" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function DocumentCard({ doc, onAnalyze }) {
  const isPdf = doc.media_type === 'application/pdf'
  return (
    <Panel className="group flex flex-col overflow-hidden transition-[border-color,box-shadow] duration-[var(--dur)] hover:border-hairline-strong hover:shadow-raised">
      <DocPreview doc={doc} />

      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.08em] text-ink-faint">
          <span className="rounded-sm border border-hairline-strong px-1.5 py-0.5 text-[10px] text-ink-soft">
            {isPdf ? 'PDF' : 'Image'}
          </span>
          <span className="truncate">{doc.kind}</span>
        </div>

        <h3 className="mt-2.5 text-[16px] font-semibold tracking-[-0.01em] text-ink">
          {doc.supplier_name}
        </h3>
        <p className="mt-0.5 text-meta text-ink-soft">
          {doc.product_count} line item{doc.product_count === 1 ? '' : 's'}
        </p>

        <dl className="mt-3 space-y-1 text-[11.5px] text-ink-faint">
          <div className="flex items-center gap-1.5">
            <Icon name={isPdf ? 'document' : 'image'} className="h-3 w-3 shrink-0" />
            <span className="truncate font-mono" title={doc.filename}>
              {doc.filename}
            </span>
          </div>
          <div className="font-mono">Reference {doc.doc_number}</div>
        </dl>

        <div className="mt-auto flex items-center justify-between gap-3 border-t border-hairline pt-4">
          <Button size="md" className="shrink-0 whitespace-nowrap" onClick={onAnalyze}>
            Extract products
            <Icon name="arrowRight" className="h-3.5 w-3.5" />
          </Button>
          <a
            href={api.documentUrl(doc.supplier_id)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-[12.5px] font-medium text-ink-faint transition-colors duration-[var(--dur)] hover:text-ink"
          >
            Preview
            <Icon name="external" className="h-3 w-3" />
          </a>
        </div>
      </div>
    </Panel>
  )
}

function CardSkeleton() {
  return (
    <Panel className="overflow-hidden">
      <div className="h-[104px] border-b border-hairline bg-surface-inset" />
      <div className="p-5">
        <div className="skeleton h-3 w-24 rounded" />
        <div className="skeleton mt-3.5 h-4 w-2/3 rounded" />
        <div className="skeleton mt-2 h-3 w-1/3 rounded" />
        <div className="skeleton mt-3.5 h-2.5 w-4/5 rounded" />
        <div className="skeleton mt-2 h-2.5 w-1/2 rounded" />
        <div className="mt-5 border-t border-hairline pt-4">
          <div className="skeleton h-9 w-36 rounded-md" />
        </div>
      </div>
    </Panel>
  )
}

export default function ImportPage({ onIngested }) {
  const [docs, setDocs] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [error, setError] = useState(null)
  const [analyzing, setAnalyzing] = useState(null) // { ...doc, step, count }

  const [advOpen, setAdvOpen] = useState(false)
  const [advSupplier, setAdvSupplier] = useState('')
  const [advFile, setAdvFile] = useState(null)
  const [advBusy, setAdvBusy] = useState(false)

  useEffect(() => {
    let alive = true
    api
      .listDocuments()
      .then((d) => alive && setDocs(d))
      .catch((e) => alive && setError(e.message))
    api
      .listSuppliers()
      .then((s) => alive && setSuppliers(s))
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])

  async function analyze(doc) {
    setError(null)
    setAnalyzing({ ...doc, step: 0, count: null })
    const stepTimers = ANALYZE_STEPS.map((_, i) =>
      setTimeout(() => setAnalyzing((a) => a && { ...a, step: i + 1 }), 550 * (i + 1)),
    )
    try {
      const [result] = await Promise.all([api.analyzeDocument(doc.supplier_id), sleep(1750)])
      stepTimers.forEach(clearTimeout)
      setAnalyzing((a) => a && { ...a, step: ANALYZE_STEPS.length, count: result.count })
      await sleep(750)
      onIngested(result)
    } catch (e) {
      stepTimers.forEach(clearTimeout)
      setAnalyzing(null)
      setError(e instanceof ApiError ? e.message : String(e))
    }
  }

  async function runAdvanced() {
    if (!advSupplier || !advFile) return
    setAdvBusy(true)
    setError(null)
    try {
      onIngested(await api.ingest(advSupplier, advFile))
    } catch (e) {
      setError(e.message)
    } finally {
      setAdvBusy(false)
    }
  }

  return (
    <div>
      {analyzing && (
        <AnalyzingOverlay doc={analyzing} step={analyzing.step} count={analyzing.count} />
      )}

      <header>
        <h1 className="text-page font-semibold text-ink">Extract products from supplier documents</h1>
        <p className="mt-2.5 max-w-2xl text-bodylg text-ink-soft">
          Supplier PDFs and images are transformed into structured product data, normalized and
          prepared for review.
        </p>
      </header>

      <div className="mt-6 grid gap-x-8 gap-y-3 rounded-md border border-hairline bg-surface-inset px-4 py-3 text-meta sm:grid-cols-2">
        <div>
          <p className="font-semibold text-ink-soft">Production</p>
          <p className="mt-0.5 text-ink-faint">
            Supplier-specific LLM extraction turns PDFs and images into structured product data.
          </p>
        </div>
        <div>
          <p className="font-semibold text-ink-soft">Public demo</p>
          <p className="mt-0.5 text-ink-faint">
            Deterministic offline extraction on fictional documents — no API keys or network
            required.
          </p>
        </div>
      </div>

      {error && (
        <div className="mt-6 flex items-center gap-2 rounded-lg border border-critical-border bg-critical-subtle px-4 py-3 text-body text-critical">
          <Icon name="info" className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        {docs.length > 0
          ? docs.map((doc) => (
              <DocumentCard key={doc.supplier_id} doc={doc} onAnalyze={() => analyze(doc)} />
            ))
          : !error && [0, 1, 2].map((i) => <CardSkeleton key={i} />)}
      </div>

      <div className="mt-10 overflow-hidden rounded-md border border-hairline bg-surface-inset">
        <button
          type="button"
          onClick={() => setAdvOpen((v) => !v)}
          className="flex w-full items-center gap-2 px-3.5 py-2.5 text-left text-meta text-ink-faint transition-colors duration-[var(--dur)] hover:text-ink-soft"
        >
          <Icon
            name="chevronRight"
            className={`h-3.5 w-3.5 transition-transform duration-[var(--dur)] ${
              advOpen ? 'rotate-90' : ''
            }`}
          />
          Developer tools — structured-file adapters (JSON / CSV / HTML)
          <span className="ml-auto text-[11px] text-ink-faint/70">Optional</span>
        </button>
        <Disclosure open={advOpen}>
          <div className="space-y-3 border-t border-hairline bg-surface px-3.5 py-4">
            <p className="max-w-2xl text-meta leading-relaxed text-ink-soft">
              An alternative entry point for suppliers that ship a machine-readable feed. Unlike the
              document extractor, these adapters genuinely parse arbitrary input. The files in{' '}
              <code className="rounded bg-surface-inset px-1 py-0.5 font-mono text-[11.5px]">
                demo_data/
              </code>{' '}
              are valid examples.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Select
                className="max-w-[260px]"
                value={advSupplier}
                onChange={(e) => setAdvSupplier(e.target.value)}
              >
                <option value="">Choose adapter</option>
                {suppliers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} — {s.input_format.toUpperCase()}
                  </option>
                ))}
              </Select>
              <input
                type="file"
                onChange={(e) => setAdvFile(e.target.files?.[0] ?? null)}
                className="text-meta text-ink-soft file:mr-3 file:rounded-md file:border file:border-hairline file:bg-surface file:px-3 file:py-1.5 file:text-meta file:font-medium file:text-ink-soft hover:file:bg-surface-inset"
              />
              <Button
                variant="secondary"
                size="sm"
                disabled={!advSupplier || !advFile || advBusy}
                onClick={runAdvanced}
              >
                {advBusy && <Spinner className="h-3.5 w-3.5" />}
                Parse file
              </Button>
            </div>
          </div>
        </Disclosure>
      </div>
    </div>
  )
}
