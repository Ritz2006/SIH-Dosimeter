// Illustrates the physical artifact the whole product is built
// around: a strap carrying a reference colour scale, the H2S
// sensor patch, a separate expiry patch, and a QR code. Reused
// wherever the app wants to say "this is a real wristband", not a
// generic device silhouette.
export default function WristbandIcon({ tone = 'amber', size = 220 }) {
  const sensorColor = tone === 'rust' ? '#a8492c' : tone === 'green' ? '#5fa776' : '#c98a26'

  return (
    <svg width={size} height={size * 0.62} viewBox="0 0 280 174" fill="none" role="img" aria-label="H2S dosimeter wristband">
      {/* strap */}
      <rect x="8" y="52" width="40" height="70" rx="10" stroke="#3a4952" strokeWidth="2" />
      <rect x="232" y="52" width="40" height="70" rx="10" stroke="#3a4952" strokeWidth="2" />

      {/* main body */}
      <rect x="40" y="20" width="200" height="134" rx="14" fill="#161d22" stroke="#3a4952" strokeWidth="2" />

      {/* reference scale label */}
      <text x="58" y="42" fill="#74838c" fontFamily="IBM Plex Mono, monospace" fontSize="9">REFERENCE</text>
      <rect x="58" y="48" width="16" height="16" rx="2" fill="#f6dfa6" />
      <rect x="78" y="48" width="16" height="16" rx="2" fill="#e3a73b" />
      <rect x="98" y="48" width="16" height="16" rx="2" fill="#c98a26" />
      <rect x="118" y="48" width="16" height="16" rx="2" fill="#a8492c" />

      {/* white calibration patch */}
      <rect x="58" y="76" width="16" height="16" rx="2" fill="#edefea" />
      <text x="80" y="88" fill="#74838c" fontFamily="IBM Plex Mono, monospace" fontSize="8">CAL</text>

      {/* sensor patch */}
      <text x="150" y="42" fill="#74838c" fontFamily="IBM Plex Mono, monospace" fontSize="9">H2S SENSOR</text>
      <rect x="150" y="48" width="44" height="44" rx="4" fill={sensorColor} stroke="#10161a" strokeWidth="1" />

      {/* expiry patch */}
      <text x="150" y="106" fill="#74838c" fontFamily="IBM Plex Mono, monospace" fontSize="9">EXPIRY</text>
      <rect x="150" y="112" width="44" height="16" rx="3" fill="#212b31" stroke="#3a4952" />
      <circle cx="158" cy="120" r="3.5" fill="#5fa776" />

      {/* QR code (stylised, not a real scannable code) */}
      <g transform="translate(58,102)">
        <rect width="34" height="34" rx="3" fill="#edefea" />
        {[0,1,2,3,4].map((r) =>
          [0,1,2,3,4].map((c) => (
            (r + c) % 2 === 0 && r < 5 && c < 5 ? (
              <rect key={`${r}-${c}`} x={4 + c * 5.2} y={4 + r * 5.2} width="4.4" height="4.4" fill="#10161a" />
            ) : null
          ))
        )}
      </g>

      <text x="150" y="146" fill="#74838c" fontFamily="IBM Plex Mono, monospace" fontSize="8">H2S-00127</text>
    </svg>
  )
}
