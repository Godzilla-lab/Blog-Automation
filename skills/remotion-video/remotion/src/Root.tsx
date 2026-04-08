import React from 'react';
import { Composition } from 'remotion';
import { WIDTH, HEIGHT, FPS, DURATION, LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT } from './brand';
import { Results } from './highlights/Results';
import { Services } from './highlights/Services';
import { HowItWorks } from './highlights/HowItWorks';
import { FAQ } from './highlights/FAQ';
import { BookACall } from './highlights/BookACall';
import { Launch } from './reels/Launch';
import { DailyReel, DailyReelProps, dailyReelDefaults } from './reels/DailyReel';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Daily Reel — 15-30s+, 9:16 portrait, props via --props flag */}
      <Composition
        id="DailyReel"
        component={DailyReel as any}
        durationInFrames={960}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={dailyReelDefaults as unknown as Record<string, unknown>}
        calculateMetadata={({ props }: { props: Record<string, unknown> }) => {
          const slides = (props.slides ?? dailyReelDefaults.slides) as DailyReelProps['slides'];
          const sps = (props.secondsPerSlide ?? dailyReelDefaults.secondsPerSlide) as number;
          const TRANSITION = 15; // must match TRANSITION_FRAMES in DailyReel
          const totalFrames = slides.length * sps * FPS - (slides.length - 1) * TRANSITION;
          return { durationInFrames: totalFrames, props };
        }}
      />

      {/* Launch Video — 90 seconds, 16:9 landscape */}
      <Composition
        id="Launch"
        component={Launch}
        durationInFrames={2700}
        fps={FPS}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />

      {/* Story Highlights — 6 seconds, 9:16 portrait */}
      <Composition
        id="Results"
        component={Results}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="Services"
        component={Services}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="HowItWorks"
        component={HowItWorks}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="FAQ"
        component={FAQ}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="BookACall"
        component={BookACall}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
