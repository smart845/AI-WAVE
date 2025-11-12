export type Bar = { t:number,o:number,h:number,l:number,c:number,v:number }

function mapKlines(arr:any[]):Bar[]{
  return arr.map((k:any)=>({ t:k[0], o:+k[1], h:+k[2], l:+k[3], c:+k[4], v:+k[5] }))
}

export async function fetchKlines(symbol:string, tf:string, limit=500):Promise<Bar[]>{
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${tf}&limit=${limit}`
  const r = await fetch(url)
  if(!r.ok) throw new Error('REST '+r.status)
  const a = await r.json()
  return mapKlines(a)
}

type StreamEvt =
 | { type:'status', payload:string }
 | { type:'kline', symbol:string, bar:Bar }

export function streamSubscribe(symbols:string[], tf:string, cb:(e:StreamEvt)=>void){
  const ws = new WebSocket('wss://stream.binance.com:9443/ws')
  const params = symbols.flatMap(s => [`${s.toLowerCase()}@kline_${tf}`, `${s.toLowerCase()}@trade`])
  ws.onopen = ()=>{ cb({type:'status', payload:'WS: connected'}); ws.send(JSON.stringify({ method:'SUBSCRIBE', params, id:Date.now() })) }
  ws.onclose= ()=> cb({type:'status', payload:'WS: disconnected'})
  ws.onerror= ()=> {}
  ws.onmessage = (ev)=>{
    try{
      const d = JSON.parse(ev.data)
      if (d.e==='kline' && d.k?.i===tf){
        const k = d.k
        const bar:Bar = { t:k.t, o:+k.o, h:+k.h, l:+k.l, c:+k.c, v:+k.v }
        cb({ type:'kline', symbol: d.s, bar })
      }
    }catch{}
  }
  return ()=> ws.close()
}
