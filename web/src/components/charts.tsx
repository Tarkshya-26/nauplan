import { bin, extent, max } from 'd3-array'
import { scaleBand, scaleLinear, scaleLog, scaleTime } from 'd3-scale'
import { area, curveMonotoneX, line } from 'd3-shape'
import type { FleetRow, Forecast, Quantiles, SeaState, Shipment, TimeCharter } from '../api'
import { monthName, shortClass } from '../format'

/* ------------------------------------------------------------------ fan chart */
export function FanChart({ history, forecast, model }: {
  history: { date: string; price: number }[]; forecast: Forecast; model: string
}) {
  const W = 900, H = 340, m = { l: 44, r: 90, t: 16, b: 30 }
  const last = new Date(`${forecast.as_of}T00:00:00`)
  const hs = Object.keys(forecast.horizons).map(Number).sort((a, b) => a - b)
  const band = [{ h: 0, p10: forecast.last_price, p50: forecast.last_price, p90: forecast.last_price },
    ...hs.map((h) => ({ h, ...(forecast.horizons[String(h)][model] as Quantiles) }))]
  const at = (h: number) => new Date(last.getTime() + h * 7 * 864e5)
  const hist = history.map((d) => ({ t: new Date(`${d.date}T00:00:00`), v: d.price }))
  const x = scaleTime().domain([hist[0].t, at(26)]).range([m.l, W - m.r])
  const vals = [...hist.map((d) => d.v), ...band.flatMap((b) => [b.p10, b.p90])]
  const [vmin, vmax] = extent(vals) as [number, number]
  const y = scaleLog().domain([vmin * 0.9, vmax * 1.1]).range([H - m.b, m.t])
  const bandArea = area<(typeof band)[number]>().x((d) => x(at(d.h))).y0((d) => y(d.p10)).y1((d) => y(d.p90)).curve(curveMonotoneX)
  const mid = line<(typeof band)[number]>().x((d) => x(at(d.h))).y((d) => y(d.p50))
  const histLine = line<(typeof hist)[number]>().x((d) => x(d.t)).y((d) => y(d.v))
  const yTicks = [2, 3, 5, 7, 10, 15, 20, 30, 40, 60].filter((t) => t >= vmin * 0.9 && t <= vmax * 1.1)
  const end = band[band.length - 1]
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Freight proxy history and forecast range" style={{ width: '100%', height: 'auto' }}>
      {yTicks.map((t) => (
        <g key={t} className="axis">
          <line x1={m.l} x2={W - m.r} y1={y(t)} y2={y(t)} stroke="var(--rule)" strokeWidth={0.6} />
          <text x={m.l - 6} y={y(t) + 4} textAnchor="end">{t}</text>
        </g>
      ))}
      {x.ticks(6).map((t) => (
        <text key={+t} x={x(t)} y={H - 8} textAnchor="middle" className="tick-label">{t.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' })}</text>
      ))}
      <rect x={x(last)} y={m.t} width={W - m.r - x(last)} height={H - m.t - m.b} fill="var(--shoal)" opacity={0.35} />
      <path d={bandArea(band) ?? ''} fill="var(--depth-2)" opacity={0.35} />
      <path d={mid(band) ?? ''} fill="none" stroke="var(--depth)" strokeWidth={1.6} strokeDasharray="5 4" />
      <path d={histLine(hist) ?? ''} fill="none" stroke="var(--ink)" strokeWidth={1.8} />
      <circle cx={x(last)} cy={y(forecast.last_price)} r={4.5} fill="var(--ink)" stroke="var(--paper)" strokeWidth={2} />
      <text x={W - m.r + 6} y={y(end.p90) + 4} className="tick-label" style={{ fill: 'var(--depth)' }}>P90 {end.p90.toFixed(1)}</text>
      <text x={W - m.r + 6} y={y(end.p50) + 4} className="tick-label" style={{ fill: 'var(--depth)' }}>P50 {end.p50.toFixed(1)}</text>
      <text x={W - m.r + 6} y={y(end.p10) + 4} className="tick-label" style={{ fill: 'var(--depth)' }}>P10 {end.p10.toFixed(1)}</text>
      <text x={x(last) + 8} y={m.t + 16} style={{ font: 'italic 14px var(--hydro)', fill: 'var(--depth)' }}>next 26 weeks</text>
    </svg>
  )
}

