import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { BRollSlide } from './scenes/BRollSlide';
import { TalkingHeadSlide } from './scenes/TalkingHeadSlide';
import { SyncedCaptions, WordTimestamp } from './scenes/SyncedCaptions';

/**
 * Daily Reel — Config-driven short-form video.
 *
 * Takes a list of slides (text + footage) and renders them as
 * a punchy 15-30 second Reel with kinetic captions over stock b-roll.
 *
 * Each slide gets `secondsPerSlide` seconds (default 4).
 * Text appears word-by-word with spring animations.
 * Hard cuts between slides (no transitions).
 *
 * Optional voiceover + synced captions: when `wordTimestamps` is provided,
 * word-by-word captions are overlaid at the bottom of the screen,
 * synced to the voiceover audio. The per-slide kinetic text still shows
 * but the synced captions provide the continuous subtitle experience.
 */

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
  const framesPerSlide = secondsPerSlide * 30; // 30fps

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

      {/* Slide sequences */}
      {slides.map((slide, i) => {
        const from = i * framesPerSlide;

        return (
          <Sequence
            key={i}
            from={from}
            durationInFrames={framesPerSlide}
            name={`Slide ${i + 1}`}
          >
            {slide.type === 'talking_head' ? (
              <TalkingHeadSlide
                text={slide.text}
                emphasis={slide.emphasis}
                footageSrc={slide.footage}
                accentColor={accentColor}
                handle={handle}
              />
            ) : (
              <BRollSlide
                text={slide.text}
                emphasis={slide.emphasis}
                footageSrc={slide.footage}
                accentColor={accentColor}
                handle={handle}
              />
            )}
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
