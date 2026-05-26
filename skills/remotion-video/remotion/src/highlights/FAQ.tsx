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

const accent = COLORS.faqAccent;

const QUESTIONS = [
  { text: 'Need tech skills?', startX: -200, startY: 700 },
  { text: 'How long to build?', startX: WIDTH + 200, startY: 780 },
  { text: 'What ROI can I expect?', startX: -200, startY: 960 },
  { text: 'Accurate AI chatbots?', startX: WIDTH + 200, startY: 1040 },
];

const QUESTION_CENTER_X = WIDTH / 2;

export const FAQ: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Question mark scale
  const qScale = spring({
    frame: frame - 15,
    fps,
    config: { mass: 1, damping: 14, stiffness: 100 },
    durationInFrames: 40,
  });

  // Question mark glow pulse
  const glowIntensity = interpolate(frame, [0, 90, 180], [0.4, 0.8, 0.4], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      <Background accent={accent} />
      <LogoBadge />
      <CornerBrackets accent={accent} />

      {/* Large question mark */}
      <div
        style={{
          position: 'absolute',
          top: 380,
          left: 0,
          right: 0,
          textAlign: 'center',
          transform: `scale(${qScale})`,
        }}
      >
        <span
          style={{
            fontFamily: orbitronFamily,
            fontSize: 240,
            fontWeight: 900,
            color: accent,
            textShadow: `0 0 ${40 * glowIntensity}px ${accent}, 0 0 ${80 * glowIntensity}px ${accent}40`,
          }}
        >
          ?
        </span>
      </div>

      {/* Question bubbles */}
      {QUESTIONS.map((q, i) => {
        const delay = 50 + i * (STAGGER + 2);

        const slideProgress = spring({
          frame: frame - delay,
          fps,
          config: SPRING_CONFIG,
          durationInFrames: 35,
        });

        const targetX = i % 2 === 0 ? QUESTION_CENTER_X - 30 : QUESTION_CENTER_X + 30;
        const currentX = interpolate(slideProgress, [0, 1], [q.startX, targetX]);

        // Subtle float
        const floatY = Math.sin((frame + i * 20) * 0.04) * 4;

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: currentX - 200,
              top: q.startY + floatY,
              width: 400,
              textAlign: 'center',
              opacity: slideProgress,
            }}
          >
            <div
              style={{
                display: 'inline-block',
                padding: '16px 32px',
                borderRadius: 16,
                border: `1.5px solid ${accent}60`,
                backgroundColor: `${accent}08`,
                fontFamily: syneFamily,
                fontSize: 26,
                color: COLORS.textPrimary,
                backdropFilter: 'blur(4px)',
              }}
            >
              {q.text}
            </div>
          </div>
        );
      })}

      <HighlightLabel text="FAQ" accent={accent} />
    </AbsoluteFill>
  );
};
