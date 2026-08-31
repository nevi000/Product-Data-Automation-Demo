import { useState } from 'react'
import { Button, CodeBlock, Disclosure, Icon, Panel, Stat } from './ui'

function ResultCard({ p }) {
  const [open, setOpen] = useState(false)
  return (
    <Panel className="p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="truncate text-body font-semibold text-ink">{p.name}</p>
          <p className="tabular mt-0.5 font-mono text-meta text-ink-faint">{p.product_number}</p>
        </div>
        <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-positive-subtle px-2 py-[3px] text-[11px] font-medium text-positive">
          <Icon name="check" className="h-3 w-3" strokeWidth={2.6} />
          Exported
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-x-8 border-t border-hairline pt-2">
        <Stat label="Variants" icon="layers" value={p.variant_count} />
        <Stat label="Categories" icon="folder" value={p.category_paths.length} />
        <Stat label="Properties" icon="tag" value={p.property_count} />
        <Stat label="Images" icon="image" value={p.image_count} />
      </div>

      <div className="mt-3">
        <Button variant="tertiary" size="sm" onClick={() => setOpen((s) => !s)}>
          <Icon
            name="chevronRight"
            className={`h-3.5 w-3.5 transition-transform duration-[var(--dur)] ${open ? 'rotate-90' : ''}`}
          />
          View generated payload
        </Button>
        <Disclosure open={open}>
          <CodeBlock className="mt-2">{JSON.stringify(p.payload, null, 2)}</CodeBlock>
        </Disclosure>
      </div>
    </Panel>
  )
}

export default function SuccessScreen({ products, onRestart }) {
  const variants = products.reduce((s, p) => s + p.variant_count, 0)
  const images = products.reduce((s, p) => s + p.image_count, 0)

  return (
    <div className="space-y-8">
      <header>
        <div className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 animate-fade-scale place-items-center rounded-full bg-positive/12 text-positive">
            <Icon name="check" className="h-4 w-4" strokeWidth={2.6} />
          </span>
          <h1 className="text-page font-semibold text-ink">Export complete</h1>
        </div>
        <p className="mt-2 max-w-lg text-body text-ink-soft">
          The demo shop client built and accepted each payload — entirely offline.
        </p>

        <dl className="mt-5 flex divide-x divide-hairline overflow-hidden rounded-lg border border-hairline">
          {[
            ['Products', products.length],
            ['Variants', variants],
            ['Images', images],
          ].map(([label, value]) => (
            <div key={label} className="flex-1 px-5 py-3">
              <dd className="tabular text-[22px] font-semibold tracking-[-0.02em] text-ink">
                {value}
              </dd>
              <dt className="mt-0.5 text-[11px] uppercase tracking-[0.06em] text-ink-faint">
                {label}
              </dt>
            </div>
          ))}
        </dl>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        {products.map((p) => (
          <ResultCard key={p.id} p={p} />
        ))}
      </div>

      <div className="flex justify-center border-t border-hairline pt-6">
        <Button size="lg" onClick={onRestart}>
          <Icon name="plus" className="h-4 w-4" />
          Onboard more products
        </Button>
      </div>
    </div>
  )
}
