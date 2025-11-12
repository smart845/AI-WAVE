import React from 'react'

export default function Logo(){
  return (
    <svg width="170" height="26" viewBox="0 0 340 52" fill="none" xmlns="http://www.w3.org/2000/svg" style={{display:'block'}}>
      <defs>
        <linearGradient id="metal" x1="0" y1="0" x2="340" y2="0">
          <stop offset="0%" stopColor="#0f1216"/>
          <stop offset="25%" stopColor="#2a2f37"/>
          <stop offset="50%" stopColor="#1a1f26"/>
          <stop offset="75%" stopColor="#3b424c"/>
          <stop offset="100%" stopColor="#0d1014"/>
        </linearGradient>
        <linearGradient id="accent" x1="0" y1="0" x2="0" y2="52">
          <stop offset="0%" stopColor="#9be7ff" stopOpacity="0.25"/>
          <stop offset="100%" stopColor="#18c964" stopOpacity="0.35"/>
        </linearGradient>
      </defs>
      <text x="0" y="38" fontFamily="Inter,Segoe UI,Arial" fontSize="36" fontWeight="900" fill="url(#metal)" letterSpacing="1">SCALP AI — My Scalper</text>
      <rect x="0" y="44" width="340" height="4" fill="url(#accent)" opacity="0.6"/>
    </svg>
  )
}
