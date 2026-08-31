import { useEffect, useState } from 'react'
import { api } from '../../lib/api'
import { Button, Field, SectionCard, Select, TextInput } from '../ui'

export default function VariantsSection({ product, patch, catalog, disabled, highlighted }) {
  const [showSizes, setShowSizes] = useState(
    () => product.variants.length > 0 || !!product.product_type,
  )
  const [presetSizes, setPresetSizes] = useState([])
  const [fromSize, setFromSize] = useState('')
  const [toSize, setToSize] = useState('')

  useEffect(() => {
    if (!product.product_type) {
      setPresetSizes([])
      return
    }
    api
      .sizesForProductType(product.product_type)
      .then((r) => setPresetSizes(r.sizes))
      .catch(() => setPresetSizes([]))
  }, [product.product_type])

  function toggleHasSizes(next) {
    setShowSizes(next)
    if (next) patch({ ean: null })
    else patch({ variants: [], product_type: null })
  }

  function applyRange() {
    const i = presetSizes.indexOf(fromSize)
    const j = presetSizes.indexOf(toSize)
    if (i === -1 || j === -1 || i > j) return
    const eanBySize = Object.fromEntries(product.variants.map((v) => [v.size, v.ean]))
    patch({
      variants: presetSizes
        .slice(i, j + 1)
        .map((size) => ({ size, ean: eanBySize[size] ?? null, active: true })),
    })
  }

  function updateVariant(size, changes) {
    patch({ variants: product.variants.map((v) => (v.size === size ? { ...v, ...changes } : v)) })
  }

  const activeCount = product.variants.filter((v) => v.active).length

  return (
    <SectionCard
      id="sec-variants"
      icon="layers"
      title="Sizes & variants"
      description="Product type sets the size run; toggle the sizes that were actually ordered."
      highlighted={highlighted}
    >
      <div className="space-y-5">
        <label className="flex cursor-pointer items-center gap-2.5 text-[12.5px] text-ink-soft">
          <input
            type="checkbox"
            checked={showSizes}
            disabled={disabled}
            onChange={(e) => toggleHasSizes(e.target.checked)}
            className="h-4 w-4 rounded border-hairline-strong accent-primary"
          />
          This product is sold in multiple sizes
        </label>

        {!showSizes && (
          <Field label="Barcode (EAN)" htmlFor="f-ean" optional>
            <TextInput
              id="f-ean"
              className="tabular max-w-[18rem] font-mono text-[13px]"
              disabled={disabled}
              value={product.ean ?? ''}
              onChange={(e) => patch({ ean: e.target.value || null })}
              placeholder="e.g. 4012345678901"
            />
          </Field>
        )}

        {showSizes && (
          <>
            <div className="grid gap-5 sm:grid-cols-2">
              <Field label="Product type" htmlFor="f-ptype">
                <Select
                  id="f-ptype"
                  disabled={disabled}
                  value={product.product_type ?? ''}
                  onChange={(e) => patch({ product_type: e.target.value || null })}
                >
                  <option value="">Choose a product type</option>
                  {catalog.productTypes
                    .filter((t) => t.size_preset)
                    .map((t) => (
                      <option key={t.key} value={t.key}>
                        {t.label}
                      </option>
                    ))}
                </Select>
              </Field>

              {presetSizes.length > 0 && (
                <Field label="Size range" description="Replaces the size list; EANs are kept.">
                  <div className="flex items-center gap-2">
                    <Select
                      className="w-[5.5rem]"
                      disabled={disabled}
                      value={fromSize}
                      onChange={(e) => setFromSize(e.target.value)}
                    >
                      <option value="">From</option>
                      {presetSizes.map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </Select>
                    <span className="text-ink-faint">–</span>
                    <Select
                      className="w-[5.5rem]"
                      disabled={disabled}
                      value={toSize}
                      onChange={(e) => setToSize(e.target.value)}
                    >
                      <option value="">To</option>
                      {presetSizes.map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </Select>
                    <Button
                      variant="secondary"
                      size="md"
                      type="button"
                      disabled={disabled || !fromSize || !toSize}
                      onClick={applyRange}
                    >
                      Apply
                    </Button>
                  </div>
                </Field>
              )}
            </div>

            {product.variants.length > 0 ? (
              <div className="overflow-hidden rounded-md border border-hairline">
                <div className="grid grid-cols-[3rem_5.5rem_1fr] items-center gap-3 border-b border-hairline bg-surface-inset px-3 py-2 text-[10.5px] font-semibold uppercase tracking-[0.07em] text-ink-soft">
                  <span>Size</span>
                  <span>Status</span>
                  <span>Barcode (EAN)</span>
                </div>
                <div className="divide-y divide-hairline">
                  {product.variants.map((v) => (
                    <div
                      key={v.size}
                      className={`grid grid-cols-[3rem_5.5rem_1fr] items-center gap-3 px-3 py-2 transition-colors ${
                        v.active ? '' : 'opacity-55'
                      }`}
                    >
                      <span className="tabular text-[13px] font-medium text-ink">{v.size}</span>
                      <label className="flex cursor-pointer items-center gap-2 text-meta text-ink-soft">
                        <input
                          type="checkbox"
                          checked={v.active}
                          disabled={disabled}
                          onChange={(e) => updateVariant(v.size, { active: e.target.checked })}
                          className="h-3.5 w-3.5 rounded border-hairline-strong accent-primary"
                        />
                        {v.active ? 'Active' : 'Off'}
                      </label>
                      <input
                        className="tabular h-8 w-full max-w-[13rem] rounded-sm border border-hairline bg-surface px-2 font-mono text-[12px] text-ink outline-none transition-[border-color,box-shadow] duration-[var(--dur)] hover:border-hairline-strong focus:border-primary focus:shadow-[0_0_0_3px_theme(colors.primary.subtle)] disabled:bg-surface-inset disabled:text-ink-faint"
                        placeholder="—"
                        disabled={disabled || !v.active}
                        value={v.ean ?? ''}
                        onChange={(e) => updateVariant(v.size, { ean: e.target.value || null })}
                      />
                    </div>
                  ))}
                </div>
                <div className="border-t border-hairline bg-surface-inset px-3 py-1.5 text-[11px] text-ink-faint">
                  {activeCount} of {product.variants.length} variant
                  {product.variants.length === 1 ? '' : 's'} active
                </div>
              </div>
            ) : (
              <p className="text-[13px] text-ink-faint">
                {product.product_type
                  ? 'Choose a size range to build the variant list.'
                  : 'Pick a product type to see its size run.'}
              </p>
            )}
          </>
        )}
      </div>
    </SectionCard>
  )
}
