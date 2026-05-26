import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { Background } from '../../components/shared/Background';
import { CornerBrackets } from '../../components/shared/CornerBrackets';
import { orbitronFamily, syneFamily } from '../../lib/fonts';

/**
 * Scene 6: CTA (frames 0-540, 18 seconds)
 * Calendar draw-in, headline, URL, handle, shimmer.
 */

const accent = COLORS.primary;
const CALENDAR_SIZE = 180;

export const CTAScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isLandscape = width > height;

  const centerX = width / 2;
  const calendarY = isLandscape ? height * 0.15 : height * 0.18;

  // Calendar draw-in
  const drawProgress = interpolate(frame, [15, 50], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Highlight pulse on a date
  const highlightPulse = interpolate(
    frame % 40,
    [0, 20, 40],
    [0.6, 1, 0.6],
    { extrapolateRight: 'clamp' },
  );
  const highlightOpacity = interpolate(frame, [45, 55], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // CTA text
  const headlineSpring = spring({
    frame: frame - 55,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 30,
  });

  const urlOpacity = interpolate(frame, [80, 95], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const handleOpacity = interpolate(frame, [100, 115], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Badge "No commitment"
  const badgeSpring = spring({
    frame: frame - 120,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 25,
  });

  // Shimmer sweep
  const shimmerX = interpolate(frame, [140, 200], [-400, width + 400], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Logo in corner
  const logoOpacity = interpolate(frame, [60, 75], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const perimeterLength = (CALENDAR_SIZE + CALENDAR_SIZE) * 2;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      <Background accent={accent} />
      <CornerBrackets accent={accent} />

      {/* Calendar icon */}
      <div
        style={{
          position: 'absolute',
          left: centerX - CALENDAR_SIZE / 2,
          top: calendarY,
        }}
      >
        <svg width={CALENDAR_SIZE} height={CALENDAR_SIZE}>
          <rect
            x={8}
            y={30}
            width={CALENDAR_SIZE - 16}
            height={CALENDAR_SIZE - 38}
            rx={10}
            fill="none"
            stroke={accent}
            strokeWidth={2.5}
            strokeDasharray={perimeterLength}
            strokeDashoffset={perimeterLength * (1 - drawProgress)}
          />
          {/* Tabs */}
          <line
            x1={CALENDAR_SIZE * 0.35}
            y1={15}
            x2={CALENDAR_SIZE * 0.35}
            y2={42}
            stroke={accent}
            strokeWidth={3}
            strokeLinecap="round"
            opacity={drawProgress}
          />
          <line
            x1={CALENDAR_SIZE * 0.65}
            y1={15}
            x2={CALENDAR_SIZE * 0.65}
            y2={42}
            stroke={accent}
            strokeWidth={3}
            strokeLinecap="round"
            opacity={drawProgress}
          />
          {/* Header line */}
          <line
            x1={24}
            y1={60}
            x2={CALENDAR_SIZE - 24}
            y2={60}
            stroke={accent}
            strokeWidth={1.5}
            opacity={drawProgress * 0.5}
          />
          {/* Grid dots */}
          {Array.from({ length: 15 }).map((_, i) => {
            const col = i % 5;
            const row = Math.floor(i / 5);
            const dotOpacity = interpolate(
              drawProgress,
              [0.5, 0.7 + i * 0.01],
              [0, 0.3],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
            );
            return (
              <circle
                key={i}
                cx={35 + col * 28}
                cy={80 + row * 28}
                r={3.5}
                fill={COLORS.textMuted}
                opacity={dotOpacity}
              />
            );
          })}
          {/* Highlighted date */}
          <circle
            cx={91}
            cy={108}
            r={14}
            fill="none"
            stroke={accent}
            strokeWidth={2}
            opacity={highlightOpacity}
          />
          <circle
            cx={91}
            cy={108}
            r={14 + highlightPulse * 8}
            fill="none"
            stroke={accent}
            strokeWidth={1}
            opacity={highlightOpacity * (1 - highlightPulse * 0.5)}
          />
        </svg>
      </div>

      {/* Headline */}
      <div
        style={{
          position: 'absolute',
          top: calendarY + CALENDAR_SIZE + 40,
          left: 0,
          right: 0,
          textAlign: 'center',
          transform: `scale(${headlineSpring})`,
          opacity: headlineSpring,
        }}
      >
        <div
          style={{
            fontFamily: orbitronFamily,
            fontSize: isLandscape ? 44 : 38,
            fontWeight: 900,
            color: COLORS.textPrimary,
            lineHeight: 1.3,
            padding: '0 60px',
          }}
        >
          Book a Free{'\n'}Strategy Call
        </div>
      </div>

      {/* URL */}
      <div
        style={{
          position: 'absolute',
          top: calendarY + CALENDAR_SIZE + (isLandscape ? 150 : 160),
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: urlOpacity,
        }}
      >
        <div
          style={{
            fontFamily: syneFamily,
            fontSize: isLandscape ? 30 : 26,
            color: accent,
            fontWeight: 600,
          }}
        >
          hexaiagency.com
        </div>
      </div>

      {/* Handle */}
      <div
        style={{
          position: 'absolute',
          top: calendarY + CALENDAR_SIZE + (isLandscape ? 195 : 205),
          left: 0,
          right: 0,
          textAlign: 'center',
          opacity: handleOpacity,
        }}
      >
        <div
          style={{
            fontFamily: syneFamily,
            fontSize: 20,
            color: COLORS.textMuted,
          }}
        >
          @hexa_aiagency
        </div>
      </div>

      {/* No commitment badge */}
      <div
        style={{
          position: 'absolute',
          top: calendarY + CALENDAR_SIZE + (isLandscape ? 250 : 260),
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
            padding: '10px 28px',
            borderRadius: 24,
            border: `1px solid ${COLORS.textMuted}40`,
            fontFamily: syneFamily,
            fontSize: 18,
            color: COLORS.textMuted,
          }}
        >
          No commitment required
        </div>
      </div>

      {/* Logo in corner */}
      <div
        style={{
          position: 'absolute',
          bottom: isLandscape ? 30 : 50,
          right: isLandscape ? 40 : undefined,
          left: isLandscape ? undefined : 0,
          width: isLandscape ? undefined : '100%',
          display: 'flex',
          justifyContent: isLandscape ? 'flex-end' : 'center',
          opacity: logoOpacity,
        }}
      >
        <img
          src={staticFile('hexa.png')}
          style={{ width: 50, height: 50, objectFit: 'contain' }}
        />
      </div>

      {/* Shimmer sweep */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: shimmerX,
          width: 250,
          height: '100%',
          background: `linear-gradient(90deg, transparent, ${accent}10, transparent)`,
          transform: 'skewX(-15deg)',
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
