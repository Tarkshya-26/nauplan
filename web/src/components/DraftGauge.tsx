import { useEffect, useState } from 'react'
import type { FitOption, Limit, Vessel } from '../api'
import { reducedMotion, shortClass } from '../format'

type Props = {
  vessels: Vessel[]
  options: FitOption[] // one row per vessel class (the option shown)
  limits: { label: string; limit: Limit }[]
}

const W = 1000, H = 420
const SURFACE = 92 // y of the sea surface
const SCALE = 12 // px per metre of draft (vertical exaggeration)
const SEA_DEPTH_M = 20 // metres of sea drawn below the surface
const LABEL_Y = SURFACE + SEA_DEPTH_M * SCALE + 30
const FREEBOARD = 44

/** Side profile of a bulk carrier, origin at the design waterline, bow to the right. */
function hullPath(L: number, D: number) {
  const F = FREEBOARD
  return [
    `M0,${-F + 4}`, `L${L * 0.86},${-F + 4}`, `L${L * 0.9},${-F - 4}`, `L${L},${-F - 6}`,
    `L${L - 16},${D - 6}`, `Q${L - 20},${D} ${L - 34},${D}`, `L${14},${D}`, `Q2,${D} 2,${D - 16}`, 'Z',
  ].join(' ')
}

