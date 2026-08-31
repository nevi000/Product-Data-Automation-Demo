import { useEffect, useRef } from 'react'
import { api } from '../../lib/api'
import { Button, Icon, IconButton, SectionCard, Skeleton } from '../ui'

const KINDS = [
  { id: 'model_shot', label: 'Model shot' },
  { id: 'lifestyle', label: 'Lifestyle' },
  { id: 'packshot', label: 'Packshot' },
]

// 1x1 transparent PNG — stands in for "the raw supplier photo" the pipeline edits.
const PIXEL =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='

const STAGE_TEXT = { removing_bg: 'Removing background…', generating: 'Generating…' }

export default function ImagesSection({ jobs, setJobs, imageUrls, onImagesChange, disabled, highlighted }) {
  const timers = useRef({})
  const lastUrls = useRef('')

  useEffect(() => {
    const urls = jobs.filter((j) => j.status === 'completed' && j.image_url).map((j) => j.image_url)
    const key = urls.join('|')
    if (key !== lastUrls.current) {
      lastUrls.current = key
      onImagesChange(urls)
    }
  }, [jobs, onImagesChange])

  useEffect(() => {
    jobs.forEach((job) => {
      if (job.status === 'processing' && !timers.current[job.id]) poll(job.id)
    })
    return () => {
      Object.values(timers.current).forEach(clearInterval)
      timers.current = {}
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobs.length])

  function poll(id) {
    timers.current[id] = setInterval(async () => {
      try {
        const updated = await api.pollImageJob(id)
        setJobs((prev) => prev.map((j) => (j.id === id ? updated : j)))
        if (updated.status !== 'processing') {
          clearInterval(timers.current[id])
          delete timers.current[id]
        }
      } catch {
        clearInterval(timers.current[id])
        delete timers.current[id]
      }
    }, 650)
  }

  async function addJob(kind) {
    const blob = await (await fetch(PIXEL)).blob()
    const file = new File([blob], 'raw.png', { type: 'image/png' })
    const job = await api.startImageJob(file, kind)
    setJobs((prev) => [...prev, job])
    if (job.status === 'processing') poll(job.id)
  }

  function removeJob(id) {
    clearInterval(timers.current[id])
    delete timers.current[id]
    setJobs((prev) => prev.filter((j) => j.id !== id))
  }

  return (
    <SectionCard
      id="sec-images"
      icon="image"
      title="Product images"
      description="Generate product imagery for the storefront."
      highlighted={highlighted}
      action={
        !disabled &&
        KINDS.map((k) => (
          <Button key={k.id} variant="secondary" size="sm" type="button" onClick={() => addJob(k.id)}>
            <Icon name="plus" className="h-3.5 w-3.5" />
            {k.label}
          </Button>
        ))
      }
    >
      {jobs.length === 0 ? (
        <div className="flex items-center gap-3 py-1 text-[13px] text-ink-soft">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-surface-inset text-ink-faint">
            <Icon name="image" className="h-4 w-4" />
          </span>
          <span>
            No images yet.
            <span className="text-ink-faint"> Generate a model shot, lifestyle image, or packshot.</span>
          </span>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 xl:grid-cols-4">
          {jobs.map((j) => (
            <figure
              key={j.id}
              className="group overflow-hidden rounded-md border border-hairline bg-surface"
            >
              <div className="relative aspect-[4/5] bg-surface-inset">
                {j.status === 'completed' && j.image_url ? (
                  <img
                    src={j.image_url}
                    alt={`${j.kind.replace('_', ' ')} render`}
                    className="h-full w-full object-cover"
                  />
                ) : j.status === 'failed' ? (
                  <div className="grid h-full place-items-center text-meta text-critical">Failed</div>
                ) : (
                  <>
                    <Skeleton className="h-full w-full rounded-none" />
                    <span className="absolute inset-x-0 bottom-3 text-center text-meta text-ink-soft">
                      {STAGE_TEXT[j.stage] || 'Generating…'}
                    </span>
                  </>
                )}
                {!disabled && (
                  <IconButton
                    label="Remove image"
                    onClick={() => removeJob(j.id)}
                    className="absolute right-1.5 top-1.5 border border-hairline bg-surface/95 text-ink-soft opacity-0 shadow-sm transition-opacity hover:bg-surface hover:text-ink group-hover:opacity-100 focus-visible:opacity-100"
                  >
                    <Icon name="x" className="h-3.5 w-3.5" strokeWidth={2.2} />
                  </IconButton>
                )}
              </div>
              <figcaption className="flex items-center justify-between gap-2 border-t border-hairline px-2.5 py-2">
                <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-ink-soft">
                  {j.kind.replace('_', ' ')}
                </span>
                <span className="text-[10px] text-ink-faint">mock render</span>
              </figcaption>
            </figure>
          ))}
        </div>
      )}

      <p className="mt-4 flex items-center gap-1.5 text-[11px] text-ink-faint">
        {imageUrls.length > 0 && <Icon name="check" className="h-3 w-3 text-positive" />}
        {imageUrls.length > 0
          ? `${imageUrls.length} image${imageUrls.length === 1 ? '' : 's'} will be attached on export.`
          : 'Public demo uses deterministic offline mock renders.'}
      </p>
    </SectionCard>
  )
}
