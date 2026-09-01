import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../../lib/api'
import { Button, Icon, Spinner } from '../ui'
import GeneralSection from './GeneralSection'
import ImagesSection from './ImagesSection'
import VariantsSection from './VariantsSection'
import CategoriesSection from './CategoriesSection'
import PropertiesSection from './PropertiesSection'
import SummaryRail from './SummaryRail'

// checklist key -> editor section id
const KEY_TO_SECTION = {
  basics: 'sec-general',
  description: 'sec-general',
  variants: 'sec-variants',
  category: 'sec-category',
  care: 'sec-properties',
  images: 'sec-images',
}

function makeForm(reviewProduct) {
  return {
    product: reviewProduct.product,
    review: {
      issues: reviewProduct.issues || [],
      checklist: reviewProduct.checklist || [],
      fields_remaining: reviewProduct.fields_remaining ?? 0,
      exportable: reviewProduct.exportable ?? false,
    },
    keywords: '',
    jobs: [],
    exported: null,
  }
}

function tabStatus(form) {
  if (form.exported) return { tone: 'positive', text: 'Exported' }
  if (form.review.issues.some((i) => i.blocking))
    return { tone: 'critical', text: 'Needs a fix' }
  if (form.review.exportable) return { tone: 'positive', text: 'Ready' }
  const n = form.review.fields_remaining
  return { tone: 'neutral', text: `${n} field${n === 1 ? '' : 's'} remaining` }
}

const DOT = {
  positive: 'bg-positive',
  critical: 'bg-critical',
  neutral: 'bg-ink-faint/50',
}

