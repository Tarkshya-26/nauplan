import { useCallback, useEffect, useState } from 'react'
import type { Overview, PlanResult, Route, Track } from './api'
import { api } from './api'
import { shortClass } from './format'
import { CharterPlan, Footer, Hero, Outlook, ShipCheck, Warnings } from './sections'

const TICKER_ORDER = ['Capesize', 'Panamax/Kamsarmax', 'Supramax/Ultramax', 'Handysize']

export default function App() {
  const [overview, setOverview] = useState<Overview | null>(null)
  const [tracks, setTracks] = useState<Track[]>([])
  const [plan, setPlan] = useState<PlanResult | null>(null)
  const [planning, setPlanning] = useState(false)
  const [planErr, setPlanErr] = useState('')
  const [loadErr, setLoadErr] = useState('')

  const runPlan = useCallback((routes: Route[], risk: number, premium: number, start: string) => {
    setPlanning(true); setPlanErr('')
    api.plan({ start_month: start, routes, risk_weight: risk, period_premium: premium })
      .then(setPlan).catch((e) => setPlanErr(e.message)).finally(() => setPlanning(false))
  }, [])

  useEffect(() => {
    api.overview().then((o) => {
      setOverview(o)
      runPlan(o.programme.routes, o.risk.risk_weight, o.contracts.period_premium, o.programme.start_month)
    }).catch((e) => setLoadErr(e.message))
    api.tracks().then(setTracks).catch(() => setTracks([]))
  }, [runPlan])

  if (loadErr) return <main style={{ padding: 48 }}><h1 style={{ font: '900 48px var(--display)' }}>NAUPLAN</h1><p className="caution">Could not reach the NauPlan API ({loadErr}). Start it with <code>uv run nauplan serve</code> and reload.</p></main>
  if (!overview) return <main style={{ padding: 48 }}><p className="kicker">Loading the chart…</p></main>

  return (
    <>
      <a href="#ship" className="skip">Skip to vessel check</a>
      <div className="topbar">
        <a className="brand" href="#chart"><b>NAUPLAN</b><i>freight &amp; charter planning, East Coast India</i></a>
        <nav className="nav" aria-label="Sections">
          <a href="#ship">Vessel check</a><a href="#outlook">Outlook</a><a href="#plan">Charter plan</a><a href="#warnings">Warnings</a>
        </nav>
        <div className="ticker" title={`Average spot timecharter hire, US$ per day. ${overview.market.note}.`}>
          {TICKER_ORDER.map((c) => <span key={c}>{shortClass(c).toUpperCase()}<b>{Math.round(overview.market.hire_usd_day[c]).toLocaleString('en-US')}</b></span>)}
          <span>$/DAY</span>
        </div>
      </div>
      <main>
        <Hero overview={overview} tracks={tracks} plan={plan} planning={planning} />
        <ShipCheck overview={overview} />
        <Outlook overview={overview} />
        <CharterPlan overview={overview} plan={plan} planning={planning} error={planErr}
          onRun={(routes, risk, premium) => runPlan(routes, risk, premium, overview.programme.start_month)} />
        <Warnings overview={overview} />
      </main>
      <Footer overview={overview} />
    </>
  )
}
