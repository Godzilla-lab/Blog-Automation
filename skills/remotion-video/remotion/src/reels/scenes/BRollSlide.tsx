import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { bebasFamily } from '../../lib/fonts';
import { FootageBackground } from './FootageBackground';

/**
 * B-Roll Slide: Full-screen background image with darkened overlay + kinetic text.
 * Text appears word-by-word, emphasis word in accent color.
 * Ken Burns zoom effect gives static images a cinematic feel.
 *
 * Footage supports both video (.mp4) and still images (.jpg).
 * OffthreadVideo decodes video via FFmpeg, bypassing Chrome limitations.
 */

interface BRollSlideProps {
  text: string;
  emphasis?: string;
  footageSrc?: string;
  footageSrcs?: string[];
  durationInFrames?: number;
  accentColor: string;
  handle?: string;
}

export const BRollSlide: React.FC<BRollSlideProps> = ({
  text,
  emphasis,
  footageSrc,
  footageSrcs,
  durationInFrames,
  accentColor,
  handle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const words = text.split(' ');

  // Subtle zoom on background image (Ken Burns effect)
  const zoom = interpolate(frame, [0, fps * 4], [1.0, 1.08], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill>
      {/* Background footage with slow zoom (Ken Burns effect) */}
      <FootageBackground
        src={footageSrc}
        srcs={footageSrcs}
        durationInFrames={durationInFrames}
        style={{
          transform: `scale(${zoom})`,
        }}
      />

      {/* Dark overlay for text readability */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.55)',
        }}
      />

      {/* Kinetic text — centered */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 60px',
        }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '8px 16px',
            lineHeight: 1.2,
          }}
        >
          {words.map((word, i) => {
            const wordSpring = spring({
              frame: frame - i * 1,
              fps,
              config: { mass: 1, damping: 20, stiffness: 150 },
              durationInFrames: 15,
            });

            const isEmphasis =
              emphasis &&
              word.toUpperCase().replace(/[^A-Z0-9]/g, '') ===
                emphasis.toUpperCase().replace(/[^A-Z0-9]/g, '');

            return (
              <span
                key={i}
                style={{
                  fontFamily: bebasFamily,
                  fontSize: 82,
                  fontWeight: 400, // Bebas Neue only has 400
                  color: isEmphasis ? accentColor : '#ffffff',
                  textTransform: 'uppercase',
                  letterSpacing: 3,
                  opacity: wordSpring,
                  transform: `translateY(${(1 - wordSpring) * 30}px)`,
                  display: 'inline-block',
                  textShadow: isEmphasis
                    ? `0 0 20px ${accentColor}80, 2px 2px 0 rgba(0,0,0,0.8)`
                    : '2px 2px 0 rgba(0,0,0,0.8)',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>

      {/* Handle watermark — bottom right */}
      {handle && (
        <div
          style={{
            position: 'absolute',
            bottom: 40,
            right: 30,
            fontFamily: bebasFamily,
            fontSize: 22,
            color: 'rgba(255, 255, 255, 0.5)',
            letterSpacing: 2,
          }}
        >
          {handle}
        </div>
      )}

    </AbsoluteFill>
  );
};
