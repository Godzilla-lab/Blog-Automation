import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG, WIDTH } from '../brand';
import { Background } from '../components/shared/Background';
import { LogoBadge } from '../components/shared/LogoBadge';
import { CornerBrackets } from '../components/shared/CornerBrackets';
import { HighlightLabel } from '../components/shared/HighlightLabel';
import { orbitronFamily, syneFamily } from '../lib/fonts';

const accent = COLORS.primary;
const CENTER_X = WIDTH / 2;
const CALENDAR_Y = 520;
const CALENDAR_SIZE = 240;

export const BookACall: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Calendar draw-in
  const drawProgress = interpolate(frame, [20, 55], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Date cell highlight pulse
  const highlightPulse = interpolate(
    frame,
    [60, 75, 90, 105, 120, 135, 150, 165, 180],
    [0, 1, 0.6, 1, 0.6, 1, 0.6, 1, 0.6],
    { extrapolateRight: 'clamp' }
  );

  const highlightOpacity = interpolate(frame, [55, 65], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Text animations
  const mainTextSpring = spring({
    frame: frame - 70,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 30,
  });

  const subTextOpacity = interpolate(frame, [90, 105], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const badgeSpring = spring({
    frame: frame - 110,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 25,
  });

  // Teal shimmer sweep at end
  const shimmerX = interpolate(frame, [140, 175], [-400, WIDTH + 400], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Calendar SVG stroke
  const perimeterLength = (CALENDAR_SIZE + CALENDAR_SIZE) * 2;

  return (
    <AbsoluteFill>
      <Background accent={accent} />
      <LogoBadge />
      <CornerBrackets accent={accent} />

      {/* Calendar icon */}
      <div
        style={{
          position: 'absolute',
          left: CENTER_X - CALENDAR_SIZE / 2,
          top: CALENDAR_Y,
        }}
      >
        <svg width={CALENDAR_SIZE} height={CALENDAR_SIZE}>
          {/* Calendar body - stroke animation */}
          <rect
            x={10}
            y={40}
            width={CALENDAR_SIZE - 20}
            height={CALENDAR_SIZE - 50}
            rx={12}
            fill="none"
            stroke={accent}
            strokeWidth={2.5}
            strokeDasharray={perimeterLength}
            strokeDashoffset={perimeterLength * (1 - drawProgress)}
          />
          {/* Calendar top tabs */}
          <line
            x1={75}
            y1={20}
            x2={75}
            y2={55}
            stroke={accent}
            strokeWidth={3}
            strokeLinecap="round"
            opacity={drawProgress}
          />
          <line
            x1={165}
            y1={20}
            x2={165}
            y2={55}
            stroke={accent}
            strokeWidth={3}
            strokeLinecap="round"
            opacity={drawProgress}
          />
          {/* Header line */}
          <line
            x1={30}
            y1={80}
            x2={CALENDAR_SIZE - 30}
            y2={80}
            stroke={accent}
            strokeWidth={1.5}
            opacity={drawProgress * 0.5}
          />
          {/* Grid dots (days) */}
          {Array.from({ length: 20 }).map((_, i) => {
            const col = i % 5;
            const row = Math.floor(i / 5);
            const dotOpacity = interpolate(
              drawProgress,
              [0.5, 0.7 + i * 0.01],
              [0, 0.3],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            );
            return (
              <circle
                key={i}
                cx={50 + col * 40}
                cy={105 + row * 35}
                r={4}
                fill={COLORS.textMuted}
                opacity={dotOpacity}
              />
            );
          })}
          {/* Highlighted date cell */}
          <circle
            cx={130}
            cy={140}
            r={16}
            fill="none"
            stroke={accent}
            strokeWidth={2}
            opacity={highlightOpacity}
          />
          <circle
            cx={130}
            cy={140}
            r={16 + highlightPulse * 8}
            fill="none"
            stroke={accent}
            strokeWidth={1}
            opacity={highlightOpacity * (1 - highlightPulse * 0.5)}
          />
        </svg>
      </div>

      {/* Main CTA text */}
      <div
        style={{
          position: 'absolute',
          top: 830,
          left: 0,
          right: 0,
          textAlign: 'center',
          transform: `scale(${mainTextSpring})`,
          opacity: mainTextSpring,
        }}
      >
        <div
          style={{
            fontFamily: orbitronFamily,
            fontSize: 42,
            fontWeight: 900,
            color: COLORS.textPrimary,
            lineHeight: 1.3,
            padding: '0 60px',
          }}
        >
          FREE 30-MIN{'\n'}STRATEGY CALL
        </div>
      </div>

      {/* Subtext */}
      <div
        style={{
          position: 'absolute',
          top: 975,
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: subTextOpacity,
        }}
      >
        <div
          style={{
            fontFamily: syneFamily,
            fontSize: 28,
            color: accent,
          }}
        >
          cal.com/hexaiagency
        </div>
      </div>

      {/* No commitment badge */}
      <div
        style={{
          position: 'absolute',
          top: 1040,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          transform: `scale(${badgeSpring})`,
          opacity: badgeSpring,
        }}
      >
        <div
          style={{
            padding: '10px 24px',
            borderRadius: 20,
            border: `1px solid ${COLORS.textMuted}40`,
            fontFamily: syneFamily,
            fontSize: 18,
            color: COLORS.textMuted,
          }}
        >
          No commitment
        </div>
      </div>

      {/* Teal shimmer sweep */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: shimmerX,
          width: 200,
          height: '100%',
          background: `linear-gradient(90deg, transparent, ${accent}12, transparent)`,
          transform: 'skewX(-15deg)',
          pointerEvents: 'none',
        }}
      />

      <HighlightLabel text="Book A Call" accent={accent} />
    </AbsoluteFill>
  );
};