/* ------------------------------------------------------------------ cost distribution */
export function CostDistribution({ spot, plan, alpha }: { spot: number[]; plan: number[]; alpha: number }) {
  const W = 900, H = 260, m = { l: 20, r: 20, t: 20, b: 34 }
  const lo = Math.min(...spot, ...plan), hi = Math.max(...spot, ...plan)
  const x = scaleLinear().domain([lo, hi]).nice().range([m.l, W - m.r])
  const bins = bin().domain(x.domain() as [number, number]).thresholds(36)
  const bs = bins(spot), bp = bins(plan)
  const y = scaleLinear().domain([0, max([...bs, ...bp], (b) => b.length) ?? 1]).range([H - m.b, m.t])
  const tail = (arr: number[]) => { const s = [...arr].sort((a, b) => a - b); const t = s.slice(Math.floor(alpha * s.length)); return t.reduce((a, b) => a + b, 0) / t.length }
  const mean = (arr: number[]) => arr.reduce((a, b) => a + b, 0) / arr.length
  const marks: { v: number; label: string; c: string; left?: boolean }[] = [
    { v: mean(spot), label: 'all spot, expected', c: 'var(--ink-2)' },
    { v: mean(plan), label: 'NauPlan', c: 'var(--depth)', left: true },
    { v: tail(spot), label: 'all spot, worst 10%', c: 'var(--magenta)' },
  ]
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Programme cost across freight scenarios" style={{ width: '100%', height: 'auto' }}>
      {bs.map((b, i) => (
        <rect key={`s${i}`} x={x(b.x0!) + 0.5} width={Math.max(0, x(b.x1!) - x(b.x0!) - 1)} y={y(b.length)} height={H - m.b - y(b.length)}
          fill="var(--ink-3)" opacity={0.45} style={{ transformOrigin: `0 ${H - m.b}px`, animation: `grow .8s ease ${i * 12}ms both` }} />
      ))}
      {bp.map((b, i) => b.length > 0 && (
        <rect key={`p${i}`} x={x(b.x0!) + 0.5} width={Math.max(0, x(b.x1!) - x(b.x0!) - 1)} y={y(b.length)} height={H - m.b - y(b.length)}
          fill="var(--depth)" style={{ transformOrigin: `0 ${H - m.b}px`, animation: 'grow .8s ease .5s both' }} />
      ))}
      <style>{'@keyframes grow { from { transform: scaleY(0) } to { transform: scaleY(1) } }'}</style>
      {marks.map((mk) => (
        <g key={mk.label}>
          <line x1={x(mk.v)} x2={x(mk.v)} y1={m.t} y2={H - m.b} stroke={mk.c} strokeDasharray="4 3" />
          <text x={x(mk.v) + (mk.left ? -5 : 5)} y={m.t + 12} textAnchor={mk.left ? 'end' : 'start'} style={{ font: 'italic 13px var(--hydro)', fill: mk.c, paintOrder: 'stroke', stroke: '#fff', strokeWidth: 4 }}>{mk.label}</text>
        </g>
      ))}
      {x.ticks(8).map((t) => (
        <text key={t} x={x(t)} y={H - 12} textAnchor="middle" className="tick-label">${t}M</text>
      ))}
    </svg>
  )
}

