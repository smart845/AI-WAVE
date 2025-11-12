import React from 'react'

export default function SignalPopup({ show, message }:{ show:boolean, message:string }){
  return (
    <div className="popup" style={{display: show ? 'block':'none'}}>
      <div className="popH">AI Signal</div>
      <div className="popB">{message}</div>
    </div>
  )
}