export default function EditorWorkspace({ items, supplierName, onBack, onDone }) {
  const [catalog, setCatalog] = useState(null)
  const [catalogError, setCatalogError] = useState(null)
  const [forms, setForms] = useState(() => items.map(makeForm))
  const [activeIdx, setActiveIdx] = useState(0)
  const [highlightKey, setHighlightKey] = useState(null)

  useEffect(() => {
    Promise.all([api.categories(), api.properties(), api.productTypes(), api.sizeCharts()])
      .then(([categories, properties, productTypes, sizeCharts]) =>
        setCatalog({ categories, properties, productTypes, sizeCharts }),
      )
      .catch((e) => setCatalogError(e.message))
  }, [])

  const active = forms[activeIdx]
  const reviewTimers = useRef({})

  const setForm = useCallback((idx, updater) => {
    setForms((prev) => {
      const next = [...prev]
      next[idx] = typeof updater === 'function' ? updater(next[idx]) : { ...next[idx], ...updater }
      return next
    })
  }, [])

  const runReview = useCallback(
    async (idx, product) => {
      try {
        const r = await api.review(product)
        setForm(idx, (f) =>
          f.product === product
            ? {
                ...f,
                review: {
                  issues: r.issues,
                  checklist: r.checklist,
                  fields_remaining: r.fields_remaining,
                  exportable: r.exportable,
                },
              }
            : f,
        )
      } catch {
        // keep the last review if this one fails
      }
    },
    [setForm],
  )

  const patchProduct = useCallback(
    (partial) => {
      const idx = activeIdx
      setForms((prev) => {
        const next = [...prev]
        const product = { ...next[idx].product, ...partial }
        next[idx] = { ...next[idx], product }
        clearTimeout(reviewTimers.current[idx])
        reviewTimers.current[idx] = setTimeout(() => runReview(idx, product), 400)
        return next
      })
    },
    [activeIdx, runReview],
  )

  useEffect(() => () => Object.values(reviewTimers.current).forEach(clearTimeout), [])

  const setJobs = useCallback(
    (updater) =>
      setForm(activeIdx, (f) => ({
        ...f,
        jobs: typeof updater === 'function' ? updater(f.jobs) : updater,
      })),
    [activeIdx, setForm],
  )

  function jumpTo(key) {
    const el = document.getElementById(KEY_TO_SECTION[key] || '')
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setHighlightKey(key)
    window.setTimeout(() => setHighlightKey(null), 1800)
  }

  async function generateDescription() {
    const enriched = await api.enrich(active.product, active.keywords)
    setForm(activeIdx, (f) => ({ ...f, product: enriched }))
    runReview(activeIdx, enriched)
  }

  async function exportProduct() {
    try {
      const shopProduct = await api.exportProduct(active.product)
      setForm(activeIdx, (f) => ({ ...f, exported: shopProduct }))
      return { ok: true }
    } catch (e) {
      const incomplete = e?.detail?.incomplete
      if (Array.isArray(incomplete) && incomplete.length) jumpTo(incomplete[0])
      return { ok: false, message: e.message }
    }
  }

  function goToNext() {
    const next = forms.findIndex((f, i) => i !== activeIdx && !f.exported)
    if (next !== -1) setActiveIdx(next)
  }

  const allExported = useMemo(() => forms.every((f) => f.exported), [forms])
  const exportedCount = forms.filter((f) => f.exported).length

  if (catalogError) return <p className="text-body text-critical">Failed to load catalogue: {catalogError}</p>
  if (!catalog)
    return (
      <p className="flex items-center gap-2 text-body text-ink-soft">
        <Spinner /> Loading catalogue…
      </p>
    )

  const highlightSection = highlightKey ? KEY_TO_SECTION[highlightKey] : null

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-page font-semibold text-ink">Edit &amp; enrich</h1>
          <p className="mt-1.5 text-body text-ink-soft">
            <span className="tabular font-medium text-ink">{forms.length}</span> product
            {forms.length === 1 ? '' : 's'} from {supplierName} ·{' '}
            <span className="tabular">{exportedCount}</span> exported
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="tertiary" size="sm" onClick={onBack}>
            <Icon name="chevronRight" className="h-3.5 w-3.5 rotate-180" />
            Back
          </Button>
          {allExported && (
            <Button size="sm" onClick={() => onDone(forms.map((f) => f.exported))}>
              Finish
              <Icon name="arrowRight" className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
      </div>

      {/* product tabs */}
      <div className="scroll-slim -mx-1 flex overflow-x-auto px-1 pb-1">
        <div className="flex rounded-lg border border-hairline bg-surface">
          {forms.map((f, i) => {
            const st = tabStatus(f)
            const activeTab = i === activeIdx
            return (
              <button
                key={i}
                type="button"
                onClick={() => setActiveIdx(i)}
                className={`relative flex w-[210px] shrink-0 flex-col gap-1.5 overflow-hidden border-r border-hairline px-4 py-3 text-left transition-colors duration-[var(--dur)] first:rounded-l-lg last:rounded-r-lg last:border-r-0 ${
                  activeTab ? 'bg-primary-subtle/60' : 'hover:bg-surface-inset'
                }`}
              >
                {activeTab && (
                  <span className="absolute inset-x-0 top-0 h-[2px] bg-primary" aria-hidden="true" />
                )}
                <span
                  className={`tabular text-[10.5px] font-semibold ${
                    activeTab ? 'text-primary' : 'text-ink-faint'
                  }`}
                >
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span
                  className={`line-clamp-2 text-[13px] leading-snug ${
                    activeTab ? 'font-semibold text-ink' : 'font-medium text-ink-soft'
                  }`}
                >
                  {f.product.name}
                </span>
                <span className="mt-auto space-y-0.5 pt-1">
                  <span className="block truncate text-[11px] text-ink-faint">
                    {f.product.color || '—'}
                  </span>
                  <span
                    className={`flex items-center gap-1 text-[11px] ${
                      st.tone === 'positive'
                        ? 'text-positive'
                        : st.tone === 'critical'
                          ? 'text-critical'
                          : 'text-ink-faint'
                    }`}
                  >
                    {st.tone === 'positive' ? (
                      <Icon name="check" className="h-3 w-3" strokeWidth={2.6} />
                    ) : (
                      <span className={`h-1.5 w-1.5 rounded-full ${DOT[st.tone]}`} />
                    )}
                    {st.text}
                  </span>
                </span>
              </button>
            )
          })}
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="divide-y divide-hairline overflow-hidden rounded-lg border border-hairline bg-surface">
          <GeneralSection
            product={active.product}
            patch={patchProduct}
            catalog={catalog}
            keywords={active.keywords}
            onKeywordsChange={(v) => setForm(activeIdx, { keywords: v })}
            onGenerateDescription={generateDescription}
            disabled={!!active.exported}
            highlighted={highlightSection === 'sec-general'}
          />
          <ImagesSection
            key={activeIdx}
            jobs={active.jobs}
            setJobs={setJobs}
            imageUrls={active.product.image_urls}
            onImagesChange={(image_urls) => patchProduct({ image_urls })}
            disabled={!!active.exported}
            highlighted={highlightSection === 'sec-images'}
          />
          <VariantsSection
            product={active.product}
            patch={patchProduct}
            catalog={catalog}
            disabled={!!active.exported}
            highlighted={highlightSection === 'sec-variants'}
          />
          <CategoriesSection
            product={active.product}
            patch={patchProduct}
            catalog={catalog}
            keywords={active.keywords}
            disabled={!!active.exported}
            highlighted={highlightSection === 'sec-category'}
          />
          <PropertiesSection
            product={active.product}
            patch={patchProduct}
            catalog={catalog}
            disabled={!!active.exported}
            highlighted={highlightSection === 'sec-properties'}
          />
        </div>

        <SummaryRail
          product={active.product}
          review={active.review}
          exported={active.exported}
          allExported={allExported}
          onExport={exportProduct}
          onJump={jumpTo}
          onNext={goToNext}
          onFinish={() => onDone(forms.map((f) => f.exported))}
        />
      </div>
    </div>
  )
}
