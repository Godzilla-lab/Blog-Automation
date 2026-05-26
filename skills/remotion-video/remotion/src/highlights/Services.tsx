import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG, STAGGER, WIDTH, HEIGHT } from '../brand';
import { Background } from '../components/shared/Background';
import { LogoBadge } from '../components/shared/LogoBadge';
import { CornerBrackets } from '../components/shared/CornerBrackets';
import { HighlightLabel } from '../components/shared/HighlightLabel';
import { syneFamily } from '../lib/fonts';

const CENTER_X = WIDTH / 2;
const CENTER_Y = HEIGHT / 2 - 60;
const HEX_RADIUS = 80;
const ORBIT_RADIUS = 260;

const SERVICES = [
  { label: 'AI Assistants', angle: -90 },
  { label: 'Lead Generation', angle: 150 },
  { label: 'Workflow\nAutomation', angle: 30 },
];

// Hexagon points helper
const hexPoints = (cx: number, cy: number, r: number): string => {
  return Array.from({ length: 6 })
    .map((_, i) => {
      const angleDeg = 60 * i - 30;
      const angleRad = (Math.PI / 180) * angleDeg;
      return `${cx + r * Math.cos(angleRad)},${cy + r * Math.sin(angleRad)}`;
    })
    .join(' ');
};

export const Services: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = COLORS.secondary;

  // Gear rotation
  const rotation = interpolate(frame, [0, 180], [0, 30], {
    extrapolateRight: 'clamp',
  });

  // Gear scale in
  const gearScale = spring({
    frame: frame - 20,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 35,
  });

  return (
    <AbsoluteFill>
      <Background accent={accent} />
      <LogoBadge />
      <CornerBrackets accent={accent} />

      {/* Central hexagonal gear */}
      <div
        style={{
          position: 'absolute',
          left: CENTER_X - HEX_RADIUS - 20,
          top: CENTER_Y - HEX_RADIUS - 20,
          width: (HEX_RADIUS + 20) * 2,
          height: (HEX_RADIUS + 20) * 2,
          transform: `scale(${gearScale}) rotate(${rotation}deg)`,
        }}
      >
        <svg width={(HEX_RADIUS + 20) * 2} height={(HEX_RADIUS + 20) * 2}>
          {/* Outer hex (gear teeth effect) */}
          <polygon
            points={hexPoints(HEX_RADIUS + 20, HEX_RADIUS + 20, HEX_RADIUS + 15)}
            fill="none"
            stroke={accent}
            strokeWidth={2}
            opacity={0.3}
          />
          {/* Inner hex */}
          <polygon
            points={hexPoints(HEX_RADIUS + 20, HEX_RADIUS + 20, HEX_RADIUS)}
            fill={`${accent}15`}
            stroke={accent}
            strokeWidth={2.5}
          />
          {/* Center dot */}
          <circle
            cx={HEX_RADIUS + 20}
            cy={HEX_RADIUS + 20}
            r={8}
            fill={accent}
          />
        </svg>
      </div>

      {/* Service labels orbiting */}
      {SERVICES.map((service, i) => {
        const labelSpring = spring({
          frame: frame - 45 - i * (STAGGER + 2),
          fps,
          config: SPRING_CONFIG,
          durationInFrames: 35,
        });

        const angleRad = (Math.PI / 180) * service.angle;
        const x = CENTER_X + ORBIT_RADIUS * Math.cos(angleRad);
        const y = CENTER_Y + ORBIT_RADIUS * Math.sin(angleRad);

        // Connector line progress
        const lineProgress = interpolate(
          frame,
          [55 + i * (STAGGER + 2), 70 + i * (STAGGER + 2)],
          [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        return (
          <React.Fragment key={i}>
            {/* Connector line */}
            <svg
              width={WIDTH}
              height={HEIGHT}
              style={{ position: 'absolute', top: 0, left: 0 }}
            >
              <line
                x1={CENTER_X}
                y1={CENTER_Y}
                x2={CENTER_X + (x - CENTER_X) * lineProgress}
                y2={CENTER_Y + (y - CENTER_Y) * lineProgress}
                stroke={accent}
                strokeWidth={1.5}
                opacity={0.4}
              />
            </svg>

            {/* Glowing dot at connection point */}
            <div
              style={{
                position: 'absolute',
                left: x - 5,
                top: y - 5,
                width: 10,
                height: 10,
                borderRadius: '50%',
                backgroundColor: accent,
                boxShadow: `0 0 12px ${accent}`,
                opacity: lineProgress,
              }}
            />

            {/* Label */}
            <div
              style={{
                position: 'absolute',
                left: x - 120,
                top: y + 18,
                width: 240,
                textAlign: 'center',
                fontFamily: syneFamily,
                fontSize: 28,
                fontWeight: 600,
                color: COLORS.textPrimary,
                opacity: labelSpring,
                transform: `scale(${labelSpring})`,
                whiteSpace: 'pre-line',
                lineHeight: 1.2,
              }}
            >
              {service.label}
            </div>
          </React.Fragment>
        );
      })}

      <HighlightLabel text="Services" accent={accent} />
    </AbsoluteFill>
  );
};
