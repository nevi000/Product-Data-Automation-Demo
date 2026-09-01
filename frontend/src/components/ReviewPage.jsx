import { useState } from 'react'
import { api } from '../lib/api'
import { Button, Disclosure, Icon, Panel, StatusBadge, money } from './ui'

function sizes(list) {
  return list && list.length ? list.join(', ') : '—'
}

function SourceVsNormalized({ raw, product }) {
  const [showJson, setShowJson] = useState(false)
  const rows = [
    {
      label: 'Reference',
      from: raw?.source_reference,
      to: product.product_number,
      mono: true,
    },
    { label: 'Name', from: raw?.model_name, to: product.name },
    {
      label: 'Colour',
      from: [raw?.color_name, raw?.color_code].filter(Boolean).join(' · '),
      to: product.color,
    },
    { label: 'Brand', from: raw?.manufacturer, to: product.manufacturer?.name },
    { label: 'Material', from: raw?.material, to: product.material },
    { label: 'Care', from: raw?.care_instructions, to: product.care_instructions },
    {
      label: 'Sizes',
      from: sizes(raw?.sizes),
      to: sizes(product.variants.map((v) => v.size)),
    },
    {
      label: 'Wholesale',
      from: money(raw?.purchase_price),
      to: money(product.purchase_price),
      mono: true,
    },
    {
      label: 'Retail',
      from: money(raw?.suggested_retail_price),
      to: money(product.retail_price),
      mono: true,
    },
  ]

  return (
    <div className="space-y-4">
      <div className="grid items-stretch gap-3 lg:grid-cols-[1fr_auto_1fr]">
        <div className="rounded-md border border-hairline-strong bg-surface-inset p-4">
          <p className="mb-2.5 text-[11px] font-semibold uppercase tracking-[0.09em] text-ink-faint">
            Extracted source
          </p>
          <dl className="divide-y divide-hairline/70">
            {rows.map((r) => (
              <div key={r.label} className="grid grid-cols-[6rem_1fr] gap-x-3 py-[7px] text-[13px]">
                <dt className="text-meta text-ink-faint">{r.label}</dt>
                <dd
                  className={`min-w-0 truncate text-ink-soft ${r.mono ? 'font-mono text-[12px]' : ''}`}
                >
                  {r.from || '—'}
                </dd>
              </div>
            ))}
          </dl>
        </div>

        {/* normalize() step between the two columns */}
        <div className="flex shrink-0 items-center justify-center gap-2 lg:flex-col lg:gap-0 lg:px-1">
          <span className="hidden w-px flex-1 bg-gradient-to-b from-transparent to-hairline-strong lg:block" />
          <span className="flex items-center gap-1.5 rounded-full border border-primary-border bg-surface px-2.5 py-1.5 lg:my-2.5">
            <Icon name="arrowRight" className="h-3.5 w-3.5 text-primary" strokeWidth={2.2} />
            <span className="font-mono text-[10px] font-medium text-primary">normalize()</span>
          </span>
          <span className="hidden w-px flex-1 bg-gradient-to-b from-hairline-strong to-transparent lg:block" />
        </div>

        <div className="rounded-md border border-primary-border/60 bg-surface p-4 ring-1 ring-primary/5">
          <p className="mb-2.5 text-[11px] font-semibold uppercase tracking-[0.09em] text-primary/70">
            Normalized product
          </p>
          <dl className="divide-y divide-hairline/70">
            {rows.map((r) => (
              <div key={r.label} className="grid grid-cols-[6rem_1fr] gap-x-3 py-[7px] text-[13px]">
                <dt className="text-meta text-ink-faint">{r.label}</dt>
                <dd
                  className={`min-w-0 truncate text-ink ${
                    r.mono ? 'font-mono text-[12px]' : 'font-medium'
                  }`}
                >
                  {r.to || '—'}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      <div>
        <Button variant="tertiary" size="sm" onClick={() => setShowJson((s) => !s)}>
          <Icon
            name="chevronRight"
            className={`h-3.5 w-3.5 transition-transform duration-[var(--dur)] ${
              showJson ? 'rotate-90' : ''
            }`}
          />
          View raw extractor output
        </Button>
        <Disclosure open={showJson}>
          <pre className="scroll-slim mt-2 max-h-56 overflow-auto rounded-lg border border-hairline bg-[#12151d] p-3.5 text-[11.5px] leading-relaxed text-[#d7dbe4]">
            {JSON.stringify(raw ?? {}, null, 2)}
          </pre>
        </Disclosure>
      </div>
    </div>
  )
}

function CompletionBadge({ rp }) {
  const dataError = rp.issues?.some((i) => i.blocking)
  if (dataError)
    return (
      <StatusBadge tone="critical" dot>
        Needs a fix
      </StatusBadge>
    )
  if (rp.exportable)
    return (
      <StatusBadge tone="positive" dot>
        Ready
      </StatusBadge>
    )
  return (
    <StatusBadge tone="neutral" dot>
      {rp.fields_remaining} field{rp.fields_remaining === 1 ? '' : 's'} left
    </StatusBadge>
  )
}

export default function ReviewPage({ result, onBack, onContinue }) {
  const [selected, setSelected] = useState(() => new Set(result.review_products.map((_, i) => i)))
  const [expanded, setExpanded] = useState(0)

  function toggle(i) {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  const doc = result.source_document

  return (
    <div className="space-y-7">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-page font-semibold text-ink">Review extracted products</h1>
          {doc ? (
            <div className="mt-3 flex flex-wrap items-center gap-2.5">
              <a
                href={api.documentUrl(result.supplier_id)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-full border border-hairline bg-surface py-1 pl-2 pr-3 text-meta text-ink-soft transition-colors hover:bg-surface-inset"
              >
                <Icon
                  name={doc.media_type === 'application/pdf' ? 'document' : 'image'}
                  className="h-3.5 w-3.5 text-ink-faint"
                />
                <span className="font-mono text-[12px] text-ink">{doc.filename}</span>
              </a>
              <StatusBadge tone={doc.is_mock ? 'neutral' : 'info'}>
                <Icon name="sparkle" className="h-3 w-3" />
                {doc.is_mock ? 'AI extraction · mocked in demo' : 'AI extraction'}
              </StatusBadge>
              <span className="text-meta text-ink-faint">{result.count} line items</span>
            </div>
          ) : (
            <p className="mt-2 max-w-2xl text-body text-ink-soft">
              {result.count} products parsed from {result.supplier_name} via the structured-file
              adapter. Expand a row to compare source and normalized data.
            </p>
          )}
        </div>
        <Button variant="tertiary" size="sm" onClick={onBack}>
          <Icon name="chevronRight" className="h-3.5 w-3.5 rotate-180" />
          Back
        </Button>
      </header>

      {doc?.note && (
        <div className="flex items-start gap-2.5 rounded-lg border border-hairline bg-surface-inset px-4 py-3 text-meta text-ink-soft">
          <Icon name="info" className="mt-px h-4 w-4 shrink-0 text-ink-faint" />
          <p>{doc.note}</p>
        </div>
      )}

      <Panel className="overflow-hidden">
        <ul className="divide-y divide-hairline">
          {result.review_products.map((rp, i) => (
            <li key={i} className={expanded === i ? 'bg-surface-inset/40' : ''}>
              <div className="flex items-center gap-3 px-4 py-3">
                <input
                  type="checkbox"
                  checked={selected.has(i)}
                  onChange={() => toggle(i)}
                  aria-label={`Select ${rp.product.name}`}
                  className="h-4 w-4 rounded border-hairline-strong accent-primary"
                />
                <button
                  type="button"
                  className="flex flex-1 items-center justify-between gap-3 text-left"
                  onClick={() => setExpanded(expanded === i ? null : i)}
                >
                  <span className="flex min-w-0 items-baseline gap-2.5">
                    <span className="truncate text-body font-medium text-ink">
                      {rp.product.name}
                    </span>
                    <span className="tabular shrink-0 font-mono text-meta text-ink-faint">
                      {rp.product.product_number}
                    </span>
                  </span>
                  <span className="flex shrink-0 items-center gap-3">
                    <CompletionBadge rp={rp} />
                    <Icon
                      name="chevronDown"
                      className={`h-4 w-4 text-ink-faint transition-transform duration-[var(--dur)] ${
                        expanded === i ? 'rotate-180' : ''
                      }`}
                    />
                  </span>
                </button>
              </div>
              <Disclosure open={expanded === i}>
                <div className="border-t border-hairline px-4 py-4">
                  <SourceVsNormalized raw={result.raw_products[i]} product={rp.product} />
                </div>
              </Disclosure>
            </li>
          ))}
        </ul>
      </Panel>

      <div className="flex items-center justify-between">
        <span className="text-body text-ink-soft">
          <span className="tabular font-medium text-ink">{selected.size}</span> of {result.count}{' '}
          selected
        </span>
        <Button
          size="lg"
          disabled={selected.size === 0}
          onClick={() => onContinue(result.review_products.filter((_, i) => selected.has(i)))}
        >
          Continue to editor
          <Icon name="arrowRight" className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
