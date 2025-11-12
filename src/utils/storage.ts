import type { Settings } from '../ui/SettingsModal'

const KEY_WL='scalp.v1.wl', KEY_ACTIVE='scalp.v1.active', KEY_TF='scalp.v1.tf', KEY_SET='scalp.v1.settings'

export function loadWL():string[]{
  try{ const v=JSON.parse(localStorage.getItem(KEY_WL)||'[]'); return Array.isArray(v)&&v.length?v:['SOLUSDT','PEPEUSDT','BONKUSDT','BTCUSDT'] }catch{ return ['SOLUSDT','PEPEUSDT','BONKUSDT','BTCUSDT'] }
}
export function saveWL(arr:string[]){ localStorage.setItem(KEY_WL, JSON.stringify(arr)) }

export function loadActive(){ return localStorage.getItem(KEY_ACTIVE) }
export function saveActive(v:string){ localStorage.setItem(KEY_ACTIVE, v) }

export function loadTF(){ return localStorage.getItem(KEY_TF) || '1m' }
export function saveTF(v:string){ localStorage.setItem(KEY_TF, v) }

export function loadSettings():Settings{
  try{ return JSON.parse(localStorage.getItem(KEY_SET)||'{}') }catch{ return {} }
}
export function saveSettings(s:Settings){ localStorage.setItem(KEY_SET, JSON.stringify(s||{})) }
