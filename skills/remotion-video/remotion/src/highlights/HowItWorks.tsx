import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG, STAGGER, WIDTH } from '../brand';
import { Background } from '../components/shared/Background';
import { LogoBadge } from '../components/shared/LogoBadge';
import { CornerBrackets } from '../components/shared/CornerBrackets';
import { HighlightLabel } from '../components/shared/HighlightLabel';
import { orbitronFamily, syneFamily } from '../lib/fonts';

const accent = COLORS.purple;

const STEPS = [
  { num: '1', label: 'FREE CALL' },
  { num: '2', label: 'WE MAP' },
  { num: '3', label: 'WE BUILD' },
];

const CIRCLE_RADIUS = 48;
const STEP_Y = 860;
const STEP_SPACING = 280;

export const HowItWorks: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startX = (WIDTH - (STEPS.length - 1) * STEP_SPACING) / 2;

  // Pulse that travels along connector
  const pulseProgress = interpolate(
    frame % 120, // Loop every 4 seconds
    [0, 120],
    [0, 1],
    { extrapolateRight: 'clamp' }
  );

  return (
    <AbsoluteFill>
      <Background accent={accent} />
      <LogoBadge />
      <CornerBrackets accent={accent} />

      {/* Dashed connectors between circles */}
      {STEPS.slice(0, -1).map((_, i) => {
        const lineStart = 40 + i * STAGGER * 2;
        const lineProgress = interpolate(frame, [lineStart, lineStart + 25], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        const x1 = startX + i * STEP_SPACING + CIRCLE_RADIUS + 12;
        const x2 = startX + (i + 1) * STEP_SPACING - CIRCLE_RADIUS - 12;

        return (
          <React.Fragment key={`line-${i}`}>
            <svg
              width={WIDTH}
              height={40}
              style={{ position: 'absolute', top: STEP_Y - 2, left: 0 }}
            >
              <line
                x1={x1}
                y1={20}
                x2={x1 + (x2 - x1) * lineProgress}
                y2={20}
                stroke={accent}
                strokeWidth={2}
                strokeDasharray="8 6"
                opacity={0.6}
              />
            </svg>

            {/* Glowing pulse traveling along line */}
            {lineProgress >= 1 && (
              <div
                style={{
                  position: 'absolute',
                  left:
                    x1 +
                    (x2 - x1) *
                      Math.max(0, Math.min(1, (pulseProgress - i * 0.33) / 0.33)),
                  top: STEP_Y - 4,
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: accent,
                  boxShadow: `0 0 16px ${accent}, 0 0 32px ${accent}60`,
                  opacity: 0.8,
                }}
              />
            )}
          </React.Fragment>
        );
      })}

      {/* Step circles and labels */}
      {STEPS.map((step, i) => {
        const circleSpring = spring({
          frame: frame - 25 - i * STAGGER * 2,
          fps,
          config: SPRING_CONFIG,
          durationInFrames: 35,
        });

        const labelOpacity = interpolate(
          frame,
          [55 + i * STAGGER * 2, 70 + i * STAGGER * 2],
          [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        const labelY = interpolate(
          frame,
          [55 + i * STAGGER * 2, 70 + i * STAGGER * 2],
          [15, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        const cx = startX + i * STEP_SPACING;

        return (
          <React.Fragment key={i}>
            {/* Circle */}
            <div
              style={{
                position: 'absolute',
                left: cx - CIRCLE_RADIUS,
                top: STEP_Y - CIRCLE_RADIUS,
                width: CIRCLE_RADIUS * 2,
                height: CIRCLE_RADIUS * 2,
                borderRadius: '50%',
                border: `2.5px solid ${accent}`,
                backgroundColor: `${accent}10`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transform: `scale(${circleSpring})`,
                boxShadow: `0 0 20px ${accent}30`,
              }}
            >
              <span
                style={{
                  fontFamily: orbitronFamily,
                  fontSize: 40,
                  fontWeight: 900,
                  color: accent,
                }}
              >
                {step.num}
              </span>
            </div>

            {/* Label below */}
            <div
              style={{
                position: 'absolute',
                left: cx - 100,
                top: STEP_Y + CIRCLE_RADIUS + 24,
                width: 200,
                textAlign: 'center',
                fontFamily: syneFamily,
                fontSize: 26,
                fontWeight: 600,
                color: COLORS.textPrimary,
                letterSpacing: 2,
                opacity: labelOpacity,
                transform: `translateY(${labelY}px)`,
              }}
            >
              {step.label}
            </div>
          </React.Fragment>
        );
      })}

      <HighlightLabel text="How It Works" accent={accent} />
    </AbsoluteFill>
  );
};