/* ------------------------------------------------------------------ charter timeline */
export function CharterTimeline({ months, charters, coaByRoute }: {
  months: string[]; charters: TimeCharter[]; coaByRoute: { route: string; cls: string; tonnes: number; months: Set<string> }[]
}) {
  const rows = [
    ...charters.map((c) => ({ key: `tc-${c.vessel_class}-${c.start}-${c.months}`, kind: 'tc' as const, label: `${c.vessels} × ${shortClass(c.vessel_class)}`,
      note: c.hire_usd_day ? `fixed now, $${Math.round(c.hire_usd_day).toLocaleString('en-US')}/day` : 'fix at the market rate that month',
      from: months.indexOf(c.start), len: c.months })),
    ...coaByRoute.map((c) => {
      const idx = months.map((mm, i) => (c.months.has(mm) ? i : -1)).filter((i) => i >= 0)
      return { key: `coa-${c.route}`, kind: 'coa' as const, label: `COA ${c.route.split(' > ')[0].split(' (')[0]}`,
        note: `${Math.round(c.tonnes / 1000)} kt on ${shortClass(c.cls)}`, from: Math.min(...idx), len: Math.max(...idx) - Math.min(...idx) + 1 }
    }),
  ]
  const W = 900, rowH = 40, top = 30, left = 200
  const H = top + Math.max(1, rows.length) * rowH + 8
  const x = scaleBand().domain(months).range([left, W]).paddingInner(0.04)
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Charter timeline" style={{ width: '100%', height: 'auto' }}>
      {months.map((mm) => (
        <g key={mm}>
          <rect x={x(mm)} y={top - 4} width={x.bandwidth()} height={H - top} fill="var(--shoal)" opacity={0.35} />
          <text x={x(mm)! + x.bandwidth() / 2} y={18} textAnchor="middle" className="tick-label">{monthName(mm)}</text>
        </g>
      ))}
      {rows.length === 0 && <text x={left} y={top + 24} style={{ font: 'italic 15px var(--hydro)', fill: 'var(--ink-3)' }}>No contracts: every voyage is fixed spot.</text>}
      {rows.map((r, i) => {
        const y0 = top + i * rowH
        const x0 = x(months[r.from])!, x1 = x(months[r.from + r.len - 1])! + x.bandwidth()
        return (
          <g key={r.key}>
            <text x={0} y={y0 + 17} style={{ font: '800 16px var(--display)', letterSpacing: '0.03em', fill: 'var(--ink)', textTransform: 'uppercase' }}>{r.label}</text>
            <text x={0} y={y0 + 32} className="tick-label">{r.kind === 'tc' ? `${r.len}-month time charter` : 'contract of affreightment'}</text>
            <rect x={x0} y={y0 + 4} width={x1 - x0} height={rowH - 12} rx={5}
              fill={r.kind === 'tc' ? 'var(--depth)' : 'var(--land)'} stroke={r.kind === 'tc' ? 'none' : 'var(--land-edge)'}
              style={{ transformOrigin: `${x0}px 0`, animation: `grow-x .9s cubic-bezier(.3,.7,.2,1) ${i * 120}ms both` }} />
            <text x={x0 + 10} y={y0 + 23} style={{ font: '500 12px var(--mono)', fill: r.kind === 'tc' ? 'var(--paper)' : 'var(--ink)' }}>{r.note}</text>
          </g>
        )
      })}
      <style>{'@keyframes grow-x { from { transform: scaleX(0) } to { transform: scaleX(1) } }'}</style>
    </svg>
  )
}

/* ------------------------------------------------------------------ shipments by mode */
const MODES = [
  { key: 'time charter', fill: 'var(--depth)', label: 'Chartered fleet' },
  { key: 'COA', fill: 'var(--land)', label: 'COA' },
  { key: 'spot', fill: 'var(--ink-3)', label: 'Spot' },
] as const

