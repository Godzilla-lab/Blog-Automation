import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { COLORS, WIDTH, HEIGHT } from '../../brand';

const DOT_SPACING = 40;
const DOT_RADIUS = 1.5;

export const Background: React.FC<{ accent?: string }> = ({
  accent = COLORS.primary,
}) => {
  const frame = useCurrentFrame();

  // Subtle dot grid
  const dots: React.ReactNode[] = [];
  for (let x = DOT_SPACING; x < WIDTH; x += DOT_SPACING) {
    for (let y = DOT_SPACING; y < HEIGHT; y += DOT_SPACING) {
      dots.push(
        <circle key={`${x}-${y}`} cx={x} cy={y} r={DOT_RADIUS} fill={COLORS.textMuted} />
      );
    }
  }

  // Slow breathing glow
  const glowPulse = interpolate(frame, [0, 90, 180], [0.15, 0.22, 0.15], {
    extrapolateRight: 'clamp',
  });

  const glowPulse2 = interpolate(frame, [0, 90, 180], [0.1, 0.17, 0.1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {/* Dot grid at 6% opacity */}
      <svg
        width={WIDTH}
        height={HEIGHT}
        style={{ position: 'absolute', opacity: 0.06 }}
      >
        {dots}
      </svg>

      {/* Teal glow top-left */}
      <div
        style={{
          position: 'absolute',
          top: -200,
          left: -200,
          width: 800,
          height: 800,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${accent}, transparent 70%)`,
          opacity: glowPulse,
          filter: 'blur(80px)',
        }}
      />

      {/* Blue glow bottom-right */}
      <div
        style={{
          position: 'absolute',
          bottom: -200,
          right: -200,
          width: 700,
          height: 700,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${COLORS.secondary}, transparent 70%)`,
          opacity: glowPulse2,
          filter: 'blur(80px)',
        }}
      />
    </AbsoluteFill>
  );
};
