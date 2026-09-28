import { geoGraticule10, geoMercator, geoPath } from 'd3-geo'
import type { Feature, FeatureCollection, Geometry } from 'geojson'
import { useMemo } from 'react'
import { feature } from 'topojson-client'
import type { Topology } from 'topojson-specification'
import land50 from 'world-atlas/land-50m.json'
import type { Port } from '../api'
import { reducedMotion } from '../format'

const LAND = feature(land50 as unknown as Topology, (land50 as unknown as Topology).objects.land) as unknown as FeatureCollection

export type MapTrack = { id: string; points: [number, number][]; kind: 'main' | 'context' }

const SEAS: { name: string; at: [number, number]; hero?: boolean }[] = [
  { name: 'Indian Ocean', at: [78, -18], hero: true },
  { name: 'Bay of Bengal', at: [89, 13] },
  { name: 'Arabian Sea', at: [64, 14] },
  { name: 'South China Sea', at: [113, 13] },
  { name: 'Coral Sea', at: [156, -15], hero: true },
  { name: 'Atlantic Ocean', at: [-40, 24], hero: true },
  { name: 'Mozambique Channel', at: [41, -19] },
  { name: 'Mediterranean', at: [18, 35], hero: true },
]

type Props = {
  tracks: MapTrack[]
  ports: Port[]
  width?: number
  height?: number
  mode?: 'hero' | 'inset'
  focusPorts?: string[]
  title?: string
}

