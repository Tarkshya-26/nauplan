import { useEffect, useRef, useState } from 'react'

export const usd = (v: number, digits = 0) => `$${v.toLocaleString('en-US', { maximumFractionDigits: digits, minimumFractionDigits: digits })}`
export const usdM = (v: number) => `$${v.toFixed(1)}M`
export const tonnes = (v: number) => (v >= 1e6 ? `${(v / 1e6).toFixed(2)} Mt` : v >= 1e3 ? `${Math.round(v / 1e3).toLocaleString('en-US')} kt` : `${Math.round(v)} t`)
export const pct = (v: number, digits = 0) => `${(v * 100).toFixed(digits)}%`
export const shortClass = (c: string) => ({ 'Panamax/Kamsarmax': 'Panamax', 'Supramax/Ultramax': 'Supramax' } as Record<string, string>)[c] ?? c
export const monthName = (ym: string) => new Date(`${ym}-01T00:00:00`).toLocaleDateString('en-GB', { month: 'short', year: '2-digit' })
export const dateLong = (d: string) => new Date(`${d}T00:00:00`).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

export const reducedMotion = () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

/** Animates a number from its previous value to `target`. */
export function useCountUp(target: number, ms = 900): number {
  const [value, setValue] = useState(target)
  const from = useRef(target)
  useEffect(() => {
    if (reducedMotion() || document.hidden) { setValue(target); from.current = target; return }
    const start = performance.now(), a = from.current
    let raf = 0
    const step = (t: number) => {
      const k = Math.min(1, (t - start) / ms)
      const e = 1 - Math.pow(1 - k, 3)
      setValue(a + (target - a) * e)
      if (k < 1) raf = requestAnimationFrame(step)
      else from.current = target
    }
    raf = requestAnimationFrame(step)
    // animation frames pause in background tabs; always land on the final value
    const done = setTimeout(() => { cancelAnimationFrame(raf); setValue(target); from.current = target }, ms + 150)
    return () => { cancelAnimationFrame(raf); clearTimeout(done) }
  }, [target, ms])
  return value
}
