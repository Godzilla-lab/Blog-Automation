import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, HEIGHT, SPRING_CONFIG, STAGGER, WIDTH } from '../brand';
import { Background } from '../components/shared/Background';
import { LogoBadge } from '../components/shared/LogoBadge';
import { CornerBrackets } from '../components/shared/CornerBrackets';
import { HighlightLabel } from '../components/shared/HighlightLabel';
import { orbitronFamily, syneFamily } from '../lib/fonts';

const BAR_DATA = [
  { height: 120, delay: 0 },
  { height: 180, delay: 1 },
  { height: 140, delay: 2 },
  { height: 220, delay: 3 },
  { height: 280, delay: 4 },
];

const BAR_WIDTH = 60;
const BAR_GAP = 28;
const CHART_BOTTOM = 950;

const STATS = [
  { value: '80%', label: 'Sales Increase', delay: 90 },
  { value: '90%+', label: 'Attribution Accuracy', delay: 100 },
];

export const Results: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const accent = COLORS.primary;

  const totalBarsWidth = BAR_DATA.length * BAR_WIDTH + (BAR_DATA.length - 1) * BAR_GAP;
  const chartLeft = (WIDTH - totalBarsWidth) / 2;

  // Trend arrow
  const arrowProgress = interpolate(frame, [50, 80], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      <Background accent={accent} />
      <LogoBadge />
      <CornerBrackets accent={accent} />

      {/* Bar chart */}
      {BAR_DATA.map((bar, i) => {
        const barSpring = spring({
          frame: frame - 25 - i * STAGGER,
          fps,
          config: SPRING_CONFIG,
          durationInFrames: 40,
        });

        const barHeight = bar.height * barSpring;
        const x = chartLeft + i * (BAR_WIDTH + BAR_GAP);

        return (
          <React.Fragment key={i}>
            {/* Bar */}
            <div
              style={{
                position: 'absolute',
                left: x,
                bottom: HEIGHT - CHART_BOTTOM,
                width: BAR_WIDTH,
                height: barHeight,
                borderRadius: 6,
                background: `linear-gradient(to top, ${accent}40, ${accent})`,
              }}
            />
            {/* Glowing top edge */}
            <div
              style={{
                position: 'absolute',
                left: x,
                bottom: HEIGHT - CHART_BOTTOM + barHeight - 3,
                width: BAR_WIDTH,
                height: 3,
                backgroundColor: accent,
                boxShadow: `0 0 12px ${accent}, 0 0 24px ${accent}60`,
                borderRadius: 2,
                opacity: barSpring,
              }}
            />
          </React.Fragment>
        );
      })}

      {/* Trend arrow SVG */}
      <svg
        width={totalBarsWidth + 40}
        height={200}
        style={{
          position: 'absolute',
          left: chartLeft - 20,
          top: CHART_BOTTOM - 320,
        }}
      >
        <line
          x1={0}
          y1={180}
          x2={(totalBarsWidth + 40) * arrowProgress}
          y2={180 - 150 * arrowProgress}
          stroke={accent}
          strokeWidth={2.5}
          strokeDasharray="8 4"
          opacity={0.7}
        />
        {arrowProgress > 0.9 && (
          <polygon
            points={`${totalBarsWidth + 40},30 ${totalBarsWidth + 25},50 ${totalBarsWidth + 35},45`}
            fill={accent}
            opacity={arrowProgress}
          />
        )}
      </svg>

      {/* Stats */}
      {STATS.map((stat, i) => {
        const statOpacity = interpolate(frame, [stat.delay, stat.delay + 15], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const statY = interpolate(frame, [stat.delay, stat.delay + 15], [20, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: 1050 + i * 120,
              left: 0,
              right: 0,
              textAlign: 'center',
              opacity: statOpacity,
              transform: `translateY(${statY}px)`,
            }}
          >
            <div
              style={{
                fontFamily: orbitronFamily,
                fontSize: 64,
                fontWeight: 900,
                color: accent,
                textShadow: `0 0 30px ${accent}60`,
              }}
            >
              {stat.value}
            </div>
            <div
              style={{
                fontFamily: syneFamily,
                fontSize: 28,
                color: COLORS.textMuted,
                marginTop: 4,
              }}
            >
              {stat.label}
            </div>
          </div>
        );
      })}

      {/* Floating particles */}
      {Array.from({ length: 12 }).map((_, i) => {
        const x = 100 + (i * 83) % (WIDTH - 200);
        const startY = 1600 + (i * 37) % 200;
        const speed = 0.5 + (i % 3) * 0.3;
        const y = startY - frame * speed;
        const particleOpacity = interpolate(
          y,
          [400, 600, 1400, 1600],
          [0, 0.3, 0.3, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y % HEIGHT < 0 ? (y % HEIGHT) + HEIGHT : y % HEIGHT,
              width: 3,
              height: 3,
              borderRadius: '50%',
              backgroundColor: accent,
              opacity: particleOpacity,
            }}
          />
        );
      })}

      <HighlightLabel text="Results" accent={accent} />
    </AbsoluteFill>
  );
};
