import { useEffect, useMemo, useState } from 'react'
import type { Fit, Overview, PlanResult, Route, Track } from './api'
import { api } from './api'
import ChartMap from './components/ChartMap'
import DraftGauge from './components/DraftGauge'
import { CharterTimeline, CostDistribution, FanChart, FleetUse, ShipmentBars, WaveSpark } from './components/charts'
import { dateLong, monthName, pct, shortClass, tonnes, usd, usdM, useCountUp } from './format'

const ROUTE_NAMES: Record<string, string> = {
  shortest: 'shortest',
  deep_draft: 'deep water',
  avoid_suez: 'via the Cape',
}
const ROUTE_LONG: Record<string, string> = {
  shortest: 'shortest sea route',
  deep_draft: 'deep-water route, avoiding Torres Strait',
  avoid_suez: 'via the Cape of Good Hope',
}

const portName = (o: Overview, id: string) => o.ports.find((p) => p.port_id === id)?.name ?? id

/* ================================================================== hero */
export function Hero({ overview, tracks, plan, planning }: { overview: Overview; tracks: Track[]; plan: PlanResult | null; planning: boolean }) {
  const mapTracks = useMemo(() => tracks.map((t) => ({ id: `${t.origin}-${t.destination}-${t.kind}`, points: t.points, kind: t.kind })), [tracks])
  const [spot, best] = plan?.strategies ?? []
  const fixedNow = plan?.time_charters.filter((c) => c.hire_usd_day) ?? []
  const vessels = fixedNow.reduce((a, c) => a + c.vessels, 0)
  const classes = [...new Set(fixedNow.map((c) => shortClass(c.vessel_class)))].join(' and ')
  const longest = Math.max(0, ...fixedNow.map((c) => c.months))
  const coaKt = Math.round((plan?.coa.reduce((a, c) => a + c.tonnes, 0) ?? 0) / 1000)
  const worstSpot = useCountUp(spot?.cvar_usd_m ?? 0), worstPlan = useCountUp(best?.cvar_usd_m ?? 0)
  return (
    <header id="chart" style={{ position: 'relative', background: 'var(--paper)' }}>
      <div style={{ padding: '28px var(--gutter) 0' }}>
        <p className="kicker">Coal imports to India's East Coast · market of {dateLong(overview.forecast.as_of)}</p>
        <h1 style={{ font: '900 clamp(48px, 9vw, 132px)/0.84 var(--display)', textTransform: 'uppercase', margin: '0 0 8px', letterSpacing: '-0.005em' }}>
          What to fix <span style={{ color: 'var(--depth)' }}>this week</span>
        </h1>
      </div>
      <div style={{ position: 'relative', padding: '0 var(--gutter)' }}>
        <ChartMap tracks={mapTracks} ports={overview.ports} title="Chart of voyage routes from 12 load ports to India's East Coast" />
        <aside className="panel hero-card" aria-live="polite">
          <p className="kicker" style={{ fontSize: 16 }}>Recommended plan</p>
          {!plan ? (
            <p className="big" style={{ fontSize: 30 }}>{planning ? 'Testing 200 freight scenarios…' : 'Plan unavailable'}</p>
          ) : (
            <>
              <p className="big" style={{ fontSize: 'clamp(28px, 3.2vw, 40px)', margin: '0 0 10px', textTransform: 'uppercase' }}>
                {vessels > 0 && `Fix ${vessels} ${classes} on ${longest}-month charters now`}
                {vessels > 0 && coaKt > 0 && <span style={{ color: 'var(--depth)' }}> + {coaKt.toLocaleString('en-US')} kt on COA</span>}
                {vessels === 0 && coaKt > 0 && `Lock ${coaKt.toLocaleString('en-US')} kt on COAs now`}
                {vessels === 0 && coaKt === 0 && 'Stay on spot this week'}
              </p>
              <p style={{ margin: '0 0 12px', color: 'var(--ink-2)' }}>
                Average cost in the worst 10% of freight markets falls from <b className="mono">{usdM(worstSpot)}</b> to{' '}
                <b className="mono" style={{ color: 'var(--depth)' }}>{usdM(worstPlan)}</b>. Expected cost {usdM(best.expected_cost_usd_m)} against {usdM(spot.expected_cost_usd_m)} all spot.
              </p>
              <span className="pill magenta">Synthetic cargo programme · placeholder costs</span>
            </>
          )}
        </aside>
      </div>
    </header>
  )
}

