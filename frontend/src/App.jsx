import { useState } from 'react'
import { Stepper } from './components/ui'
import ImportPage from './components/ImportPage'
import ReviewPage from './components/ReviewPage'
import EditorWorkspace from './components/editor/EditorWorkspace'
import SuccessScreen from './components/SuccessScreen'

const STEPS = [
  { id: 'import', label: 'Import' },
  { id: 'review', label: 'Review' },
  { id: 'editor', label: 'Edit & Enrich' },
  { id: 'done', label: 'Export' },
]

function Wordmark() {
  return (
    <div className="flex items-center gap-2.5">
      <span className="grid h-7 w-7 place-items-center rounded-md bg-primary text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.16)]">
        {/* raw lines → structured record */}
        <svg
          className="h-[18px] w-[18px]"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        >
          <path d="M3.5 5h5M3.5 8h5M3.5 11h3.5" />
          <path d="M8.5 7.5c3.4 0 3.75 2 3.75 4.25" opacity="0.8" />
          <rect x="11.5" y="10" width="5.5" height="6" rx="1.4" fill="currentColor" stroke="none" />
        </svg>
      </span>
      <div className="leading-none">
        <div className="text-[13px] font-semibold tracking-[-0.006em] text-ink">
          Product Data Automation
        </div>
        <div className="mt-[5px] text-[9.5px] font-semibold uppercase tracking-[0.2em] text-ink-faint">
          Portfolio Demo
        </div>
      </div>
    </div>
  )
}

/** Wizard: import → review → editor → done. */
export default function App() {
  const [step, setStep] = useState('import')
  const [ingestResult, setIngestResult] = useState(null)
  const [selected, setSelected] = useState([])
  const [created, setCreated] = useState([])

  function reset() {
    setIngestResult(null)
    setSelected([])
    setCreated([])
    setStep('import')
  }

  const currentIndex = STEPS.findIndex((s) => s.id === step)
  const container =
    step === 'editor'
      ? 'max-w-[1320px]'
      : step === 'import'
        ? 'max-w-[1080px]'
        : 'max-w-[900px]'

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-hairline bg-canvas/85 backdrop-blur-md">
        <div className="mx-auto grid h-14 max-w-[1320px] grid-cols-[1fr_auto] items-center gap-6 px-6 sm:px-8 md:grid-cols-[1fr_auto_1fr]">
          <Wordmark />
          <div className="justify-self-end md:justify-self-center">
            <Stepper steps={STEPS} currentIndex={currentIndex} />
          </div>
        </div>
      </header>

      <main className={`mx-auto px-6 py-10 sm:px-8 sm:py-12 ${container}`}>
        {step === 'import' && (
          <ImportPage
            onIngested={(result) => {
              setIngestResult(result)
              setStep('review')
            }}
          />
        )}

        {step === 'review' && ingestResult && (
          <ReviewPage
            result={ingestResult}
            onBack={reset}
            onContinue={(items) => {
              setSelected(items)
              setStep('editor')
            }}
          />
        )}

        {step === 'editor' && (
          <EditorWorkspace
            items={selected}
            supplierName={ingestResult?.supplier_name}
            onBack={() => setStep('review')}
            onDone={(shopProducts) => {
              setCreated(shopProducts)
              setStep('done')
            }}
          />
        )}

        {step === 'done' && <SuccessScreen products={created} onRestart={reset} />}
      </main>
    </div>
  )
}
