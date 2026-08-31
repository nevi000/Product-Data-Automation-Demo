/**
 * UI kit — "precise operations console".
 * Warm paper canvas, near-black ink, one deep ink-blue accent. Structure comes
 * from a 3-tier surface system + spacing rhythm, not colour.
 */

/* =========================================================== icons ======= */

const PATHS = {
  document:
    'M6 2.75h7.5L18 7.25v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3.75a1 1 0 0 1 1-1Z M13 3v4.5h4.5 M8 12h7 M8 15.5h7 M8 8.5h2',
  image:
    'M4 4.75h16v13.5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4.75Z M4 15l4-3.5 4 3 3-2.5 5 4.25 M8.5 9.25a1.25 1.25 0 1 1 0-2.5 1.25 1.25 0 0 1 0 2.5Z',
  sparkle:
    'M12 3.5l1.6 4.2 4.4 1.6-4.4 1.6L12 15l-1.6-4.1L6 9.3l4.4-1.6L12 3.5Z M18.5 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2Z',
  folder:
    'M4 6.75A1.75 1.75 0 0 1 5.75 5h3.4a1 1 0 0 1 .8.4l.9 1.2a1 1 0 0 0 .8.4h6.8A1.75 1.75 0 0 1 21 8.75v8.5A1.75 1.75 0 0 1 19.25 19H5.75A1.75 1.75 0 0 1 4 17.25V6.75Z',
  layers:
    'M12 3.5 21 8l-9 4.5L3 8l9-4.5Z M3 12l9 4.5L21 12 M3 16l9 4.5L21 16',
  tag:
    'M4 11.5V5.5a1.5 1.5 0 0 1 1.5-1.5h6L20 12.5a1.5 1.5 0 0 1 0 2.1l-5.4 5.4a1.5 1.5 0 0 1-2.1 0L4 11.5Z M8 8.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z',
  box:
    'M12 3.25 20 7v10l-8 3.75L4 17V7l8-3.75Z M4 7l8 3.75L20 7 M12 10.75V20.5',
  check: 'M4.5 12.5l5 5 10-11',
  x: 'M6 6l12 12M18 6L6 18',
  plus: 'M12 5v14M5 12h14',
  chevronRight: 'M9 6l6 6-6 6',
  chevronDown: 'M6 9l6 6 6-6',
  arrowRight: 'M5 12h14M13 6l6 6-6 6',
  arrowDown: 'M12 5v14M6 13l6 6 6-6',
  info: 'M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18Z M12 11v5 M12 8h.01',
  external: 'M14 5h5v5 M19 5l-8 8 M18 13.5V19a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h5.5',
}

export function Icon({ name, className = 'h-4 w-4', strokeWidth = 1.75 }) {
  const d = PATHS[name]
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {d.split(' M').map((seg, i) => (
        <path key={i} d={i === 0 ? seg : `M${seg}`} />
      ))}
    </svg>
  )
}

/* ========================================================= surfaces ====== */

export function Panel({ className = '', elevated = false, ...props }) {
  return (
    <div
      className={`rounded-lg border border-hairline bg-surface ${
        elevated ? 'shadow-raised' : ''
      } ${className}`}
      {...props}
    />
  )
}

/**
 * A flat section meant to sit inside one shared workspace surface — separated
 * from its siblings by a divider, not its own card border. Title is a compact
 * tracked label with a rule under the header.
 */
export function SectionCard({ id, icon, title, description, action, highlighted = false, children }) {
  return (
    <section
      id={id}
      className={`scroll-mt-sticky px-6 py-7 transition-colors duration-[var(--dur)] sm:px-8 ${
        highlighted ? 'bg-primary-subtle/50' : ''
      }`}
    >
      <header className="mb-5 border-b border-hairline pb-3">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
          <h2 className="flex items-center gap-2 text-[12px] font-semibold uppercase tracking-[0.08em] text-ink-soft">
            {icon && <Icon name={icon} className="h-3.5 w-3.5 text-ink-faint" />}
            {title}
          </h2>
          {action && <div className="flex flex-wrap items-center gap-2">{action}</div>}
        </div>
        {description && <p className="mt-2 text-meta text-ink-faint">{description}</p>}
      </header>
      {children}
    </section>
  )
}

/* ========================================================== buttons ===== */

