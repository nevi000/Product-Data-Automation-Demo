import { useState } from 'react'
import { Button, CodeBlock, CompletionList, Disclosure, Icon, Spinner, money } from '../ui'

function Payload({ payload }) {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <Button variant="tertiary" size="sm" onClick={() => setOpen((o) => !o)}>
        <Icon
          name="chevronRight"
          className={`h-3.5 w-3.5 transition-transform duration-[var(--dur)] ${open ? 'rotate-90' : ''}`}
        />
        View generated payload
      </Button>
      <Disclosure open={open}>
        <CodeBlock className="mt-2">{JSON.stringify(payload, null, 2)}</CodeBlock>
      </Disclosure>
    </div>
  )
}

function MetricRow({ label, value }) {
  return (
    <div className="flex items-center justify-between py-[5px] text-[12.5px]">
      <span className="text-ink-faint">{label}</span>
      <span className="tabular font-medium text-ink">{value}</span>
    </div>
  )
}

export default function SummaryRail({
  product,
  review,
  exported,
  allExported,
  onExport,
  onJump,
  onNext,
  onFinish,
}) {
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)

  const dataErrors = review.issues.filter((i) => i.blocking)
  const canExport = dataErrors.length === 0

  const checklist = review.checklist || []
  const doneCount = checklist.filter((c) => c.done).length
  const pct = checklist.length ? Math.round((doneCount / checklist.length) * 100) : 0
  const variantCount = product.variants.length || 1

  async function doExport() {
    setBusy(true)
    setMessage(null)
    const res = await onExport()
    setBusy(false)
    if (!res.ok) setMessage(res.message || 'Complete the required fields before exporting.')
  }

  return (
    <aside className="scroll-slim lg:sticky lg:top-sticky lg:max-h-[calc(100vh-5.5rem)] lg:self-start lg:overflow-y-auto">
      <div className="overflow-hidden rounded-lg border border-hairline bg-surface shadow-raised">
        {/* name + sku */}
        <div className="px-5 pb-4 pt-5">
          <h3 className="text-[15px] font-semibold leading-snug tracking-[-0.01em] text-ink">
            {product.name}
          </h3>
          <p className="mt-1 text-meta text-ink-faint">
            {product.color && <span>{product.color} · </span>}
            <span className="font-mono text-[11.5px] text-ink-soft">{product.product_number}</span>
          </p>
        </div>

        {/* price + variant count */}
        <div className="grid grid-cols-2 divide-x divide-hairline border-y border-hairline">
          <div className="px-5 py-3">
            <p className="tabular text-[21px] font-semibold leading-none tracking-[-0.02em] text-ink">
              {money(product.retail_price)}
            </p>
            <p className="mt-1.5 text-[11px] uppercase tracking-[0.06em] text-ink-faint">Retail</p>
          </div>
          <div className="px-5 py-3">
            <p className="tabular text-[21px] font-semibold leading-none tracking-[-0.02em] text-ink">
              {variantCount}
            </p>
            <p className="mt-1.5 text-[11px] uppercase tracking-[0.06em] text-ink-faint">
              {variantCount === 1 ? 'Variant' : 'Variants'}
            </p>
          </div>
        </div>

        {/* the rest of the numbers */}
        <div className="px-5 py-2.5">
          <MetricRow label="Purchase price" value={money(product.purchase_price)} />
          <MetricRow label="Categories" value={product.categories.length} />
          <MetricRow label="Properties" value={Object.keys(product.properties || {}).length} />
          <MetricRow label="Images" value={product.image_urls.length} />
        </div>

        {!exported && (
          <>
            <div className="border-t border-hairline px-5 py-4">
              <div className="mb-2.5 flex items-baseline justify-between">
                <h4 className="text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-soft">
                  Completion
                </h4>
                <span className="tabular text-meta font-medium text-ink-soft">
                  {doneCount} / {checklist.length}
                </span>
              </div>
              <div className="mb-3.5 h-1 overflow-hidden rounded-full bg-hairline">
                <div
                  className="h-full rounded-full bg-primary transition-[width] duration-300 ease-swift"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <CompletionList items={checklist} onJump={onJump} />
            </div>

            {dataErrors.length > 0 && (
              <div className="mx-5 mb-1 rounded-md bg-critical-subtle px-3 py-2.5 text-meta text-critical">
                {dataErrors.map((e, i) => (
                  <p key={i} className="flex items-start gap-1.5">
                    <Icon name="info" className="mt-px h-3.5 w-3.5 shrink-0" />
                    {e.message}
                  </p>
                ))}
              </div>
            )}

            <div className="border-t border-hairline px-5 py-4">
              {review.exportable ? (
                <p className="mb-3 flex items-center gap-1.5 rounded-md bg-positive-subtle px-3 py-2 text-[12.5px] font-medium text-positive">
                  <Icon name="check" className="h-4 w-4" strokeWidth={2.4} />
                  Ready to export
                </p>
              ) : (
                <p className="mb-3 text-[12.5px] text-ink-soft">
                  <span className="tabular font-medium text-ink">{review.fields_remaining}</span> field
                  {review.fields_remaining === 1 ? '' : 's'} remaining
                </p>
              )}
              <Button
                variant="primary"
                size="lg"
                className="w-full"
                disabled={busy || !canExport}
                onClick={doExport}
              >
                {busy && <Spinner className="h-4 w-4" />}
                Export to demo shop
                {!busy && <Icon name="arrowRight" className="h-4 w-4" />}
              </Button>
              {message && <p className="mt-2 text-meta text-caution">{message}</p>}
              {!canExport && (
                <p className="mt-2 text-meta text-critical">Fix the data errors above first.</p>
              )}
            </div>
          </>
        )}

        {exported && (
          <div className="space-y-3 border-t border-hairline px-5 py-4">
            <p className="flex items-center gap-2 text-[13px] font-semibold text-positive">
              <span className="grid h-5 w-5 place-items-center rounded-full bg-positive text-white">
                <Icon name="check" className="h-3 w-3" strokeWidth={3} />
              </span>
              Exported to demo shop
            </p>
            <div className="rounded-md bg-surface-inset px-3 py-2.5 text-meta text-ink-soft">
              <p className="tabular">
                {exported.variant_count} variants · {exported.property_count} properties ·{' '}
                {exported.image_count} images
              </p>
              <p className="mt-1 break-all font-mono text-[11px] text-ink-faint">{exported.url}</p>
            </div>
            <Payload payload={exported.payload} />
            {allExported ? (
              <Button className="w-full" onClick={onFinish}>
                Finish
                <Icon name="arrowRight" className="h-4 w-4" />
              </Button>
            ) : (
              <Button variant="secondary" className="w-full" onClick={onNext}>
                Continue to next product
                <Icon name="arrowRight" className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}