export default function DraftGauge({ vessels, options, limits }: Props) {
  const [settled, setSettled] = useState(reducedMotion())
  useEffect(() => {
    if (reducedMotion()) return
    setSettled(false)
    const t = setTimeout(() => setSettled(true), 350)
    return () => clearTimeout(t)
  }, [options])

  const cols = vessels.length
  const colW = W / cols
  const maxLoa = Math.max(...vessels.map((v) => v.loa_m))
  const drafted = limits.filter((l) => l.limit.draft_m !== null)
  const binding = drafted.length ? Math.min(...drafted.map((l) => l.limit.draft_m!)) : null

  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" style={{ width: '100%', height: 'auto' }}
      aria-label="Draft gauge: each vessel class at its laden draft against the port draft limits">
      <defs>
        <pattern id="shutout" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="7" height="7" fill="var(--magenta-soft)" />
          <line x1="0" y1="0" x2="0" y2="7" stroke="var(--magenta)" strokeWidth="2" />
        </pattern>
        <linearGradient id="sea" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="var(--shoal)" stopOpacity="0.55" />
          <stop offset="1" stopColor="var(--shoal-2)" stopOpacity="0.85" />
        </linearGradient>
        <style>{`
          @keyframes swell { from { transform: translateX(0) } to { transform: translateX(-80px) } }
          .swell { animation: swell 6s linear infinite; }
          .hull { transition: transform 1.3s cubic-bezier(.3,.7,.2,1); }
        `}</style>
      </defs>

      {/* draft scale (metres below the surface) */}
      {[0, 4, 8, 12, 16].map((m) => (
        <g key={m}>
          <line x1={0} x2={W} y1={SURFACE + m * SCALE} y2={SURFACE + m * SCALE} stroke="var(--rule)" strokeWidth={m === 0 ? 0 : 0.7} />
          {m > 0 && <text x={4} y={SURFACE + m * SCALE - 4} className="tick-label">{m} m</text>}
        </g>
      ))}

      {vessels.map((v, i) => {
        const opt = options.find((o) => o.vessel_class === v.vessel_class)
        const L = (v.loa_m / maxLoa) * (colW - 56)
        const D = v.draft_ssw_m * SCALE
        const x = i * colW + (colW - L) / 2 + 8
        const feasible = opt?.feasible ?? false
        const laden = opt ? Math.min(opt.laden_draft_m, v.draft_ssw_m) : v.draft_ssw_m
        const lift = settled ? (v.draft_ssw_m - laden) * SCALE : 0
        const cut = v.draft_ssw_m - laden
        const shutT = cut * 100 * v.tpc_t_per_cm
        const clip = `wl-${i}`
        return (
          <g key={v.vessel_class} opacity={feasible ? 1 : 0.35}>
            <clipPath id={clip}><rect x={-10} y={0} width={L + 20} height={D + 10} /></clipPath>
            {/* shut-out cargo: the draft the ship is not allowed to use */}
            {feasible && cut > 0.02 && (
              <rect x={x + 12} y={SURFACE + laden * SCALE} width={L - 40} height={cut * SCALE} fill="url(#shutout)" rx={2}
                style={{ opacity: settled ? 1 : 0, transition: 'opacity .6s ease 1s' }} />
            )}
            <g className="hull" style={{ transform: `translate(${x}px, ${SURFACE - lift}px)` }}>
              <path d={hullPath(L, D)} fill="var(--ink)" />
              <path d={hullPath(L, D)} fill="var(--hull-red)" clipPath={`url(#${clip})`} />
              <line x1={2} x2={L - 2} y1={0} y2={0} stroke="var(--paper)" strokeWidth={1.2} opacity={0.7} />
              {/* draft marks on the bow, metres above the keel */}
              {Array.from({ length: Math.floor(v.draft_ssw_m / 2) }, (_, k) => (k + 1) * 2).map((m) => (
                <text key={m} x={L - 26 - (m / v.draft_ssw_m) * 10} y={D - m * SCALE + 4} textAnchor="end"
                  style={{ font: '700 9px var(--display)', fill: 'var(--paper)' }}>{m}M</text>
              ))}
              {/* superstructure aft */}
              <rect x={8} y={-FREEBOARD - 26} width={Math.max(18, L * 0.1)} height={31} fill="var(--ink)" />
              <rect x={12} y={-FREEBOARD - 20} width={Math.max(10, L * 0.1) - 8} height={4} fill="var(--shoal-2)" />
            </g>
            <text x={i * colW + colW / 2} y={LABEL_Y} textAnchor="middle" style={{ font: '800 20px var(--display)', letterSpacing: '0.04em', fill: 'var(--ink)', textTransform: 'uppercase' }}>
              {shortClass(v.vessel_class)}
            </text>
            <text x={i * colW + colW / 2} y={LABEL_Y + 18} textAnchor="middle" className="tick-label">
              {(v.dwt_t / 1000).toFixed(1)}k dwt · design {v.draft_ssw_m.toFixed(1)} m
            </text>
            <text x={i * colW + colW / 2} y={LABEL_Y + 38} textAnchor="middle"
              style={{ font: `${feasible ? '500' : 'italic 400'} 12px ${feasible ? 'var(--mono)' : 'var(--hydro)'}`, fill: feasible ? (cut > 0.02 ? 'var(--magenta)' : 'var(--depth)') : 'var(--magenta)' }}>
              {!opt ? '' : !feasible ? 'Cannot call' : cut > 0.02 ? `sails at ${laden.toFixed(1)} m, ${Math.round(shutT / 1000)}k t shut out` : 'loads to full draft'}
            </text>
          </g>
        )
      })}

      {/* sea, drawn over the hulls so the underwater body reads as submerged */}
      <rect x={0} y={SURFACE} width={W} height={SEA_DEPTH_M * SCALE} fill="url(#sea)" pointerEvents="none" />
      <g className="swell" pointerEvents="none">
        <path d={`M-80,${SURFACE} ${Array.from({ length: 28 }, () => `q20,-5 40,0 t40,0`).join(' ')}`} fill="none" stroke="var(--depth)" strokeWidth={1.4} opacity={0.6} />
      </g>

      {/* port draft limits */}
      {[...drafted].sort((a, b) => a.limit.draft_m! - b.limit.draft_m!).map((l, k) => {
        const y = SURFACE + l.limit.draft_m! * SCALE
        const isBinding = l.limit.draft_m === binding
        const below = k % 2 === 1
        return (
          <g key={l.label}>
            <line x1={0} x2={W} y1={y} y2={y} stroke="var(--magenta)" strokeWidth={isBinding ? 2 : 1.2} strokeDasharray={isBinding ? '0' : '6 5'} />
            <text x={below ? 40 : W - 6} y={below ? y + 16 : y - 6} textAnchor={below ? 'start' : 'end'}
              style={{ font: 'italic 500 14px var(--hydro)', fill: 'var(--magenta)', paintOrder: 'stroke', stroke: 'var(--shoal)', strokeWidth: 3 }}>
              {l.label} limit {l.limit.draft_m!.toFixed(2)} m{isBinding ? ' (binding)' : ''}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
