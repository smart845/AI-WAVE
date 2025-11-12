import type { Bar } from './binance'

export function ema(values:number[], p:number){
  const out:number[] = []; const k = 2/(p+1); let v = values[0]; out.push(v);
  for(let i=1;i<values.length;i++){ v = values[i]*k + v*(1-k); out.push(v); }
  return out
}
export function emaSeries(values:number[], p:number, bars:Bar[]){
  const e = ema(values, p)
  return e.map((v,i)=> ({ time: Math.floor(bars[i].t/1000), value: v }))
}
export function rsi(values:number[], period=14){
  const out = new Array(values.length).fill(null) as (number|null)[]
  let gains=0, losses=0
  for(let i=1;i<=period;i++){ const d=values[i]-values[i-1]; if(d>=0) gains+=d; else losses+=-d }
  let avgGain=gains/period, avgLoss=losses/period
  out[period] = 100 - (100/(1+(avgGain/(avgLoss||1e-9))))
  for(let i=period+1;i<values.length;i++){
    const d=values[i]-values[i-1]; const g=Math.max(d,0), l=Math.max(-d,0)
    avgGain=(avgGain*(period-1)+g)/period; avgLoss=(avgLoss*(period-1)+l)/period
    out[i] = 100 - (100/(1+(avgGain/(avgLoss||1e-9))))
  }
  return out
}
export function rsiSeriesCalc(values:number[], period:number, bars:Bar[]){
  const a = rsi(values, period)
  return a.map((v,i)=> v==null? { time: Math.floor(bars[i].t/1000), value: 50 } : { time: Math.floor(bars[i].t/1000), value: v })
}
export function vwap(bars:Bar[]){
  let cumPV=0, cumV=0; const out:number[]=[]
  for(const k of bars){ const tp=(k.h+k.l+k.c)/3; cumPV += tp*k.v; cumV += k.v; out.push(cumPV/Math.max(cumV,1e-9)) }
  return out
}
export function vwapSeries(bars:Bar[]){
  const v = vwap(bars)
  return v.map((val,i)=> ({ time: Math.floor(bars[i].t/1000), value: val }))
}
