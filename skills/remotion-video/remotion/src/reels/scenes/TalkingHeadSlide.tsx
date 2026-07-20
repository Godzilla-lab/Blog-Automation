import React from 'react';
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { bebasFamily } from '../../lib/fonts';
import { FootageBackground } from './FootageBackground';

/**
 * Talking Head Slide: Speaker image fills screen, kinetic text overlaid above.
 * Text appears on a semi-transparent dark banner for readability.
 */

interface TalkingHeadSlideProps {
  text: string;
  emphasis?: string;
  footageSrc?: string;
  footageSrcs?: string[];
  durationInFrames?: number;
  accentColor: string;
  handle?: string;
}

export const TalkingHeadSlide: React.FC<TalkingHeadSlideProps> = ({
  text,
  emphasis,
  footageSrc,
  footageSrcs,
  durationInFrames,
  accentColor,
  handle,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const words = text.split(' ');

  // Text banner slide-in
  const bannerSpring = spring({
    frame: frame - 3,
    fps,
    config: { mass: 1, damping: 22, stiffness: 120 },
    durationInFrames: 20,
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#000000' }}>
      {/* Talking head footage — fills the frame */}
      <FootageBackground
        src={footageSrc}
        srcs={footageSrcs}
        durationInFrames={durationInFrames}
      />

      {/* Text banner — top portion */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: height * 0.35,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 50px',
          opacity: bannerSpring,
          transform: `translateY(${(1 - bannerSpring) * -40}px)`,
        }}
      >
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: '6px 14px',
            lineHeight: 1.2,
          }}
        >
          {words.map((word, i) => {
            const wordSpring = spring({
              frame: frame - 10 - i * 2,
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
                  fontSize: 72,
                  fontWeight: 400,
                  color: isEmphasis ? accentColor : '#ffffff',
                  textTransform: 'uppercase',
                  letterSpacing: 3,
                  opacity: wordSpring,
                  transform: `translateY(${(1 - wordSpring) * 20}px)`,
                  display: 'inline-block',
                  textShadow: isEmphasis
                    ? `0 0 15px ${accentColor}60`
                    : 'none',
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </div>

      {/* Handle watermark */}
      {handle && (
        <div
          style={{
            position: 'absolute',
            bottom: 40,
            right: 30,
            fontFamily: bebasFamily,
            fontSize: 22,
            color: 'rgba(255, 255, 255, 0.4)',
            letterSpacing: 2,
          }}
        >
          {handle}
        </div>
      )}
    </AbsoluteFill>
  );
};
