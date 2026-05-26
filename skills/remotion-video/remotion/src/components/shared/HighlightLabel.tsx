import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { orbitronFamily } from '../../lib/fonts';

export const HighlightLabel: React.FC<{ text: string; accent?: string }> = ({
  text,
  accent = COLORS.primary,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lineWidth = spring({
    frame: frame - 40,
    fps,
    config: { ...SPRING_CONFIG, damping: 22 },
    durationInFrames: 30,
  });

  const textOpacity = interpolate(frame, [50, 65], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const textY = interpolate(frame, [50, 65], [10, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 120,
        left: 0,
        right: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 16,
      }}
    >
      {/* Horizontal line */}
      <div
        style={{
          width: 120 * lineWidth,
          height: 2,
          backgroundColor: accent,
          opacity: 0.8,
        }}
      />
      {/* Label text */}
      <div
        style={{
          fontFamily: orbitronFamily,
          fontSize: 24,
          fontWeight: 700,
          color: COLORS.textPrimary,
          letterSpacing: 6,
          textTransform: 'uppercase',
          opacity: textOpacity,
          transform: `translateY(${textY}px)`,
        }}
      >
        {text}
      </div>
    </div>
  );
};
