import { ChipToggle, Field, SectionCard, TextInput, Textarea } from '../ui'

export default function PropertiesSection({ product, patch, catalog, disabled, highlighted }) {
  const props = product.properties || {}

  function setGroup(group, value) {
    const next = { ...props }
    if (next[group] === value) delete next[group]
    else next[group] = value
    patch({ properties: next })
  }

  return (
    <SectionCard
      id="sec-properties"
      icon="tag"
      title="Properties & filters"
      description="Storefront filter values, material and care. One value per filter group."
      highlighted={highlighted}
    >
      <div className="space-y-7">
        <div className="grid gap-x-8 gap-y-6 sm:grid-cols-2">
          {Object.entries(catalog.properties).map(([group, options]) => (
            <div key={group}>
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.06em] text-ink-faint">
                {group}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {options.map((opt) => (
                  <ChipToggle
                    key={opt}
                    disabled={disabled}
                    selected={props[group] === opt}
                    onClick={() => setGroup(group, opt)}
                  >
                    {opt}
                  </ChipToggle>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="grid gap-5 border-t border-hairline pt-6 sm:grid-cols-2">
          <Field label="Material" htmlFor="f-material" optional>
            <Textarea
              id="f-material"
              rows={2}
              disabled={disabled}
              value={product.material ?? ''}
              onChange={(e) => patch({ material: e.target.value || null })}
              placeholder="e.g. 87% merino wool, 13% nylon"
            />
          </Field>
          <Field
            label="Care instructions"
            htmlFor="f-care"
            message={
              !product.care_instructions?.trim()
                ? 'Add washing / care instructions before export.'
                : undefined
            }
          >
            <TextInput
              id="f-care"
              disabled={disabled}
              value={product.care_instructions ?? ''}
              onChange={(e) => patch({ care_instructions: e.target.value || null })}
              placeholder="e.g. Machine wash cold, do not tumble dry"
            />
          </Field>
        </div>
      </div>
    </SectionCard>
  )
}
