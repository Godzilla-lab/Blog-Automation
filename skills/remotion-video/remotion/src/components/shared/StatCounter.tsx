import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { orbitronFamily, syneFamily } from '../../lib/fonts';

interface StatCounterProps {
  value: number;
  prefix?: string;
  suffix?: string;
  label: string;
  startFrame?: number;
  accent?: string;
  fontSize?: number;
  labelFontSize?: number;
}

export const StatCounter: React.FC<StatCounterProps> = ({
  value,
  prefix = '',
  suffix = '',
  label,
  startFrame = 0,
  accent = COLORS.primary,
  fontSize = 96,
  labelFontSize = 32,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrySpring = spring({
    frame: frame - startFrame,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 30,
  });

  // Count up animation
  const countProgress = interpolate(
    frame,
    [startFrame + 5, startFrame + 35],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );
  const displayValue = Math.round(value * countProgress);

  // Label fade in after number
  const labelOpacity = interpolate(
    frame,
    [startFrame + 25, startFrame + 40],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );
  const labelY = interpolate(
    frame,
    [startFrame + 25, startFrame + 40],
    [15, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Glow pulse after counter finishes
  const glowPulse =
    countProgress >= 1
      ? interpolate(
          (frame - startFrame - 35) % 60,
          [0, 30, 60],
          [0.4, 0.8, 0.4],
          { extrapolateRight: 'clamp' },
        )
      : 0.3;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        opacity: entrySpring,
        transform: `scale(${0.85 + entrySpring * 0.15})`,
      }}
    >
      <div
        style={{
          fontFamily: orbitronFamily,
          fontSize,
          fontWeight: 900,
          color: accent,
          textShadow: `0 0 ${40 * glowPulse}px ${accent}, 0 0 ${80 * glowPulse}px ${accent}40`,
          lineHeight: 1,
        }}
      >
        {prefix}
        {displayValue}
        {suffix}
      </div>
      <div
        style={{
          fontFamily: syneFamily,
          fontSize: labelFontSize,
          color: COLORS.textMuted,
          marginTop: 8,
          opacity: labelOpacity,
          transform: `translateY(${labelY}px)`,
          letterSpacing: 1,
        }}
      >
        {label}
      </div>
    </div>
  );
};