export function ShipmentBars({ months, shipments }: { months: string[]; shipments: Shipment[] }) {
  const W = 900, H = 240, m = { l: 48, r: 10, t: 14, b: 30 }
  const byMonth = months.map((mm) => {
    const rows = shipments.filter((s) => s.month === mm)
    return { mm, ...Object.fromEntries(MODES.map((md) => [md.key, rows.filter((r) => r.mode === md.key).reduce((a, r) => a + r.tonnes, 0)])) } as Record<string, number> & { mm: string }
  })
  const total = Math.max(...byMonth.map((b) => MODES.reduce((a, md) => a + b[md.key], 0)))
  const x = scaleBand().domain(months).range([m.l, W - m.r]).padding(0.28)
  const y = scaleLinear().domain([0, total]).nice().range([H - m.b, m.t])
  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Tonnes shipped per month by contract type" style={{ width: '100%', height: 'auto' }}>
        {y.ticks(4).map((t) => (
          <g key={t} className="axis"><line x1={m.l} x2={W - m.r} y1={y(t)} y2={y(t)} stroke="var(--rule)" strokeWidth={0.6} /><text x={m.l - 6} y={y(t) + 4} textAnchor="end">{t / 1000}k</text></g>
        ))}
        {byMonth.map((b, i) => {
          let acc = 0
          return (
            <g key={b.mm} style={{ transformOrigin: `0 ${H - m.b}px`, animation: `grow .8s ease ${i * 80}ms both` }}>
              {MODES.map((md) => {
                const v = b[md.key]; const y1 = y(acc + v), y0 = y(acc); acc += v
                return v > 0 ? <rect key={md.key} x={x(b.mm)} width={x.bandwidth()} y={y1} height={y0 - y1} fill={md.fill} stroke="var(--paper)" strokeWidth={1} /> : null
              })}
              <text x={x(b.mm)! + x.bandwidth() / 2} y={H - 10} textAnchor="middle" className="tick-label">{monthName(b.mm)}</text>
            </g>
          )
        })}
        <style>{'@keyframes grow { from { transform: scaleY(0) } to { transform: scaleY(1) } }'}</style>
      </svg>
      <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--ink-2)' }}>
        {MODES.map((md) => <span key={md.key}><i style={{ display: 'inline-block', width: 10, height: 10, background: md.fill, border: '1px solid var(--land-edge)', marginRight: 6 }} />{md.label}</span>)}
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ fleet use */
export function FleetUse({ fleet }: { fleet: FleetRow[] }) {
  if (!fleet.length) return <p className="muted">No chartered ships in this plan.</p>
  return (
    <div className="stack" style={{ gap: 10 }}>
      {fleet.map((f) => {
        const tot = f.vessel_days
        const seg = [{ v: f.voyage_days, c: 'var(--depth)', l: 'carrying our cargo' }, { v: f.relet_days, c: 'var(--land)', l: 'relet to the market' }, { v: f.idle_days, c: 'var(--magenta)', l: 'idle' }]
        return (
          <div key={`${f.vessel_class}${f.month}`} style={{ display: 'grid', gridTemplateColumns: '92px 1fr 150px', gap: 10, alignItems: 'center' }}>
            <span className="mono" style={{ fontSize: 12 }}>{monthName(f.month)}</span>
            <div style={{ display: 'flex', height: 14, borderRadius: 4, overflow: 'hidden', background: 'var(--shoal)' }}>
              {seg.map((s) => s.v > 0.5 && <div key={s.l} title={`${Math.round(s.v)} vessel-days ${s.l}`} style={{ width: `${(s.v / tot) * 100}%`, background: s.c, border: s.c === 'var(--land)' ? '1px solid var(--land-edge)' : undefined }} />)}
            </div>
            <span className="mono" style={{ fontSize: 12, color: 'var(--ink-2)' }}>{f.vessels} ships · {Math.round(f.relet_days)} d relet</span>
          </div>
        )
      })}
      <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--ink-2)' }}>
        <span><i style={{ display: 'inline-block', width: 10, height: 10, background: 'var(--depth)', marginRight: 6 }} />carrying our cargo</span>
        <span><i style={{ display: 'inline-block', width: 10, height: 10, background: 'var(--land)', border: '1px solid var(--land-edge)', marginRight: 6 }} />relet to the market</span>
        <span><i style={{ display: 'inline-block', width: 10, height: 10, background: 'var(--magenta)', marginRight: 6 }} />idle</span>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ sea state sparkline */
export function WaveSpark({ s }: { s: SeaState }) {
  const W = 220, H = 56
  const x = scaleLinear().domain([0, s.history_m.length - 1]).range([2, W - 2])
  const y = scaleLinear().domain([0, Math.max(s.p90_month_m, ...s.history_m) * 1.15]).range([H - 2, 4])
  const d = line<number>().x((_, i) => x(i)).y((v) => y(v)).curve(curveMonotoneX)(s.history_m) ?? ''
  const high = s.wave_m > s.p90_month_m
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto' }} aria-hidden>
      <path d={`${d} L${W - 2},${H} L2,${H} Z`} fill="var(--shoal)" />
      <path d={d} fill="none" stroke={high ? 'var(--magenta)' : 'var(--depth)'} strokeWidth={1.5} />
      <line x1={0} x2={W} y1={y(s.p90_month_m)} y2={y(s.p90_month_m)} stroke="var(--magenta)" strokeDasharray="3 3" strokeWidth={1} />
      <circle cx={x(s.history_m.length - 1)} cy={y(s.wave_m)} r={3.5} fill={high ? 'var(--magenta)' : 'var(--depth)'} />
    </svg>
  )
}
