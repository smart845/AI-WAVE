import React, { useEffect, useRef, useState } from 'react'
import { createChart, ColorType, ISeriesApi } from 'lightweight-charts'
import { fetchKlines, streamSubscribe } from '../utils/binance'
import { emaSeries, rsiSeriesCalc, vwapSeries } from '../utils/indicators'
import { loadWL, saveWL, loadActive, saveActive, loadTF, saveTF, loadSettings, saveSettings } from '../utils/storage'
import SignalPopup from './SignalPopup'
import SettingsModal, { Settings } from './SettingsModal'
import Logo from './Logo'

type Bar = { t:number,o:number,h:number,l:number,c:number,v:number }
const TFs = ['1m','3m','5m','15m','1h'] as const
type TF = typeof TFs[number]

export default function App(){
  const [symbols, setSymbols] = useState<string[]>(()=>loadWL())
  const [active, setActive] = useState<string>(()=> loadActive() || (loadWL()[0] ?? 'BTCUSDT'))
  const [tf, setTf] = useState<TF>(()=> (loadTF() as TF) || '1m')
  const [data, setData] = useState<Record<string, Bar[]>>({})
  const [status, setStatus] = useState('WS: —')
  const [pulse, setPulse] = useState('MIXED')
  const [signalText, setSignalText] = useState('AI SIGNAL: waiting…')
  const [popupMsg, setPopupMsg] = useState<string>('')
  const [showPopup, setShowPopup] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [settings, setSettings] = useState<Settings>(loadSettings())

  // charts
  const chartRef = useRef<HTMLDivElement>(null)
  const rsiRef = useRef<HTMLDivElement>(null)
  const chartApi = useRef<ReturnType<typeof createChart> | null>(null)
  const rsiApi = useRef<ReturnType<typeof createChart> | null>(null)
  const seriesC = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const seriesV = useRef<ISeriesApi<'Histogram'> | null>(null)
  const ema9 = useRef<ISeriesApi<'Line'> | null>(null)
  const ema21 = useRef<ISeriesApi<'Line'> | null>(null)
  const ema50 = useRef<ISeriesApi<'Line'> | null>(null)
  const vwap = useRef<ISeriesApi<'Line'> | null>(null)
  const rsiS = useRef<ISeriesApi<'Line'> | null>(null)

  // init charts
  useEffect(()=>{
    if (!chartRef.current || chartApi.current) return
    const main = createChart(chartRef.current, {
      layout: { background: { type: ColorType.Solid, color: '#0c0e12' }, textColor: '#cfd6e4' },
      grid: { vertLines: { color: '#1a1c24' }, horzLines: { color: '#1a1c24' } },
      rightPriceScale: { borderColor: '#1d2230' }, timeScale: { borderColor: '#1d2230', timeVisible: true }
    })
    const rsi = createChart(rsiRef.current!, {
      layout: { background: { type: ColorType.Solid, color: '#0c0e12' }, textColor: '#cfd6e4' },
      grid: { vertLines: { color: '#1a1c24' }, horzLines: { color: '#1a1c24' } },
      rightPriceScale: { borderColor: '#1d2230' }, timeScale: { borderColor: '#1d2230', timeVisible: true }
    })
    seriesC.current = main.addCandlestickSeries({ upColor:'#18c964', downColor:'#ff4d4f', wickUpColor:'#18c964', wickDownColor:'#ff4d4f', borderVisible:false })
    seriesV.current = main.addHistogramSeries({ priceScaleId:'', priceFormat:{type:'volume'}, overlay:true, scaleMargins:{ top:0.85, bottom:0 }, color:'#2a3544' })
    ema9.current  = main.addLineSeries({ color:'#77e0ae', lineWidth:1 })
    ema21.current = main.addLineSeries({ color:'#3aa0ff', lineWidth:1 })
    ema50.current = main.addLineSeries({ color:'#f0b90b', lineWidth:1 })
    vwap.current  = main.addLineSeries({ color:'#c77dff', lineWidth:1 })
    rsiS.current  = rsi.addLineSeries({ color:'#9aa4b2', lineWidth:1.5 })
    chartApi.current = main; rsiApi.current = rsi

    main.timeScale().subscribeVisibleTimeRangeChange((tr)=> rsi.timeScale().setVisibleRange(tr))
    rsi.timeScale().subscribeVisibleTimeRangeChange((tr)=> main.timeScale().setVisibleRange(tr))
    const ro1 = new ResizeObserver(()=> main.applyOptions({})); ro1.observe(chartRef.current)
    const ro2 = new ResizeObserver(()=> rsi.applyOptions({})); ro2.observe(rsiRef.current!)
  }, [])

  // bootstrap data + ws
  useEffect(()=>{
    let alive = true
    ;(async ()=>{
      const list = symbols.length ? symbols : ['BTCUSDT']
      for (const s of list) { fetchKlines(s, tf).then(b=> alive && setData(d=>({...d, [s]:b}))) }
    })()
    const unsub = streamSubscribe(symbols, tf, (evt)=>{
      if (evt.type==='status') setStatus(evt.payload)
      if (evt.type==='kline'){
        setData(prev => {
          const arr = prev[evt.symbol] ? [...prev[evt.symbol]] : []
          const bar = evt.bar
          if (arr.length && arr[arr.length-1].t === bar.t) arr[arr.length-1] = bar; else arr.push(bar)
          if (arr.length > 600) arr.shift()
          return { ...prev, [evt.symbol]: arr }
        })
      }
    })
    return ()=> unsub()
  }, [symbols, tf])

  // update chart
  useEffect(()=>{
    const arr = data[active]; if (!arr || !seriesC.current) return
    seriesC.current.setData(arr.map(k=>({ time: Math.floor(k.t/1000), open:k.o, high:k.h, low:k.l, close:k.c })))
    seriesV.current?.setData(arr.map(k=>({ time: Math.floor(k.t/1000), value:k.v, color: k.c>=k.o? '#1e8b5f':'#8b2f33' })))
    const closes = arr.map(k=>k.c)
    ema9.current?.setData(emaSeries(closes, 9, arr))
    ema21.current?.setData(emaSeries(closes, 21, arr))
    ema50.current?.setData(emaSeries(closes, 50, arr))
    vwap.current?.setData(vwapSeries(arr))
    rsiS.current?.setData(rsiSeriesCalc(closes, 14, arr))
    computePulse(); runAISignal(active)
  }, [active, data])

  function computePulse(){
    const vols = symbols.map(s=>{
      const arr = data[s]; if(!arr?.length) return 0
      const k = arr[arr.length-1]; return (k.h-k.l)/Math.max(k.c,1e-9)
    })
    const m = vols.reduce((a,b)=>a+b,0) / Math.max(vols.length,1)
    if (m > 0.004) setPulse('HIGH VOL')
    else if (m < 0.0015) setPulse('LOW VOL')
    else setPulse('MIXED')
  }
  function runAISignal(sym:string){
    const arr = data[sym]; if(!arr || arr.length<25) return
    const ema = (p:number)=>{ let k=2/(p+1), v=arr[0].c; for(let i=1;i<arr.length;i++) v = arr[i].c*k + v*(1-k); return v; }
    const e9=ema(9), e21=ema(21), slope=e9/e21 - 1; const last = arr[arr.length-1]; const hl=(last.h-last.l)/Math.max(last.c,1e-9)
    let side:'LONG'|'SHORT'|'FLAT'='FLAT'; let conf=0.5
    if(slope>0.0008 && hl>0.0012){ side='LONG'; conf=Math.min(0.99, 0.5 + slope*120 + hl*30) }
    if(slope<-0.0008 && hl>0.0012){ side='SHORT'; conf=Math.min(0.99, 0.5 + (-slope)*120 + hl*30) }
    const msg = `AI SIGNAL: ${sym} → ${side} (${Math.round(conf*100)}%)`
    setSignalText(msg); setPopupMsg(msg); setShowPopup(true); setTimeout(()=>setShowPopup(false), 2600)
  }

  // controls
  function zoom(delta:number){
    const ts = chartApi.current?.timeScale(); if(!ts) return
    const range = ts.getVisibleLogicalRange(); if(!range) return
    ts.setVisibleLogicalRange({ from: range.from + delta, to: range.to - delta })
  }
  function scroll(offset:number){
    const ts = chartApi.current?.timeScale(); if(!ts) return
    ts.scrollToPosition(offset, false)
  }

  // hotkeys
  useEffect(()=>{
    const onKey = (e:KeyboardEvent)=>{
      if ((e.target as HTMLElement).tagName === 'INPUT') return
      if (e.key==='+' || e.key==='=') zoom(-10)
      if (e.key==='-') zoom(10)
      if (e.key==='ArrowLeft') scroll(-30)
      if (e.key==='ArrowRight') scroll(30)
      if (e.key.toLowerCase()==='r') chartApi.current?.timeScale().fitContent()
      if (e.key==='End') chartApi.current?.timeScale().scrollToRealTime()
    }
    window.addEventListener('keydown', onKey)
    return ()=> window.removeEventListener('keydown', onKey)
  }, [])

  // handlers
  function onAddSymbol(v:string){
    const sym = v.toUpperCase().trim()
    if (!/^[A-Z0-9]{5,15}$/.test(sym)) return
    if (symbols.includes(sym)) return
    const next = [...symbols, sym]; setSymbols(next); saveWL(next)
    fetchKlines(sym, tf).then(b=> setData(d=>({...d, [sym]:b})))
  }
  function onRemoveSymbol(sym:string){
    const next = symbols.filter(s=> s!==sym); setSymbols(next); saveWL(next)
    if (active===sym){ const a = next[0] ?? 'BTCUSDT'; setActive(a); saveActive(a) }
  }
  function onActive(sym:string){ setActive(sym); saveActive(sym) }
  function onTF(newTf:TF){ if (tf===newTf) return; setTf(newTf); saveTF(newTf) }

  // Telegram bridge (optional)
  useEffect(()=>{
    if (!settings.tgToken) return
    const id = setInterval(async ()=>{
      try{
        const resp = await fetch(`https://api.telegram.org/bot${settings.tgToken}/getUpdates`)
        const j = await resp.json()
        if (!j.ok) return
        j.result.forEach((u:any)=>{
          const text = u.message?.text || ''
          const m = text.match(/\b[A-Z]{3,}USDT\b/g) || []
          m.forEach((s:string)=>{ if (!symbols.includes(s)) { onAddSymbol(s); setPopupMsg(`⚡️ ТГ сигнал: ${s}`); setShowPopup(true); setTimeout(()=>setShowPopup(false), 2400) } })
        })
      }catch(_){}
    }, 35000)
    return ()=> clearInterval(id)
  }, [settings.tgToken, symbols, tf])

  return (
    <div className="app">
      <header>
        <div className="brand"><Logo /></div>
        <div className="badges">
          <div className="badge">TF: {tf}</div>
          <div className="badge">Pulse: {pulse}</div>
          <div className="badge">{status}</div>
          <div className="badge" style={{cursor:'pointer'}} onClick={()=>setSettingsOpen(true)}>⚙️ Settings</div>
        </div>
      </header>

      <div className="toolbar">
        <div className="tf">
          {TFs.map(t => <button key={t} className={t===tf?'active':''} onClick={()=>onTF(t)}>{t}</button>)}
        </div>
      </div>

      <aside className="sidebar">
        <div className="sideHead"><div>My Watchlist</div><div id="count" style={{opacity:.7,fontSize:12}}>{symbols.length}</div></div>
        <div className="addWrap">
          <input id="addSym" placeholder="e.g. BTCUSDT" onKeyDown={(e)=>{
            const t=e.target as HTMLInputElement; if(e.key==='Enter') onAddSymbol(t.value)
          }}/>
          <button onClick={()=>{
            const el = document.getElementById('addSym') as HTMLInputElement
            onAddSymbol(el.value); el.value=''
          }}>Add</button>
        </div>
        <div className="list">
          {symbols.map(sym => (
            <div key={sym} className="item" onClick={()=>onActive(sym)}>
              <div>
                <div className="sym">{sym}</div>
                <div className="px">{data[sym]?.at(-1)?.c?.toFixed(6) ?? '—'}</div>
              </div>
              <div style={{display:'flex',alignItems:'center',gap:8}}>
                <div className={"chg " + ((()=>{
                  const arr=data[sym]; if(!arr) return ''
                  const first = arr[Math.max(0,arr.length-61)]?.c ?? arr[0]?.c
                  const last = arr.at(-1)?.c ?? 0
                  const ch = first? (last/first-1)*100 : 0
                  return ch>=0?'up':'down'
                })())}>
                  {(()=>{
                    const arr=data[sym]; if(!arr) return '0.00%'
                    const first = arr[Math.max(0,arr.length-61)]?.c ?? arr[0]?.c
                    const last = arr.at(-1)?.c ?? 0
                    const ch = first? (last/first-1)*100 : 0
                    return (ch>=0?'+':'')+ch.toFixed(2)+'%'
                  })()}
                </div>
                <div className="rm" onClick={(e)=>{ e.stopPropagation(); onRemoveSymbol(sym) }}>×</div>
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main className="main">
        <div className="pulse" style={{borderColor: pulse==='HIGH VOL' ? '#18c964' : pulse==='LOW VOL' ? '#f0b90b' : '#3aa0ff'}}>SCALP ZONE: {pulse}</div>
        <div className="chartWrap">
          <div ref={chartRef} style={{height:'56vh', minHeight:280}}/>
          <div ref={rsiRef} style={{height:120}}/>
          <div className="chartControls">
            <button onClick={()=>zoom(-10)}>🔍➕</button>
            <button onClick={()=>zoom(10)}>🔍➖</button>
            <button onClick={()=>scroll(-30)}>⏪</button>
            <button onClick={()=>scroll(30)}>⏩</button>
            <button onClick={()=>chartApi.current?.timeScale().fitContent()}>🎯 Reset</button>
            <button onClick={()=>chartApi.current?.timeScale().scrollToRealTime()}>📡 Realtime</button>
          </div>
        </div>
        <div className="signal" style={{border:'1px solid #18232f'}}>{signalText}</div>
      </main>

      <footer>
        <button className="btn long" onClick={()=> setPopupMsg(`LONG ${active} — demo`) || setShowPopup(true) || setTimeout(()=>setShowPopup(false),1500)}>LONG</button>
        <button className="btn short" onClick={()=> setPopupMsg(`SHORT ${active} — demo`) || setShowPopup(true) || setTimeout(()=>setShowPopup(false),1500)}>SHORT</button>
        <button className="btn close" onClick={()=> setPopupMsg(`CLOSE ${active} — demo`) || setShowPopup(true) || setTimeout(()=>setShowPopup(false),1500)}>CLOSE</button>
      </footer>

      <SignalPopup show={showPopup} message={popupMsg} />
      <SettingsModal open={settingsOpen} onClose={()=>setSettingsOpen(false)} settings={settings} onSave={(s)=>{ saveSettings(s); setSettings(s) }} />
    </div>
  )
}
