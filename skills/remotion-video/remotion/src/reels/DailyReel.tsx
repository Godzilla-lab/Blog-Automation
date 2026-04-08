import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import { BRollSlide } from './scenes/BRollSlide';
import { TalkingHeadSlide } from './scenes/TalkingHeadSlide';
import { SyncedCaptions, WordTimestamp } from './scenes/SyncedCaptions';

/**
 * Daily Reel — Config-driven short-form video.
 *
 * Takes a list of slides (text + footage) and renders them as
 * a punchy Reel with kinetic captions over stock b-roll video.
 *
 * Supports per-slide durations synced to voiceover timing.
 * Crossfade transitions between slides (15 frame overlap).
 * Handle watermark on every slide.
 */

const FPS = 30;
const TRANSITION_FRAMES = 15; // 0.5s crossfade

export interface SlideConfig {
  text: string;
  emphasis?: string;
  footage: string;
  type: 'broll' | 'talking_head' | 'cta';
}

export interface DailyReelProps {
  slides: SlideConfig[];
  secondsPerSlide: number;
  accentColor: string;
  handle: string;
  voiceover: string;
  wordTimestamps: WordTimestamp[];
  bgMusic: string;
  bgMusicVolume: number;
}

export const dailyReelDefaults: DailyReelProps = {
  slides: [
    {
      text: 'Your dental reminders are broken.',
      emphasis: 'broken',
      footage: 'footage/test-still.jpg',
      type: 'broll',
    },
  ],
  secondsPerSlide: 4,
  accentColor: '#FFD700',
  handle: '@hexa_aiagency',
  voiceover: '',
  wordTimestamps: [],
  bgMusic: '',
  bgMusicVolume: 0.15,
};

/** Wrapper that adds fade-in/fade-out opacity to a slide */
const FadeWrapper: React.FC<{
  durationInFrames: number;
  isFirst: boolean;
  isLast: boolean;
  children: React.ReactNode;
}> = ({ durationInFrames, isFirst, isLast, children }) => {
  const frame = useCurrentFrame();

  // Fade in over TRANSITION_FRAMES (skip for first slide)
  const fadeIn = isFirst
    ? 1
    : interpolate(frame, [0, TRANSITION_FRAMES], [0, 1], {
        extrapolateRight: 'clamp',
      });

  // Fade out over TRANSITION_FRAMES (skip for last slide)
  const fadeOut = isLast
    ? 1
    : interpolate(
        frame,
        [durationInFrames - TRANSITION_FRAMES, durationInFrames],
        [1, 0],
        { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
      );

  return (
    <AbsoluteFill style={{ opacity: fadeIn * fadeOut }}>
      {children}
    </AbsoluteFill>
  );
};

export const DailyReel: React.FC<DailyReelProps> = ({
  slides = dailyReelDefaults.slides,
  secondsPerSlide = dailyReelDefaults.secondsPerSlide,
  accentColor = dailyReelDefaults.accentColor,
  handle = dailyReelDefaults.handle,
  voiceover = dailyReelDefaults.voiceover,
  wordTimestamps = dailyReelDefaults.wordTimestamps,
  bgMusic = dailyReelDefaults.bgMusic,
  bgMusicVolume = dailyReelDefaults.bgMusicVolume,
}) => {
  const framesPerSlide = secondsPerSlide * FPS;
  const getSlideFrames = (_i: number) => framesPerSlide;

  // Calculate cumulative start frames with crossfade overlap
  const slideStarts: number[] = [];
  let offset = 0;
  for (let i = 0; i < slides.length; i++) {
    slideStarts.push(offset);
    const frames = getSlideFrames(i);
    // Subtract overlap for crossfade (except after last slide)
    offset += frames - (i < slides.length - 1 ? TRANSITION_FRAMES : 0);
  }

  return (
    <AbsoluteFill style={{ backgroundColor: '#000000' }}>
      {/* Voiceover audio */}
      {voiceover && (
        <Audio
          src={staticFile(voiceover)}
          volume={1}
          placeholder={undefined as any}
          onPointerEnterCapture={undefined as any}
          onPointerLeaveCapture={undefined as any}
        />
      )}

      {/* Background music (low volume under voiceover) */}
      {bgMusic && (
        <Audio
          src={staticFile(bgMusic)}
          volume={bgMusicVolume}
          loop
          placeholder={undefined as any}
          onPointerEnterCapture={undefined as any}
          onPointerLeaveCapture={undefined as any}
        />
      )}

      {/* Slide sequences with crossfade transitions */}
      {slides.map((slide, i) => {
        const from = slideStarts[i];
        const durationInFrames = getSlideFrames(i);
        const isFirst = i === 0;
        const isLast = i === slides.length - 1;

        const SlideComponent = slide.type === 'talking_head' ? TalkingHeadSlide : BRollSlide;

        return (
          <Sequence
            key={i}
            from={from}
            durationInFrames={durationInFrames}
            name={`Slide ${i + 1}`}
          >
            <FadeWrapper
              durationInFrames={durationInFrames}
              isFirst={isFirst}
              isLast={isLast}
            >
              <SlideComponent
                text={slide.text}
                emphasis={slide.emphasis}
                footageSrc={slide.footage}
                accentColor={accentColor}
                handle={handle}
              />
            </FadeWrapper>
          </Sequence>
        );
      })}

      {/* Synced captions layer — on top of everything, runs for full duration */}
      {wordTimestamps && wordTimestamps.length > 0 && (
        <SyncedCaptions
          wordTimestamps={wordTimestamps}
          accentColor={accentColor}
        />
      )}
    </AbsoluteFill>
  );
};
