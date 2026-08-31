import { useState } from 'react'
import {
  Button,
  Field,
  Icon,
  PriceInput,
  SectionCard,
  Select,
  Spinner,
  TextInput,
  Textarea,
} from '../ui'

export default function GeneralSection({
  product,
  patch,
  catalog,
  keywords,
  onKeywordsChange,
  onGenerateDescription,
  disabled,
  highlighted,
}) {
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)

  async function generate() {
    setGenerating(true)
    setError(null)
    try {
      await onGenerateDescription()
    } catch (e) {
      setError(e.message)
    } finally {
      setGenerating(false)
    }
  }

  const currency = product.retail_price?.currency || product.purchase_price?.currency || 'EUR'
  const priceOut = (v) => (v ? { amount: v, currency } : null)

  return (
    <SectionCard
      id="sec-general"
      icon="box"
      title="General information"
      highlighted={highlighted}
    >
      <div className="space-y-7">
        {/* primary identity + copy */}
        <div className="space-y-5">
          <Field label="Product name" htmlFor="f-name">
            <TextInput
              id="f-name"
              className="text-[15px] font-medium"
              disabled={disabled}
              value={product.name}
              onChange={(e) => patch({ name: e.target.value })}
            />
          </Field>

          <Field
            label="Description"
            htmlFor="f-desc"
            message={
              !product.description?.trim()
                ? 'Add a storefront description before export.'
                : undefined
            }
          >
            <Textarea
              id="f-desc"
              rows={5}
              disabled={disabled}
              value={product.description ?? ''}
              onChange={(e) => patch({ description: e.target.value })}
              placeholder="Describe the product for the storefront…"
            />
          </Field>

          <div>
            <p className="mb-2 flex items-center gap-1.5 text-[10.5px] font-semibold uppercase tracking-[0.07em] text-ink-faint">
              <Icon name="sparkle" className="h-3 w-3 text-primary" />
              AI-assisted
            </p>
            <div className="flex flex-wrap items-center gap-2">
              <TextInput
                aria-label="Keywords for the description generator"
                className="h-9 min-w-[12rem] flex-1"
                placeholder="Keywords (optional)"
                value={keywords}
                disabled={disabled}
                onChange={(e) => onKeywordsChange(e.target.value)}
              />
              <Button
                variant="secondary"
                size="md"
                type="button"
                onClick={generate}
                disabled={disabled || generating}
              >
                {generating && <Spinner className="h-3.5 w-3.5" />}
                Generate suggestions
              </Button>
            </div>
            {error && <p className="mt-1.5 text-meta text-critical">{error}</p>}
          </div>
        </div>

        {/* supporting identity */}
        <div className="grid gap-5 border-t border-hairline pt-6 sm:grid-cols-2">
          <Field label="SKU / article number" htmlFor="f-sku">
            <TextInput
              id="f-sku"
              className="font-mono text-[13px]"
              disabled={disabled}
              value={product.product_number}
              onChange={(e) => patch({ product_number: e.target.value })}
            />
          </Field>
          <Field label="Manufacturer / brand" htmlFor="f-brand">
            <TextInput
              id="f-brand"
              disabled={disabled}
              value={product.manufacturer?.name ?? ''}
              onChange={(e) =>
                patch({ manufacturer: e.target.value ? { name: e.target.value } : null })
              }
            />
          </Field>

          <Field label="Purchase price" htmlFor="f-purchase">
            <PriceInput
              id="f-purchase"
              disabled={disabled}
              currency={currency}
              value={product.purchase_price?.amount}
              onChange={(v) => patch({ purchase_price: priceOut(v) })}
            />
          </Field>
          <Field label="Retail price" htmlFor="f-retail">
            <PriceInput
              id="f-retail"
              disabled={disabled}
              currency={currency}
              value={product.retail_price?.amount}
              onChange={(v) => patch({ retail_price: priceOut(v) })}
            />
          </Field>

          <div className="sm:col-span-2">
            <Field label="Size chart" htmlFor="f-chart">
              <Select
                id="f-chart"
                disabled={disabled}
                value={product.size_chart ?? ''}
                onChange={(e) => patch({ size_chart: e.target.value || null })}
              >
                <option value="">No size chart</option>
                {catalog.sizeCharts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Select>
            </Field>
          </div>
        </div>
      </div>
    </SectionCard>
  )
}