const BTN_BASE =
  'inline-flex select-none items-center justify-center gap-1.5 rounded-md font-medium transition-[background-color,box-shadow,transform,border-color] duration-[var(--dur)] disabled:cursor-not-allowed active:translate-y-px focus-visible:outline-none'
const BTN_VARIANT = {
  primary:
    'bg-primary text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_1px_2px_rgba(20,26,40,0.12)] hover:bg-primary-hover active:bg-primary-press disabled:opacity-40 disabled:shadow-none',
  secondary:
    'border border-hairline bg-surface text-ink hover:border-hairline-strong hover:bg-surface-inset disabled:opacity-50',
  tertiary: 'text-ink-soft hover:bg-surface-inset hover:text-ink disabled:opacity-40',
  positive:
    'bg-positive text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_1px_2px_rgba(20,26,40,0.12)] hover:brightness-95 disabled:opacity-50',
  danger:
    'border border-hairline bg-surface text-critical hover:border-critical-border hover:bg-critical-subtle disabled:opacity-40',
}
const BTN_SIZE = {
  sm: 'h-8 px-2.5 text-[12px]',
  md: 'h-9 px-3.5 text-[13px]',
  lg: 'h-10 px-4 text-[13px]',
}

export function Button({ variant = 'primary', size = 'md', className = '', ...props }) {
  return (
    <button
      className={`${BTN_BASE} ${BTN_VARIANT[variant]} ${BTN_SIZE[size]} ${className}`}
      {...props}
    />
  )
}

