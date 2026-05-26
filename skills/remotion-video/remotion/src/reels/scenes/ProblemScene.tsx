import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { orbitronFamily, syneFamily } from '../../lib/fonts';

/**
 * Scene 2: The Problem (frames 0-390, 13 seconds within this sequence)
 * Animated stat cards on dark background.
 * Stats fly in staggered with red/warm accent.
 */

const PROBLEM_COLOR = '#ff6b6b';

const STATS = [
  { value: '23%', label: 'of dental appointments end in no-shows' },
  { value: '68%', label: 'of cleaning contracts lost to communication' },
  { value: '$150K+', label: 'lost per year to inefficiency' },
];

export const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const isLandscape = width > height;
  const cardWidth = isLandscape ? 500 : 400;
  const cardHeight = isLandscape ? 140 : 130;

  // Subtle background pulse
  const bgPulse = interpolate(frame % 90, [0, 45, 90], [0.08, 0.14, 0.08], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {/* Red ambient glow */}
      <div
        style={{
          position: 'absolute',
          top: '20%',
          left: '30%',
          width: 600,
          height: 600,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${PROBLEM_COLOR}, transparent 70%)`,
          opacity: bgPulse,
          filter: 'blur(100px)',
        }}
      />

      {/* Section label */}
      <div
        style={{
          position: 'absolute',
          top: isLandscape ? 60 : 80,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: syneFamily,
          fontSize: 20,
          fontWeight: 600,
          color: PROBLEM_COLOR,
          letterSpacing: 6,
          textTransform: 'uppercase',
          opacity: interpolate(frame, [0, 15], [0, 0.7], {
            extrapolateRight: 'clamp',
          }),
        }}
      >
        THE PROBLEM
      </div>

      {/* Stat cards */}
      {STATS.map((stat, i) => {
        const delay = 20 + i * 30;
        const cardSpring = spring({
          frame: frame - delay,
          fps,
          config: { ...SPRING_CONFIG, stiffness: 100 },
          durationInFrames: 25,
        });

        // Slide in from alternating sides
        const slideFrom = i % 2 === 0 ? -1 : 1;
        const translateX = (1 - cardSpring) * slideFrom * 200;

        // Number counter
        const numericValue = parseFloat(stat.value.replace(/[^0-9.]/g, ''));
        const countProgress = interpolate(
          frame,
          [delay + 10, delay + 35],
          [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
        );
        const displayNum = Math.round(numericValue * countProgress);
        const displayValue = stat.value.startsWith('$')
          ? `$${displayNum}K+`
          : `${displayNum}%`;

        // Left accent bar glow
        const barGlow = interpolate(
          (frame - delay) % 60,
          [0, 30, 60],
          [0.5, 1, 0.5],
          { extrapolateRight: 'clamp' },
        );

        const centerY = isLandscape
          ? height * 0.25 + i * (cardHeight + 30)
          : height * 0.2 + i * (cardHeight + 40);

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: centerY,
              left: (width - cardWidth) / 2,
              width: cardWidth,
              height: cardHeight,
              opacity: cardSpring,
              transform: `translateX(${translateX}px)`,
              display: 'flex',
              alignItems: 'center',
              borderRadius: 12,
              backgroundColor: `${COLORS.surface}cc`,
              border: `1px solid ${PROBLEM_COLOR}20`,
              overflow: 'hidden',
            }}
          >
            {/* Left accent bar */}
            <div
              style={{
                width: 5,
                height: '100%',
                backgroundColor: PROBLEM_COLOR,
                boxShadow: `0 0 ${12 * barGlow}px ${PROBLEM_COLOR}`,
                flexShrink: 0,
              }}
            />

            {/* Number */}
            <div
              style={{
                fontFamily: orbitronFamily,
                fontSize: isLandscape ? 52 : 48,
                fontWeight: 900,
                color: PROBLEM_COLOR,
                padding: '0 24px',
                minWidth: isLandscape ? 180 : 150,
                textAlign: 'center',
                textShadow: `0 0 20px ${PROBLEM_COLOR}40`,
              }}
            >
              {displayValue}
            </div>

            {/* Label */}
            <div
              style={{
                fontFamily: syneFamily,
                fontSize: isLandscape ? 22 : 20,
                color: COLORS.textMuted,
                lineHeight: 1.3,
                paddingRight: 24,
              }}
            >
              {stat.label}
            </div>
          </div>
        );
      })}

      {/* Floating down-arrow particles */}
      {Array.from({ length: 8 }).map((_, i) => {
        const x = width * 0.15 + ((i * 137) % (width * 0.7));
        const startY = -30 - (i * 47) % 100;
        const y = startY + frame * (1.2 + (i % 3) * 0.4);
        const particleOpacity = interpolate(
          y,
          [0, 100, height - 200, height],
          [0, 0.2, 0.2, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
        );

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y % (height + 100),
              fontFamily: syneFamily,
              fontSize: 16,
              color: PROBLEM_COLOR,
              opacity: particleOpacity,
            }}
          >
            ▼
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
