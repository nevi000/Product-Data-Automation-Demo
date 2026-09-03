import { useMemo, useState } from 'react'
import { api } from '../../lib/api'
import { Button, Icon, RemovableChip, SectionCard, StatusBadge } from '../ui'

function buildTree(paths) {
  const root = []
  for (const path of paths) {
    const parts = path.split(' / ')
    let level = root
    let acc = ''
    parts.forEach((part, i) => {
      acc = acc ? `${acc} / ${part}` : part
      let node = level.find((n) => n.name === part)
      if (!node) {
        node = { name: part, path: acc, children: [], leaf: i === parts.length - 1 }
        level.push(node)
      }
      level = node.children
    })
  }
  return root
}

function countSelected(node, selected) {
  if (node.leaf) return selected.includes(node.path) ? 1 : 0
  return node.children.reduce((s, c) => s + countSelected(c, selected), 0)
}

function Node({ node, selected, onToggle, disabled, depth }) {
  const [open, setOpen] = useState(depth < 1)
  const pad = { paddingLeft: `${12 + depth * 18}px` }

  if (node.leaf) {
    const checked = selected.includes(node.path)
    return (
      <label
        className="flex cursor-pointer items-center gap-2.5 rounded-md py-1.5 text-body transition-colors hover:bg-surface-inset"
        style={pad}
      >
        <input
          type="checkbox"
          checked={checked}
          disabled={disabled}
          onChange={() => onToggle(node.path)}
          className="h-4 w-4 rounded border-hairline-strong accent-primary"
        />
        <span className={checked ? 'font-medium text-ink' : 'text-ink-soft'}>{node.name}</span>
      </label>
    )
  }
  const n = countSelected(node, selected)
  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-1.5 rounded-md py-1.5 text-left text-body font-medium text-ink transition-colors hover:bg-surface-inset"
        style={pad}
      >
        <Icon
          name="chevronRight"
          className={`h-3.5 w-3.5 text-ink-faint transition-transform duration-[var(--dur)] ${
            open ? 'rotate-90' : ''
          }`}
        />
        {node.name}
        {n > 0 && <StatusBadge tone="info">{n}</StatusBadge>}
      </button>
      {open &&
        node.children.map((c) => (
          <Node key={c.path} node={c} selected={selected} onToggle={onToggle} disabled={disabled} depth={depth + 1} />
        ))}
    </div>
  )
}

export default function CategoriesSection({ product, patch, catalog, keywords, disabled, highlighted }) {
  const tree = useMemo(() => buildTree(catalog.categories), [catalog.categories])
  const selected = product.categories
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function toggle(path) {
    patch({
      categories: selected.includes(path) ? selected.filter((p) => p !== path) : [...selected, path],
    })
  }

  async function suggest() {
    setLoading(true)
    setError(null)
    try {
      const result = await api.suggest(product, keywords)
      setSuggestions(result.categories.filter((c) => !selected.includes(c)))
    } catch {
      setError('Could not generate suggestions.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <SectionCard
      id="sec-category"
      icon="folder"
      title="Categories"
      description="Where this product appears in the storefront."
      highlighted={highlighted}
      action={
        !disabled && (
          <Button variant="secondary" size="sm" type="button" disabled={loading} onClick={suggest}>
            <Icon name="sparkle" className="h-3.5 w-3.5 text-primary" />
            {loading ? 'Suggesting…' : 'Suggest categories'}
          </Button>
        )
      }
    >
      <div className="space-y-5">
        {error && <p className="text-meta text-critical">{error}</p>}
        <div>
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.06em] text-ink-faint">
            Selected
          </p>
          {selected.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {selected.map((path) => (
                <RemovableChip key={path} disabled={disabled} onRemove={() => toggle(path)}>
                  <span title={path}>{path.split(' / ').slice(-2).join(' / ')}</span>
                </RemovableChip>
              ))}
            </div>
          ) : (
            <p className="text-meta text-ink-faint">No category selected yet.</p>
          )}
        </div>

        {suggestions.length > 0 && (
          <div className="animate-slide-down rounded-md bg-primary-subtle px-3 py-2.5">
            <p className="mb-2 flex items-center gap-1.5 text-meta font-semibold text-primary">
              <Icon name="sparkle" className="h-3.5 w-3.5" />
              Suggested — click to add
            </p>
            <div className="flex flex-wrap gap-1.5">
              {suggestions.map((path) => (
                <button
                  key={path}
                  type="button"
                  onClick={() => {
                    toggle(path)
                    setSuggestions((s) => s.filter((p) => p !== path))
                  }}
                  className="inline-flex items-center gap-1 rounded-full border border-primary-border bg-surface px-2.5 py-1 text-meta text-primary transition-colors hover:bg-primary/10"
                >
                  <Icon name="plus" className="h-3 w-3" strokeWidth={2.2} />
                  {path}
                </button>
              ))}
            </div>
          </div>
        )}

        <div>
          <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-ink-faint">
            Browse categories
          </p>
          <div className="scroll-slim -mx-1.5 max-h-72 overflow-auto px-1.5">
            {tree.map((node) => (
              <Node
                key={node.path}
                node={node}
                selected={selected}
                onToggle={toggle}
                disabled={disabled}
                depth={0}
              />
            ))}
          </div>
        </div>
      </div>
    </SectionCard>
  )
}