export function IconButton({ label, className = '', children, ...props }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`inline-grid h-7 w-7 place-items-center rounded-md text-ink-soft transition-colors duration-[var(--dur)] hover:bg-surface-inset hover:text-ink ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

/* =========================================================== fields ===== */

export function Field({
  label,
  htmlFor,
  description,
  message,
  tone = 'muted',
  hint,
  optional = false,
  children,
}) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <div className="flex items-baseline justify-between gap-2">
          <label htmlFor={htmlFor} className="text-label font-semibold text-ink">
            {label}
          </label>
          {(hint || optional) && (
            <span className="text-meta font-normal text-ink-faint">{hint || 'Optional'}</span>
          )}
        </div>
      )}
      {description && <p className="-mt-0.5 text-meta leading-snug text-ink-faint">{description}</p>}
      {children}
      {message && (
        <p
          className={`flex items-center gap-1.5 text-meta ${
            tone === 'critical' ? 'text-critical' : 'text-ink-faint'
          }`}
        >
          <Icon name="info" className="h-3.5 w-3.5" />
          {message}
        </p>
      )}
    </div>
  )
}

const CONTROL =
  'w-full rounded-md border border-hairline bg-surface px-3 text-input text-ink outline-none transition-[border-color,box-shadow] duration-[var(--dur)] placeholder:text-ink-faint hover:border-hairline-strong focus:border-primary focus:shadow-[0_0_0_3px_theme(colors.primary.subtle)] disabled:cursor-not-allowed disabled:bg-surface-inset disabled:text-ink-faint'

export function TextInput({ className = '', ...props }) {
  return <input className={`${CONTROL} h-10 ${className}`} {...props} />
}

export function Textarea({ className = '', rows = 3, ...props }) {
  return (
    <textarea
      rows={rows}
      className={`${CONTROL} resize-y py-2.5 leading-relaxed ${className}`}
      {...props}
    />
  )
}

export function Select({ className = '', children, ...props }) {
  return (
    <div className={`relative ${className}`}>
      <select
        className={`${CONTROL} h-10 w-full cursor-pointer appearance-none pr-9`}
        {...props}
      >
        {children}
      </select>
      <Icon
        name="chevronDown"
        className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint"
      />
    </div>
  )
}

export function PriceInput({ value, onChange, currency = 'EUR', disabled, id }) {
  const sym = { EUR: '€', USD: '$', CHF: 'CHF' }[currency] || currency
  return (
    <div
      className={`flex h-10 w-full items-center gap-1.5 rounded-md border border-hairline bg-surface px-3 transition-[border-color,box-shadow] duration-[var(--dur)] focus-within:border-primary focus-within:shadow-[0_0_0_3px_theme(colors.primary.subtle)] hover:border-hairline-strong ${
        disabled ? 'bg-surface-inset' : ''
      }`}
    >
      <span className="shrink-0 text-input font-medium text-ink-faint">{sym}</span>
      <input
        id={id}
        type="number"
        inputMode="decimal"
        step="0.01"
        min="0"
        disabled={disabled}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder="0.00"
        className="tabular w-full bg-transparent text-input text-ink outline-none placeholder:text-ink-faint disabled:cursor-not-allowed disabled:text-ink-faint"
      />
    </div>
  )
}

/* ============================================================ chips ===== */

export function ChipToggle({ selected, disabled, onClick, children }) {
  return (
    <button
      type="button"
      disabled={disabled}
      aria-pressed={selected}
      onClick={onClick}
      className={`inline-flex h-8 items-center gap-1.5 rounded-full border px-3 text-[12px] transition-[background-color,border-color,color] duration-[var(--dur)] disabled:cursor-not-allowed ${
        selected
          ? 'border-primary-border bg-primary-subtle font-medium text-primary'
          : 'border-hairline bg-surface text-ink-soft hover:border-hairline-strong hover:text-ink'
      }`}
    >
      {selected && <Icon name="check" className="h-3 w-3" strokeWidth={2.4} />}
      {children}
    </button>
  )
}

export function RemovableChip({ children, onRemove, disabled }) {
  return (
    <span className="inline-flex h-7 items-center gap-1.5 rounded-full border border-primary-border bg-primary-subtle pl-2.5 pr-1.5 text-[12px] text-primary">
      {children}
      {!disabled && (
        <button
          type="button"
          onClick={onRemove}
          aria-label="Remove"
          className="grid h-4 w-4 place-items-center rounded-full text-primary/70 transition-colors hover:bg-primary/15 hover:text-primary"
        >
          <Icon name="x" className="h-3 w-3" strokeWidth={2.2} />
        </button>
      )}
    </span>
  )
}

/* ============================================================ stats ===== */

export function Stat({ label, value, icon }) {
  return (
    <div className="flex items-center justify-between gap-3 py-[7px] text-[13px]">
      <span className="flex items-center gap-2 text-ink-faint">
        {icon && <Icon name={icon} className="h-3.5 w-3.5" />}
        {label}
      </span>
      <span className="tabular text-right font-medium text-ink">{value}</span>
    </div>
  )
}

/* ========================================================= statuses ===== */

const BADGE_TONE = {
  neutral: 'border border-hairline bg-surface-inset text-ink-soft',
  info: 'bg-primary-subtle text-primary',
  positive: 'bg-positive-subtle text-positive',
  caution: 'bg-caution-subtle text-caution',
  critical: 'bg-critical-subtle text-critical',
}
const DOT_TONE = {
  neutral: 'bg-ink-faint',
  info: 'bg-primary',
  positive: 'bg-positive',
  caution: 'bg-caution',
  critical: 'bg-critical',
}

export function StatusBadge({ tone = 'neutral', dot = false, children }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2 py-[3px] text-[11px] font-medium ${BADGE_TONE[tone]}`}
    >
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${DOT_TONE[tone]}`} />}
      {children}
    </span>
  )
}

/* =========================================================== motion ===== */

export function Spinner({ className = 'h-4 w-4' }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-20" cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="3" />
      <path
        className="opacity-90"
        fill="currentColor"
        d="M12 3a9 9 0 0 1 9 9h-3a6 6 0 0 0-6-6V3Z"
      />
    </svg>
  )
}

export function Skeleton({ className = '' }) {
  return <div className={`skeleton rounded-md ${className}`} />
}

/** Centered modal surface with a fade-scale entrance. */
export function Overlay({ children, labelledBy }) {
  return (
    <div className="fixed inset-0 z-50 grid animate-fade-in place-items-center bg-ink/45 p-4 backdrop-blur-[3px]">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
        className="w-[min(94vw,440px)] animate-fade-scale rounded-xl border border-hairline bg-surface shadow-overlay"
      >
        {children}
      </div>
    </div>
  )
}

export function Disclosure({ open, children }) {
  return (
    <div className="disclosure" data-open={open ? 'true' : 'false'}>
      <div>{children}</div>
    </div>
  )
}

export function CodeBlock({ children, className = '' }) {
  return (
    <pre
      className={`scroll-slim max-h-72 overflow-auto rounded-lg border border-hairline bg-[#12151d] p-3.5 text-[11.5px] leading-relaxed text-[#d7dbe4] ${className}`}
    >
      {children}
    </pre>
  )
}