export default function ChartMap({ tracks, ports, width = 1600, height = 720, mode = 'hero', focusPorts = [], title }: Props) {
  const motion = !reducedMotion()
  const { path, projection, ticks } = useMemo(() => {
    const pts: [number, number][] = tracks.flatMap((t) => t.points)
    const focus = mode === 'hero' ? ports : ports.filter((p) => focusPorts.includes(p.port_id))
    focus.forEach((p) => pts.push([p.lon, p.lat]))
    const fc: Feature<Geometry> = { type: 'Feature', properties: {}, geometry: { type: 'MultiPoint', coordinates: pts } }
    const pad = mode === 'hero' ? 56 : 44
    const projection = geoMercator().fitExtent([[pad, pad], [width - pad, height - pad]], fc)
    const path = geoPath(projection)
    const [[x0, y0], [x1, y1]] = [projection.invert!([0, 0])!, projection.invert!([width, height])!]
    const step = mode === 'hero' ? 10 : 5
    const lon: number[] = [], lat: number[] = []
    for (let v = Math.ceil(x0 / step) * step; v <= x1; v += step) lon.push(v)
    for (let v = Math.ceil(y1 / step) * step; v <= y0; v += step) lat.push(v)
    return { path, projection, ticks: { lon, lat } }
  }, [tracks, ports, width, height, mode, focusPorts])

  const P = (lon: number, lat: number) => projection([lon, lat]) as [number, number]
  const eastCoast = ports.filter((p) => p.role === 'discharge').sort((a, b) => b.lat - a.lat)
  const loads = ports.filter((p) => p.role === 'load')
  const shown = mode === 'hero' ? ports : ports.filter((p) => focusPorts.includes(p.port_id))

  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title ?? 'Chart of voyage routes'} style={{ width: '100%', height: 'auto' }}>
      <defs>
        <clipPath id={`frame-${mode}`}><rect x={0} y={0} width={width} height={height} /></clipPath>
        <style>{`
          @keyframes draw { from { stroke-dashoffset: 1 } to { stroke-dashoffset: 0 } }
          .trk-main { stroke-dasharray: 1; stroke-dashoffset: ${motion ? 1 : 0}; animation: draw 2.4s cubic-bezier(.6,.1,.2,1) forwards; }
        `}</style>
      </defs>
      <rect width={width} height={height} fill="var(--paper)" />
      <g clipPath={`url(#frame-${mode})`}>
        <path d={path(geoGraticule10()) ?? ''} fill="none" stroke="var(--rule)" strokeWidth={0.6} />
        {/* coastal shoal band, then land */}
        <path d={path(LAND) ?? ''} fill="var(--shoal)" stroke="var(--shoal-2)" strokeWidth={mode === 'hero' ? 5 : 10} strokeLinejoin="round" opacity={0.9} />
        <path d={path(LAND) ?? ''} fill="var(--land)" stroke="var(--land-edge)" strokeWidth={0.7} />
        {SEAS.filter((s) => mode === 'hero' || !s.hero).map((s) => {
          const [x, y] = P(...s.at)
          return x > 0 && x < width && y > 0 && y < height ? (
            <text key={s.name} x={x} y={y} className="hydro-label" textAnchor="middle" opacity={0.85}
              fontSize={mode === 'hero' ? (s.hero ? 22 : 16) : 14}>{s.name}</text>
          ) : null
        })}
        {tracks.filter((t) => t.kind === 'context').map((t) => (
          <path key={t.id} d={path({ type: 'LineString', coordinates: t.points }) ?? ''} fill="none"
            stroke="var(--depth-2)" strokeWidth={1} strokeDasharray="3 4" opacity={0.45} />
        ))}
        {tracks.filter((t) => t.kind === 'main').map((t, i) => (
          <path key={t.id} id={`trk-${mode}-${i}`} className="trk-main" pathLength={1}
            style={{ animationDelay: `${0.3 + i * 0.35}s` }}
            d={path({ type: 'LineString', coordinates: t.points }) ?? ''} fill="none"
            stroke="var(--depth)" strokeWidth={mode === 'hero' ? 2.4 : 3} strokeLinecap="round" />
        ))}
        {motion && tracks.filter((t) => t.kind === 'main').map((t, i) => (
          <g key={`ship-${t.id}`}>
            <g>
              <circle r={mode === 'hero' ? 5 : 6} fill="var(--ink)" stroke="var(--paper)" strokeWidth={2} />
              <animateMotion dur={`${16 + i * 3}s`} begin={`${2.8 + i * 0.35}s`} repeatCount="indefinite" rotate="auto" fill="freeze">
                <mpath href={`#trk-${mode}-${i}`} />
              </animateMotion>
            </g>
          </g>
        ))}
        {(mode === 'hero' ? loads : shown).map((p) => {
          const [x, y] = P(p.lon, p.lat)
          const left = x > 170 && (p.lon < 20 || (p.lon > 100 && p.lon < 125))
          return (
            <g key={p.port_id}>
              <circle cx={x} cy={y} r={4} fill={p.role === 'load' ? 'var(--ink)' : 'var(--magenta)'} stroke="var(--paper)" strokeWidth={1.5} />
              <text x={x + (left ? -8 : 8)} y={y + 4} textAnchor={left ? 'end' : 'start'} className={`port-label ${p.role}`}
                fontSize={mode === 'hero' ? 12 : 14}>{p.name}</text>
            </g>
          )
        })}
        {mode === 'hero' && (() => {
          // Callout list for the seven East Coast ports, which sit too close together to label in place.
          const anchor = P(99, 22)
          return (
            <g>
              {eastCoast.map((p, i) => {
                const [x, y] = P(p.lon, p.lat)
                const ly = anchor[1] - 70 + i * 17
                return (
                  <g key={p.port_id}>
                    <path d={`M${x},${y} L${anchor[0] - 8},${ly}`} stroke="var(--magenta)" strokeWidth={0.7} opacity={0.6} fill="none" />
                    <circle cx={x} cy={y} r={3.5} fill="var(--magenta)" stroke="var(--paper)" strokeWidth={1.2} />
                    <text x={anchor[0]} y={ly + 4} className="port-label" fill="var(--magenta)" style={{ fill: 'var(--magenta)' }}>{p.name}</text>
                  </g>
                )
              })}
            </g>
          )
        })()}
      </g>
      {/* neatline with an alternating degree scale, as on a printed chart */}
      <rect x={0.5} y={0.5} width={width - 1} height={height - 1} fill="none" stroke="var(--ink)" strokeWidth={1.5} />
      {ticks.lon.map((v, i) => {
        const x = P(v, 0)[0], x2 = P(v + (mode === 'hero' ? 10 : 5), 0)[0]
        return (
          <g key={`lon${v}`}>
            {i % 2 === 0 && <rect x={x} y={0} width={Math.max(0, Math.min(x2, width) - x)} height={6} fill="var(--ink)" />}
            {i % 2 === 0 && <rect x={x} y={height - 6} width={Math.max(0, Math.min(x2, width) - x)} height={6} fill="var(--ink)" />}
            <text x={x + 3} y={20} className="tick-label">{Math.abs(v)}°{v < 0 ? 'W' : 'E'}</text>
          </g>
        )
      })}
      {ticks.lat.map((v, i) => {
        const y = P(0, v)[1], y2 = P(0, v + (mode === 'hero' ? 10 : 5))[1]
        return (
          <g key={`lat${v}`}>
            {i % 2 === 0 && <rect x={0} y={Math.max(0, y2)} width={6} height={Math.max(0, y - Math.max(0, y2))} fill="var(--ink)" />}
            {i % 2 === 0 && <rect x={width - 6} y={Math.max(0, y2)} width={6} height={Math.max(0, y - Math.max(0, y2))} fill="var(--ink)" />}
            <text x={10} y={y - 3} className="tick-label">{Math.abs(v)}°{v < 0 ? 'S' : 'N'}</text>
          </g>
        )
      })}
    </svg>
  )
}
