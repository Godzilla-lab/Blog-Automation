import React from 'react';
import { AbsoluteFill } from 'remotion';

// A clean, precisely-drawn MacBook centered in a 1920x1080 frame.
// Screen content is passed as children and clipped inside the display.
const SCREEN_W = 1200;
const SCREEN_H = 760;
const BEZEL = 16;
const TOP = 140;
const LEFT = (1920 - SCREEN_W) / 2;

// inner display area (where children render), exported for content sizing
export const DISPLAY = { W: SCREEN_W - BEZEL * 2, H: SCREEN_H - BEZEL * 2 };

export const MacBook: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <AbsoluteFill>
      {/* soft contact shadow on the desk */}
      <div
        style={{
          position: 'absolute',
          left: LEFT - 70,
          top: TOP + SCREEN_H + 34,
          width: SCREEN_W + 140,
          height: 70,
          background: 'radial-gradient(ellipse at center, rgba(25,35,28,0.20), transparent 72%)',
          filter: 'blur(14px)',
        }}
      />
      {/* screen body / bezel */}
      <div
        style={{
          position: 'absolute',
          left: LEFT,
          top: TOP,
          width: SCREEN_W,
          height: SCREEN_H,
          borderRadius: 26,
          background: 'linear-gradient(180deg,#1c1e20,#0d0f11)',
          boxShadow: '0 40px 90px rgba(25,35,28,0.22), inset 0 0 0 1.5px #2a2d30',
          padding: BEZEL,
        }}
      >
        {/* camera dot */}
        <div style={{ position: 'absolute', top: 6, left: '50%', transform: 'translateX(-50%)', width: 6, height: 6, borderRadius: '50%', background: '#2f3336' }} />
        {/* display */}
        <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: 12, overflow: 'hidden', background: '#FBFBFD' }}>
          {children}
          {/* subtle screen reflection */}
          <AbsoluteFill style={{ background: 'linear-gradient(118deg, rgba(255,255,255,0.10) 0%, transparent 26%, transparent 72%, rgba(255,255,255,0.05) 100%)', pointerEvents: 'none' }} />
        </div>
      </div>
      {/* base / deck */}
      <div
        style={{
          position: 'absolute',
          left: LEFT - 36,
          top: TOP + SCREEN_H + 2,
          width: SCREEN_W + 72,
          height: 28,
          borderRadius: '7px 7px 14px 14px',
          background: 'linear-gradient(180deg,#cdd0d2,#a6aaad)',
          boxShadow: '0 10px 20px rgba(25,35,28,0.14)',
        }}
      >
        {/* finger notch */}
        <div style={{ position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)', width: 128, height: 9, borderRadius: '0 0 12px 12px', background: '#9aa0a3' }} />
      </div>
    </AbsoluteFill>
  );
};
