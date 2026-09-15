export default function SchoolCrest({ size = 40, className = '', variant = 'default' }) {
  // Variants: 'default' (navy/gold), 'white' (white monochrome), 'gold' (gold monochrome)
  const isWhite = variant === 'white'
  const isGold = variant === 'gold'

  const primaryColor = isWhite ? '#ffffff' : isGold ? '#d7b979' : '#173a2b'
  const accentColor = isWhite ? '#ffffff' : '#b38848'
  const textColor = isWhite ? '#ffffff' : isGold ? '#ffffff' : '#f7f5ef'

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Riverside Academy Crest"
    >
      {/* Outer circular rim */}
      <circle cx="50" cy="50" r="48" fill={primaryColor} stroke={accentColor} strokeWidth="2.5" />
      <circle cx="50" cy="50" r="44" stroke={accentColor} strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />

      {/* Inner shield background */}
      <path
        d="M50 18 C65 18 72 26 72 40 C72 60 50 78 50 78 C50 78 28 60 28 40 C28 26 35 18 50 18 Z"
        fill={isWhite ? 'rgba(255,255,255,0.15)' : '#102c21'}
        stroke={accentColor}
        strokeWidth="1.8"
      />

      {/* Open Book in Upper Center */}
      <path
        d="M37 36 C42 34 47 35 50 37 C53 35 58 34 63 36 V48 C58 46 53 47 50 49 C47 47 42 46 37 48 Z"
        fill={isWhite ? '#ffffff' : '#f7f5ef'}
        stroke={accentColor}
        strokeWidth="1.2"
      />
      <line x1="50" y1="37" x2="50" y2="49" stroke={accentColor} strokeWidth="1.2" />

      {/* Star of Excellence */}
      <polygon
        points="50,23 52,28 57,28 53,31 55,36 50,33 45,36 47,31 43,28 48,28"
        fill={accentColor}
      />

      {/* Laurel leaves on left and right of shield */}
      <path
        d="M23 48 C21 40 24 32 29 27 M23 48 C22 55 25 62 31 68 M21 42 C18 45 19 51 22 55"
        stroke={accentColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M77 48 C79 40 76 32 71 27 M77 48 C78 55 75 62 69 68 M79 42 C82 45 81 51 78 55"
        stroke={accentColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />

      {/* Letter R in lower shield */}
      <text
        x="50"
        y="65"
        textAnchor="middle"
        fontFamily="Georgia, serif"
        fontSize="14"
        fontWeight="bold"
        fill={accentColor}
      >
        R
      </text>

      {/* Motto banner text */}
      <text
        x="50"
        y="91"
        textAnchor="middle"
        fontFamily="Georgia, serif"
        fontSize="7.5"
        letterSpacing="1.8"
        fontWeight="600"
        fill={textColor}
      >
        VERITAS · SCIENTIA
      </text>
    </svg>
  )
}

