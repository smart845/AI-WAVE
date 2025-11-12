import React, { useState } from 'react'

export type Settings = { tgToken?: string; tgChatId?: string; openaiKey?: string }

export default function SettingsModal({ open, onClose, settings, onSave }:
  { open:boolean, onClose:()=>void, settings:Settings, onSave:(s:Settings)=>void }){

  const [form, setForm] = useState<Settings>(settings || {})

  return (
    <div className="modal" style={{display: open ? 'flex':'none'}}>
      <div className="box">
        <h3>Settings</h3>
        <div className="row">
          <input placeholder="Telegram Bot Token (optional)" value={form.tgToken||''}
            onChange={e=> setForm({...form, tgToken:e.target.value}) } />
          <input placeholder="Telegram Group/Channel Chat ID (optional)" value={form.tgChatId||''}
            onChange={e=> setForm({...form, tgChatId:e.target.value}) } />
        </div>
        <div className="row">
          <input placeholder="OpenAI / Grok API Key (optional)" value={form.openaiKey||''}
            onChange={e=> setForm({...form, openaiKey:e.target.value}) } />
          <button onClick={()=> onSave(form)}>Save</button>
          <button onClick={onClose}>Close</button>
        </div>
        <div style={{fontSize:12,color:'#9aa4b2'}}>Ключи/токены сохраняются только локально (localStorage). Никаких серверов.</div>
      </div>
    </div>
  )
}
