import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { orbitronFamily } from '../../lib/fonts';

interface KineticTextProps {
  text: string;
  /** Word to highlight with accent color + glow */
  emphasisWord?: string;
  fontSize?: number;
  startFrame?: number;
  accent?: string;
  /** Frames between each word appearing */
  wordDelay?: number;
  fontFamily?: string;
  fontWeight?: number;
  lineHeight?: number;
  maxWidth?: number;
}

export const KineticText: React.FC<KineticTextProps> = ({
  text,
  emphasisWord,
  fontSize = 64,
  startFrame = 0,
  accent = COLORS.primary,
  wordDelay = 3,
  fontFamily = orbitronFamily,
  fontWeight = 900,
  lineHeight = 1.3,
  maxWidth,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(' ');

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: `0 ${fontSize * 0.3}px`,
        maxWidth: maxWidth || '85%',
        lineHeight,
      }}
    >
      {words.map((word, i) => {
        const wordFrame = startFrame + i * wordDelay;
        const wordSpring = spring({
          frame: frame - wordFrame,
          fps,
          config: { ...SPRING_CONFIG, stiffness: 120 },
          durationInFrames: 20,
        });

        const isEmphasis =
          emphasisWord &&
          word.toLowerCase().replace(/[^a-z]/g, '') ===
            emphasisWord.toLowerCase().replace(/[^a-z]/g, '');

        const wordColor = isEmphasis ? accent : COLORS.textPrimary;
        const glowStyle = isEmphasis
          ? { textShadow: `0 0 30px ${accent}, 0 0 60px ${accent}40` }
          : {};

        return (
          <span
            key={i}
            style={{
              fontFamily,
              fontSize,
              fontWeight,
              color: wordColor,
              opacity: wordSpring,
              transform: `translateY(${(1 - wordSpring) * 20}px) scale(${0.8 + wordSpring * 0.2})`,
              display: 'inline-block',
              ...glowStyle,
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