/* ================================================================== ship check */
export function ShipCheck({ overview }: { overview: Overview }) {
  const loads = overview.ports.filter((p) => p.role === 'load')
  const disch = overview.ports.filter((p) => p.role === 'discharge' && p.operation !== 'transloading')
  const [origin, setOrigin] = useState('hay_point')
  const [dest, setDest] = useState('paradip')
  const [fit, setFit] = useState<Fit | null>(null)
  const [err, setErr] = useState('')
  useEffect(() => {
    let live = true
    setErr('')
    api.fit(origin, dest).then((f) => live && setFit(f)).catch((e) => live && setErr(e.message))
    return () => { live = false }
  }, [origin, dest])

  const perClass = useMemo(() => {
    if (!fit) return []
    return overview.vessels.map((v) => {
      const rows = fit.options.filter((o) => o.vessel_class === v.vessel_class)
      return rows.find((r) => r.feasible) ?? rows[0]
    }).filter(Boolean)
  }, [fit, overview.vessels])
  const best = fit?.options.find((o) => o.feasible)
  const gaugeLimits = fit ? Object.values(fit.limits).filter((l) => !l.transloading).map((l) => ({ label: portName(overview, l.port), limit: l })) : []
  const countries = [...new Set(loads.map((p) => p.country))]

  return (
    <section className="block" id="ship">
      <p className="kicker">Vessel type against port limits</p>
      <h2>Which ship fits this route?</h2>
      <p className="lede">Pick a load port and an East Coast port. Each Baltic standard ship is checked against the length, beam, size and draft limits at both ends. Where a port is shallower than the ship, cargo is cut until she floats at the limit.</p>
      <div className="controls">
        <label className="field">Load port
          <select value={origin} onChange={(e) => setOrigin(e.target.value)}>
            {countries.map((c) => (
              <optgroup key={c} label={c}>{loads.filter((p) => p.country === c).map((p) => <option key={p.port_id} value={p.port_id}>{p.name}</option>)}</optgroup>
            ))}
          </select>
        </label>
        <label className="field">Discharge port
          <select value={dest} onChange={(e) => setDest(e.target.value)}>
            {disch.map((p) => <option key={p.port_id} value={p.port_id}>{p.name}</option>)}
          </select>
        </label>
        {best && (
          <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
            <div className="kicker" style={{ fontSize: 15, margin: 0 }}>Cheapest per tonne at today's hire</div>
            <div className="big">{shortClass(best.vessel_class)} <span style={{ color: 'var(--depth)' }}>{usd(best.spot_usd_per_t!, 2)}/t</span></div>
          </div>
        )}
      </div>
      {err && <p className="caution">{err}</p>}
      {fit && (
        <div className="stack">
          <div className="panel" style={{ padding: '12px 12px 4px' }}>
            <DraftGauge vessels={overview.vessels} options={perClass} limits={gaugeLimits} />
            {dest === 'haldia' && <p className="caution" style={{ margin: '4px 8px 8px' }}>Ships too deep or too long for Haldia can discharge at Sandheads anchorage and transload by barge; the table shows both.</p>}
          </div>
          <div className="grid-2">
            <div className="panel table-wrap">
              <h3>Options, cheapest first</h3>
              <p className="sub">Spot freight per tonne at today's Baltic hire. Round voyage with a ballast return.</p>
              <table className="data">
                <thead><tr><th>Ship</th><th>Discharge</th><th className="num">Cargo</th><th>Route</th><th className="num">Days</th><th className="num">$/t</th></tr></thead>
                <tbody>
                  {fit.options.map((o) => (
                    <tr key={`${o.vessel_class}${o.discharge_at}`} style={{ opacity: o.feasible ? 1 : 0.55 }}>
                      <td><b>{shortClass(o.vessel_class)}</b>{o.why && <div className="caution" style={{ fontSize: 12.5 }}>{o.why}</div>}</td>
                      <td>{portName(overview, o.discharge_at)}</td>
                      <td className="num">{o.feasible ? tonnes(o.cargo_t) : '·'}</td>
                      <td style={{ fontSize: 12.5 }}>{o.route ? ROUTE_NAMES[o.route] : 'cannot call'}{o.distance_nm ? <div className="muted mono">{o.distance_nm.toLocaleString('en-US')} nm</div> : null}</td>
                      <td className="num">{o.round_trip_days ?? '·'}</td>
                      <td className="num"><b>{o.spot_usd_per_t ? o.spot_usd_per_t.toFixed(2) : '·'}</b></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="panel">
              <h3>{portName(overview, origin)} to {portName(overview, best?.discharge_at ?? dest)}</h3>
              <p className="sub">{best?.route ? ROUTE_LONG[best.route] : ''}{best?.distance_nm ? `, ${best.distance_nm.toLocaleString('en-US')} nm` : ''}</p>
              {fit.track && (
                <ChartMap mode="inset" width={640} height={420} tracks={[{ id: 'sel', points: fit.track, kind: 'main' }]}
                  ports={overview.ports} focusPorts={[origin, best?.discharge_at ?? dest]} title="Selected voyage" />
              )}
              <div style={{ marginTop: 12, fontSize: 13 }}>
                {Object.values(fit.limits).map((l) => (
                  <div key={l.port} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, borderTop: '1px solid #eef3f7', padding: '6px 0' }}>
                    <span><b>{portName(overview, l.port)}</b> <span className="muted">{l.berth}</span></span>
                    <span className="mono" style={{ textAlign: 'right' }}>{l.transloading ? 'anchorage, no draft limit' : `${l.draft_m ? `${l.draft_m.toFixed(2)} m` : 'draft ?'} · ${l.loa_m ? `${l.loa_m} m LOA` : 'LOA ?'}`}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

/* ================================================================== outlook */
export function Outlook({ overview }: { overview: Overview }) {
  const [model, setModel] = useState('random_walk')
  const f = overview.forecast
  const hold = (m: string, h: number) => overview.backtest.find((b) => b.period === 'holdout' && b.model === m && b.horizon === h)
  const rank = f.weekly_volatility_pct_rank
  return (
    <section className="block" id="outlook">
      <p className="kicker">Freight outlook</p>
      <h2>Where freight could be in six months</h2>
      <p className="lede">The line is the BDRY dry bulk freight futures ETF, the free proxy we can test on. The shaded range is where the price should land 8 times in 10. Testing on 2021 to 2023 found no model that beats "no change" on direction, so the centre stays flat and the work goes into honest ranges.</p>
      <div className="grid-2">
        <div className="panel">
          <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
            {[['random_walk', 'Range from past moves (selected)'], ['vol_random_walk', "Range scaled to today's volatility"]].map(([k, l]) => (
              <button key={k} className="btn ghost" aria-pressed={model === k} onClick={() => setModel(k)}
                style={model === k ? { background: 'var(--ink)', color: 'var(--paper)' } : undefined}>{l}</button>
            ))}
          </div>
          <FanChart history={overview.history} forecast={f} model={model} />
        </div>
        <div className="stack">
          <div className="panel">
            <h3>Market mood</h3>
            <p className="big" style={{ color: rank < 0.2 ? 'var(--depth)' : rank > 0.8 ? 'var(--magenta)' : 'var(--ink)' }}>
              {rank < 0.2 ? 'Calm' : rank > 0.8 ? 'Turbulent' : 'Normal'}
            </p>
            <p style={{ margin: 0, color: 'var(--ink-2)' }}>Weekly volatility is {pct(f.weekly_volatility, 1)}, quieter than {pct(1 - rank)} of weeks since 2018. Calm spells end; the volatility-scaled range is narrower now for that reason.</p>
          </div>
          <div className="panel table-wrap">
            <h3>How the ranges held up</h3>
            <p className="sub">Share of 2024 to 2026 outcomes inside the 80% range (target 80%).</p>
            <table className="data">
              <thead><tr><th>Weeks ahead</th><th className="num">Past moves</th><th className="num">Volatility-scaled</th></tr></thead>
              <tbody>
                {[1, 4, 13, 26].map((h) => (
                  <tr key={h}><td>{h}</td><td className="num">{hold('random_walk', h) ? pct(hold('random_walk', h)!.coverage_80) : '·'}</td><td className="num">{hold('vol_random_walk', h) ? pct(hold('vol_random_walk', h)!.coverage_80) : '·'}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ================================================================== charter plan */
export function CharterPlan({ overview, plan, planning, onRun, error }: {
  overview: Overview; plan: PlanResult | null; planning: boolean; error: string
  onRun: (routes: Route[], risk: number, premium: number) => void
}) {
  const [routes, setRoutes] = useState<Route[]>(overview.programme.routes)
  const [risk, setRisk] = useState(overview.risk.risk_weight)
  const [premium, setPremium] = useState(overview.contracts.period_premium)
  const loads = overview.ports.filter((p) => p.role === 'load')
  const disch = overview.ports.filter((p) => p.role === 'discharge' && p.operation !== 'transloading')
  const months = Array.from({ length: overview.programme.months }, (_, i) => {
    const [y, m] = overview.programme.start_month.split('-').map(Number)
    const d = new Date(y, m - 1 + i, 1); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  })
  const edit = (i: number, patch: Partial<Route>) => setRoutes((rs) => rs.map((r, j) => (j === i ? { ...r, ...patch } : r)))
  const [spot, best] = plan?.strategies ?? []
  const expSpot = useCountUp(spot?.expected_cost_usd_m ?? 0), expBest = useCountUp(best?.expected_cost_usd_m ?? 0)
  const worstSpot = useCountUp(spot?.cvar_usd_m ?? 0), worstBest = useCountUp(best?.cvar_usd_m ?? 0)
  const coaByRoute = useMemo(() => {
    const g = new Map<string, { route: string; cls: string; tonnes: number; months: Set<string> }>()
    plan?.coa.forEach((c) => {
      const e = g.get(c.route) ?? { route: c.route, cls: c.vessel_class, tonnes: 0, months: new Set<string>() }
      e.tonnes += c.tonnes; e.months.add(c.month); g.set(c.route, e)
    })
    return [...g.values()]
  }, [plan])

  return (
    <section className="block" id="plan">
      <p className="kicker">Spot, time charter or contract of affreightment</p>
      <h2>Build the charter plan</h2>
      <p className="lede">Enter the monthly import plan. NauPlan tests every mix of spot voyages, 3 and 6 month time charters and COAs against {overview.risk.scenarios} freight scenarios drawn from real market moves, then picks the plan with the best balance of expected cost and bad-case cost. Idle days on chartered ships are relet to the market.</p>
      <div className="panel table-wrap" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 8 }}>
          <h3>Monthly import plan (thousand tonnes)</h3>
          {overview.programme.synthetic && <span className="pill magenta">Example figures, not SAIL data</span>}
        </div>
        <table className="data" style={{ marginTop: 10 }}>
          <thead><tr><th>Load port</th><th>Discharge port</th>{months.map((m) => <th key={m} className="num">{monthName(m)}</th>)}<th /></tr></thead>
          <tbody>
            {routes.map((r, i) => (
              <tr key={i}>
                <td><select aria-label="Load port" value={r.origin} onChange={(e) => edit(i, { origin: e.target.value })} style={{ minWidth: 150 }}>{loads.map((p) => <option key={p.port_id} value={p.port_id}>{p.name}</option>)}</select></td>
                <td><select aria-label="Discharge port" value={r.destination} onChange={(e) => edit(i, { destination: e.target.value })} style={{ minWidth: 150 }}>{disch.map((p) => <option key={p.port_id} value={p.port_id}>{p.name}</option>)}</select></td>
                {months.map((m, k) => (
                  <td key={m} className="num"><input type="number" min={0} step={10} aria-label={`${monthName(m)} thousand tonnes`}
                    value={Math.round(r.tonnes_per_month[k] / 1000)}
                    onChange={(e) => edit(i, { tonnes_per_month: r.tonnes_per_month.map((t, j) => (j === k ? Math.max(0, Number(e.target.value)) * 1000 : t)) })} /></td>
                ))}
                <td><button className="btn ghost" aria-label="Remove route" onClick={() => setRoutes((rs) => rs.filter((_, j) => j !== i))} disabled={routes.length === 1}>Remove</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        <button className="btn ghost" style={{ marginTop: 10 }} onClick={() => setRoutes((rs) => [...rs, { origin: 'gladstone', destination: 'paradip', tonnes_per_month: months.map(() => 100000) }])}>Add route</button>
      </div>
      <div className="controls">
        <label className="field">Weight on bad-case cost: {risk.toFixed(1)}
          <input type="range" min={0} max={3} step={0.1} value={risk} onChange={(e) => setRisk(Number(e.target.value))} />
        </label>
        <label className="field">Period hire vs today's spot: {premium >= 0 ? '+' : ''}{pct(premium)}
          <input type="range" min={-0.1} max={0.2} step={0.01} value={premium} onChange={(e) => setPremium(Number(e.target.value))} />
        </label>
        <button className="btn" onClick={() => onRun(routes, risk, premium)} disabled={planning}>{planning ? 'Testing scenarios…' : 'Optimise plan'}</button>
      </div>
      {error && <p className="caution">{error}</p>}
      {plan && spot && best && (
        <div className="stack">
          <div className="grid-2" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))' }}>
            {[{ t: 'All spot (current practice)', e: expSpot, w: worstSpot, c: 'var(--ink-2)' }, { t: 'NauPlan', e: expBest, w: worstBest, c: 'var(--depth)' }].map((s) => (
              <div key={s.t} className="panel" style={{ borderTop: `4px solid ${s.c}` }}>
                <h3>{s.t}</h3>
                <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap', marginTop: 8 }}>
                  <div><div className="muted" style={{ fontSize: 12 }}>Expected cost</div><div className="big" style={{ color: s.c }}>{usdM(s.e)}</div></div>
                  <div><div className="muted" style={{ fontSize: 12 }}>Average of worst 10%</div><div className="big" style={{ color: s.c }}>{usdM(s.w)}</div></div>
                </div>
              </div>
            ))}
            <div className="panel" style={{ borderTop: '4px solid var(--magenta)' }}>
              <h3>Difference</h3>
              {(() => {
                const d = (a: number, b: number, f: (v: number) => string) => `${f(Math.abs(a - b))} ${a <= b ? 'lower' : 'higher'}`
                return (
                  <p style={{ margin: '8px 0 0' }}>
                    Expected cost <b className="mono">{d(best.expected_cost_usd_m, spot.expected_cost_usd_m, usdM)}</b>. Worst 10% <b className="mono">{d(best.cvar_usd_m, spot.cvar_usd_m, usdM)}</b>. Per tonne <b className="mono">{d(best.expected_usd_per_t, spot.expected_usd_per_t, (v) => usd(v, 2))}</b>.
                  </p>
                )
              })()}
              <p className="caution" style={{ margin: '8px 0 0' }}>With no directional view, contracts mostly buy certainty rather than a lower average.</p>
            </div>
          </div>
          <div className="panel">
            <h3>Programme cost across {plan.costs_usd_m.spot.length} freight scenarios</h3>
            <p className="sub">Grey: all spot. Blue: NauPlan. A narrow blue spike means the plan's cost barely depends on where freight goes.</p>
            <CostDistribution spot={plan.costs_usd_m.spot} plan={plan.costs_usd_m.plan} alpha={plan.alpha} />
          </div>
          <div className="panel">
            <h3>What to fix and when</h3>
            <p className="sub">Charters starting later are fixed at that month's market hire.</p>
            <CharterTimeline months={plan.months} charters={plan.time_charters}
              coaByRoute={coaByRoute.map((c) => ({ ...c, route: c.route.split(' > ').map((id) => portName(overview, id)).join(' > ') }))} />
          </div>
          <div className="grid-2">
            <div className="panel"><h3>How each month ships</h3><p className="sub">Scenario average, tonnes.</p><ShipmentBars months={plan.months} shipments={plan.shipments} /></div>
            <div className="panel"><h3>Chartered ship days</h3><p className="sub">Spare days are relet rather than left idle.</p><FleetUse fleet={plan.fleet} /></div>
          </div>
        </div>
      )}
    </section>
  )
}

/* ================================================================== warnings */
export function Warnings({ overview }: { overview: Overview }) {
  const east = overview.sea_state
  const gaps = overview.limits.filter((l) => !l.transloading && (l.draft_m === null || l.loa_m === null))
  const high = east.filter((s) => s.wave_m > s.p90_month_m)
  return (
    <section className="block" id="warnings">
      <p className="kicker">Early warnings</p>
      <h2>What could disrupt the plan</h2>
      <p className="lede">Sea state off each East Coast port from ERA5 wave data, compared with the usual level for this month. A reading above the dashed line is higher than 9 in 10 past days of the same month.</p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(230px, 1fr))', gap: 14, marginBottom: 24 }}>
        {east.map((s) => {
          const hi = s.wave_m > s.p90_month_m
          return (
            <div key={s.port} className="panel" style={{ padding: 14, borderColor: hi ? 'var(--magenta)' : undefined }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <b style={{ font: '800 18px var(--display)', textTransform: 'uppercase', letterSpacing: '0.03em' }}>{portName(overview, s.port)}</b>
                <span className="mono" style={{ color: hi ? 'var(--magenta)' : 'var(--depth)' }}>{s.wave_m.toFixed(1)} m</span>
              </div>
              <WaveSpark s={s} />
              <div className="muted" style={{ fontSize: 12 }}>{hi ? <span className="caution">Above the usual level for the month</span> : 'Within the usual range'} · {dateLong(s.date)}</div>
            </div>
          )
        })}
      </div>
      <div className="grid-2">
        <div className="panel">
          <h3>{high.length ? `${high.length} port${high.length > 1 ? 's' : ''} above usual swell` : 'Swell is normal'}</h3>
          <p className="sub">Heavy swell slows cargo work and pilot boarding; consider it when setting laycans for the next fortnight.</p>
          <p style={{ margin: 0 }}>{high.map((s) => portName(overview, s.port)).join(', ') || 'No East Coast port is above its usual level.'}</p>
        </div>
        <div className="panel">
          <h3>Data still missing</h3>
          <p className="sub">Limits not yet sourced are not enforced, so check these before relying on a result.</p>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
            {gaps.map((g) => <li key={g.port}><b>{portName(overview, g.port)}</b>: {[g.draft_m === null && 'draft', g.loa_m === null && 'length'].filter(Boolean).join(' and ')} limit</li>)}
            <li>{overview.placeholders.length} cost and operating parameters are placeholders (bunker price, port costs, waiting days and more)</li>
          </ul>
        </div>
      </div>
    </section>
  )
}

/* ================================================================== footer */
export function Footer({ overview }: { overview: Overview }) {
  return (
    <footer className="block" style={{ background: 'var(--ink)', color: 'var(--shoal)', padding: '40px var(--gutter)', fontSize: 13 }}>
      <p style={{ font: '900 28px var(--display)', color: 'var(--paper)', letterSpacing: '0.06em', margin: '0 0 8px' }}>NAUPLAN</p>
      <p style={{ maxWidth: '80ch', margin: '0 0 12px' }}>
        Team Vector66, Smart India Hackathon 2026, problem statement SIH26006 (Ministry of Steel, SAIL). Vessel specifications and today's hire: Baltic Exchange Guide to Market Benchmarks v8.7 and index levels ({overview.market.note}). Port limits: port authority and terminal documents, cited per berth. Freight proxy: BDRY via Yahoo Finance. Brent and USD/INR: FRED. Coal prices: World Bank Pink Sheet. Sea state: Open-Meteo ERA5. Sea routes: searoute (Eurostat MARNET).
      </p>
      <p style={{ margin: 0 }}><a href="https://github.com/Tarkshya-26/nauplan" style={{ color: 'var(--shoal-2)' }}>Source code and method notes</a></p>
    </footer>
  )
}
