import React from 'react';

// macOS-style arrow cursor
export const Cursor: React.FC<{ x: number; y: number; opacity?: number; scale?: number }> = ({ x, y, opacity = 1, scale = 1 }) => (
  <svg
    width={30}
    height={30}
    viewBox="0 0 24 24"
    style={{ position: 'absolute', left: x, top: y, opacity, transform: `scale(${scale})`, transformOrigin: 'top left', filter: 'drop-shadow(0 2px 3px rgba(0,0,0,0.35))' }}
  >
    <path d="M4 2 L4 20 L9 15 L12.6 21.6 L15.3 20.3 L11.8 14 L18 14 Z" fill="#ffffff" stroke="#1a1a1a" strokeWidth={1.4} strokeLinejoin="round" />
  </svg>
);
