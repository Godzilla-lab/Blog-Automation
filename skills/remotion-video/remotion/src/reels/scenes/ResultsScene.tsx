import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG, STAGGER } from '../../brand';
import { Background } from '../../components/shared/Background';
import { CornerBrackets } from '../../components/shared/CornerBrackets';
import { StatCounter } from '../../components/shared/StatCounter';
import { orbitronFamily, syneFamily } from '../../lib/fonts';

/**
 * Scene 5: Results (frames 0-420, 14 seconds)
 * Animated stat counters with glow effects.
 */

const STATS = [
  { value: 100, prefix: '$', suffix: 'K+', label: '/year recovered', accent: COLORS.primary },
  { value: 40, prefix: '', suffix: '%', label: 'fewer no-shows', accent: COLORS.secondary },
  { value: 20, prefix: '', suffix: '+', label: 'hours/week saved', accent: COLORS.purple },
];

export const ResultsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isLandscape = width > height;

  // Section label
  const labelOpacity = interpolate(frame, [5, 20], [0, 0.7], {
    extrapolateRight: 'clamp',
  });

  // Divider line under "RESULTS"
  const dividerWidth = spring({
    frame: frame - 15,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 25,
  });

  // Bar chart decorative element (background)
  const barData = [0.4, 0.6, 0.5, 0.8, 0.7, 0.95, 0.85];

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      <Background accent={COLORS.primary} />
      <CornerBrackets accent={COLORS.primary} />

      {/* Decorative bar chart in background */}
      {isLandscape &&
        barData.map((h, i) => {
          const barSpring = spring({
            frame: frame - 30 - i * 4,
            fps,
            config: SPRING_CONFIG,
            durationInFrames: 30,
          });
          const barHeight = h * 300 * barSpring;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                right: 80 + i * 50,
                bottom: 100,
                width: 30,
                height: barHeight,
                borderRadius: 4,
                background: `linear-gradient(to top, ${COLORS.primary}08, ${COLORS.primary}20)`,
              }}
            />
          );
        })}

      {/* Section label */}
      <div
        style={{
          position: 'absolute',
          top: isLandscape ? 60 : 80,
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: labelOpacity,
        }}
      >
        <div
          style={{
            fontFamily: syneFamily,
            fontSize: 20,
            fontWeight: 600,
            color: COLORS.primary,
            letterSpacing: 6,
            textTransform: 'uppercase',
          }}
        >
          REAL RESULTS
        </div>
        <div
          style={{
            margin: '12px auto 0',
            width: 80 * dividerWidth,
            height: 2,
            backgroundColor: COLORS.primary,
            opacity: 0.5,
          }}
        />
      </div>

      {/* Stats */}
      {isLandscape ? (
        // Landscape: horizontal row
        <div
          style={{
            position: 'absolute',
            top: height * 0.3,
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            gap: 100,
          }}
        >
          {STATS.map((stat, i) => (
            <StatCounter
              key={i}
              value={stat.value}
              prefix={stat.prefix}
              suffix={stat.suffix}
              label={stat.label}
              startFrame={30 + i * 20}
              accent={stat.accent}
              fontSize={80}
              labelFontSize={24}
            />
          ))}
        </div>
      ) : (
        // Portrait: vertical stack
        STATS.map((stat, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: 200 + i * 180,
              left: 0,
              right: 0,
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <StatCounter
              value={stat.value}
              prefix={stat.prefix}
              suffix={stat.suffix}
              label={stat.label}
              startFrame={30 + i * 25}
              accent={stat.accent}
            />
          </div>
        ))
      )}

      {/* Tagline below stats */}
      <div
        style={{
          position: 'absolute',
          bottom: isLandscape ? 120 : 200,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: syneFamily,
          fontSize: isLandscape ? 28 : 24,
          color: COLORS.textPrimary,
          opacity: interpolate(frame, [120, 140], [0, 0.8], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }}
      >
        Built for service businesses ready to scale.
      </div>
    </AbsoluteFill>
  );
};