/* ========================================================== stepper ===== */

export function Stepper({ steps, currentIndex }) {
  return (
    <ol className="flex items-center">
      {steps.map((step, i) => {
        const state = i < currentIndex ? 'done' : i === currentIndex ? 'current' : 'todo'
        return (
          <li key={step.id} className="flex items-center">
            <span
              className={`flex items-center gap-2 text-[12px] font-medium transition-colors duration-[var(--dur)] ${
                state === 'current'
                  ? 'text-ink'
                  : state === 'done'
                    ? 'text-ink-soft'
                    : 'text-ink-faint'
              }`}
            >
              <span
                className={`grid h-[22px] w-[22px] place-items-center rounded-full text-[11px] font-semibold transition-colors duration-[var(--dur)] ${
                  state === 'current'
                    ? 'bg-primary text-white ring-2 ring-primary/20 ring-offset-1 ring-offset-canvas'
                    : state === 'done'
                      ? 'bg-primary/10 text-primary'
                      : 'border border-hairline-strong text-ink-faint'
                }`}
              >
                {state === 'done' ? <Icon name="check" className="h-3 w-3" strokeWidth={2.6} /> : i + 1}
              </span>
              <span className="hidden md:inline">{step.label}</span>
            </span>
            {i < steps.length - 1 && (
              <span className="mx-2.5 h-[1.5px] w-8 overflow-hidden rounded-full bg-hairline">
                <span
                  className={`block h-full origin-left bg-primary transition-transform duration-300 ease-swift ${
                    i < currentIndex ? 'scale-x-100' : 'scale-x-0'
                  }`}
                />
              </span>
            )}
          </li>
        )
      })}
    </ol>
  )
}

/* ==================================================== completion list == */

export function CompletionList({ items, onJump }) {
  const required = items.filter((i) => i.required)
  const recommended = items.filter((i) => !i.required)
  const render = (item) => {
    const Row = onJump && !item.done ? 'button' : 'div'
    return (
      <li key={item.key}>
        <Row
          {...(Row === 'button'
            ? {
                type: 'button',
                onClick: () => onJump(item.key),
                className:
                  'group flex w-full items-center gap-2.5 rounded-md py-1 pr-1 text-left transition-colors hover:bg-surface-inset',
              }
            : { className: 'flex items-center gap-2.5 py-1' })}
        >
          <span
            className={`grid h-[18px] w-[18px] shrink-0 place-items-center rounded-full transition-colors ${
              item.done
                ? 'bg-positive/12 text-positive'
                : 'border border-hairline-strong bg-surface group-hover:border-primary/50'
            }`}
          >
            {item.done && <Icon name="check" className="h-3 w-3" strokeWidth={2.6} />}
          </span>
          <span className={`text-[13px] ${item.done ? 'text-ink-faint' : 'text-ink'}`}>
            {item.label}
          </span>
          {Row === 'button' && (
            <Icon
              name="chevronRight"
              className="ml-auto h-3.5 w-3.5 text-ink-faint opacity-0 transition-opacity group-hover:opacity-100"
            />
          )}
        </Row>
      </li>
    )
  }
  return (
    <div className="space-y-2.5">
      <ul className="space-y-0.5">{required.map(render)}</ul>
      {recommended.length > 0 && (
        <ul className="space-y-0.5 border-t border-dashed border-hairline pt-2">
          {recommended.map((item) => (
            <li key={item.key} className="flex items-center gap-2.5 py-1">
              <span
                className={`grid h-[18px] w-[18px] shrink-0 place-items-center rounded-full ${
                  item.done ? 'bg-positive/15 text-positive' : 'border border-dashed border-hairline-strong'
                }`}
              >
                {item.done && <Icon name="check" className="h-2.5 w-2.5" strokeWidth={3} />}
              </span>
              <span className="text-[13px] text-ink-faint">
                {item.label} <span className="text-[11px]">· recommended</span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

/* =============================================================== misc === */

export function money(m) {
  if (!m) return '—'
  const sym = { EUR: '€', USD: '$', CHF: 'CHF ' }[m.currency] || ''
  return `${sym}${Number(m.amount).toFixed(2)}`
}
