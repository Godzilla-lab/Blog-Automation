import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS } from '../../brand';
import { KineticText } from '../../components/shared/KineticText';

/**
 * Scene 1: Hook (0-5s = 150 frames)
 * Dark background with glitch-style kinetic text.
 * "Your business is leaking money."
 * Red/orange danger accent.
 */

const ALERT_COLOR = '#ff4444';

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  // Scanline effect
  const scanlineY = (frame * 8) % height;

  // Flash on entry
  const flashOpacity = interpolate(frame, [0, 6, 12], [0.6, 0, 0], {
    extrapolateRight: 'clamp',
  });

  // Glitch bars that appear randomly
  const glitchBars = [
    { y: 0.2, width: 0.6, delay: 20, duration: 4 },
    { y: 0.5, width: 0.3, delay: 45, duration: 3 },
    { y: 0.75, width: 0.45, delay: 80, duration: 5 },
    { y: 0.35, width: 0.5, delay: 110, duration: 3 },
  ];

  // Pulsing vignette
  const vignetteIntensity = interpolate(
    frame,
    [0, 75, 150],
    [0.3, 0.5, 0.6],
    { extrapolateRight: 'clamp' },
  );

  // Warning icon pulse
  const warningScale = interpolate(
    frame % 30,
    [0, 15, 30],
    [1, 1.1, 1],
    { extrapolateRight: 'clamp' },
  );
  const warningOpacity = interpolate(frame, [10, 25], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {/* Red vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(ellipse at center, transparent 30%, ${ALERT_COLOR}${Math.round(vignetteIntensity * 25).toString(16).padStart(2, '0')} 100%)`,
        }}
      />

      {/* Scanline */}
      <div
        style={{
          position: 'absolute',
          top: scanlineY,
          left: 0,
          width: '100%',
          height: 2,
          backgroundColor: `${ALERT_COLOR}15`,
        }}
      />

      {/* Glitch bars */}
      {glitchBars.map((bar, i) => {
        const visible =
          frame >= bar.delay && frame < bar.delay + bar.duration;
        if (!visible) return null;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: bar.y * height,
              left: 0,
              width: bar.width * width,
              height: 3,
              backgroundColor: `${ALERT_COLOR}30`,
              transform: `translateX(${(1 - bar.width) * width * 0.5}px)`,
            }}
          />
        );
      })}

      {/* Warning triangle icon */}
      <div
        style={{
          position: 'absolute',
          top: height * 0.28,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          opacity: warningOpacity,
          transform: `scale(${warningScale})`,
        }}
      >
        <svg width={80} height={72} viewBox="0 0 80 72">
          <polygon
            points="40,4 76,68 4,68"
            fill="none"
            stroke={ALERT_COLOR}
            strokeWidth={3}
            strokeLinejoin="round"
          />
          <text
            x={40}
            y={56}
            textAnchor="middle"
            fill={ALERT_COLOR}
            fontSize={36}
            fontWeight={900}
          >
            !
          </text>
        </svg>
      </div>

      {/* Main kinetic text */}
      <div
        style={{
          position: 'absolute',
          top: height * 0.38,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <KineticText
          text="Your business is leaking money."
          emphasisWord="leaking"
          fontSize={width > height ? 72 : 64}
          startFrame={15}
          accent={ALERT_COLOR}
          wordDelay={4}
          maxWidth={width * 0.8}
        />
      </div>

      {/* Flash overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: ALERT_COLOR,
          opacity: flashOpacity,
          pointerEvents: 'none',
        }}
      />
    </AbsoluteFill>
  );
};
