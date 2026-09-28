export type Port = { port_id: string; name: string; country: string; role: 'load' | 'discharge'; operation: string; lat: number; lon: number }
export type Limit = {
  port: string; berth: string; draft_m: number | null; draft_basis: string; loa_m: number | null; beam_m: number | null
  max_dwt_t: number | null; min_dwt_t: number | null; transloading: boolean
}
export type Vessel = { vessel_class: string; baltic_standard: string; dwt_t: number; draft_ssw_m: number; loa_m: number; beam_m: number; tpc_t_per_cm: number }
export type Route = { origin: string; destination: string; cargo?: string; tonnes_per_month: number[] }
export type Quantiles = { p10: number; p50: number; p90: number }
export type Forecast = {
  as_of: string; series: string; last_price: number; weekly_volatility: number; weekly_volatility_pct_rank: number
  horizons: Record<string, { selected: string } & Record<string, Quantiles | string>>
}
export type BacktestRow = { period: string; model: string; horizon: number; coverage_80: number; pinball_vs_rw: number; mae_vs_rw: number; direction_hit: number | null }
export type SeaState = { port: string; date: string; wave_m: number; max_30d_m: number; p90_month_m: number; history_m: number[] }
export type Overview = {
  market: { note: string; hire_usd_day: Record<string, number> }
  forecast: Forecast
  history: { date: string; price: number }[]
  backtest: BacktestRow[]
  ports: Port[]
  limits: Limit[]
  vessels: Vessel[]
  programme: { synthetic: boolean; start_month: string; months: number; routes: Route[] }
  risk: { cvar_alpha: number; risk_weight: number; scenarios: number }
  contracts: { period_premium: number }
  placeholders: string[]
  sea_state: SeaState[]
}
export type Track = { origin: string; destination: string; kind: 'main' | 'context'; points: [number, number][] }
export type FitOption = {
  vessel_class: string; discharge_at: string; feasible: boolean; cargo_t: number; laden_draft_m: number
  route: string | null; distance_nm: number | null; round_trip_days: number | null; spot_usd_per_t: number | null
  why: string; data_gaps: string
}
export type Fit = { options: FitOption[]; limits: Record<string, Limit>; track: [number, number][] | null }
export type Summary = { plan: string; expected_cost_usd_m: number; cvar_usd_m: number; p90_usd_m: number; std_usd_m: number; expected_usd_per_t: number }
export type TimeCharter = { vessel_class: string; vessels: number; start: string; months: number; hire: string; hire_usd_day: number | null }
export type Coa = { route: string; vessel_class: string; months: number; month: string; tonnes: number; usd_per_t: number }
export type Shipment = { month: string; route: string; vessel_class: string; discharge_at: string; mode: 'spot' | 'time charter' | 'COA'; tonnes: number }
export type FleetRow = { vessel_class: string; month: string; vessels: number; vessel_days: number; voyage_days: number; relet_days: number; idle_days: number }
export type PlanResult = {
  strategies: Summary[]; costs_usd_m: { spot: number[]; plan: number[] }
  time_charters: TimeCharter[]; coa: Coa[]; shipments: Shipment[]; fleet: FleetRow[]; months: string[]; alpha: number
}
export type PlanRequest = { start_month: string; routes: Route[]; risk_weight: number; period_premium: number; scenarios?: number }

async function call<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, body === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    const msg = typeof detail.detail === 'string' ? detail.detail : `Request failed (${res.status})`
    throw new Error(msg)
  }
  return res.json() as Promise<T>
}

export const api = {
  overview: () => call<Overview>('/api/overview'),
  tracks: () => call<Track[]>('/api/tracks'),
  fit: (origin: string, destination: string) => call<Fit>('/api/fit', { origin, destination }),
  plan: (req: PlanRequest) => call<PlanResult>('/api/plan', req),
}
