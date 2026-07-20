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
import { SabiDashboard } from './explainer/SabiDashboard';
import { SabiWorkflow } from './explainer/SabiWorkflow';
import { SabiUiAd } from './explainer/SabiUiAd';
import { SabiExplainer, EXPLAINER_FRAMES } from './explainer/SabiExplainer';
import { SabiLogoReveal } from './explainer/SabiLogoReveal';
import { SabiStory, STORY_FRAMES } from './explainer/SabiStory';
import { SabiStoryVertical } from './explainer/SabiStoryVertical';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Sabi "One Story" — MacBook Apple-style explainer, 16:9, ~41s */}
      <Composition
        id="SabiStory"
        component={SabiStory}
        durationInFrames={STORY_FRAMES}
        fps={30}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />

      {/* Sabi "One Story" — 9:16 vertical cut */}
      <Composition
        id="SabiStoryVertical"
        component={SabiStoryVertical}
        durationInFrames={STORY_FRAMES}
        fps={30}
        width={WIDTH}
        height={HEIGHT}
      />

      {/* Sabi full explainer — 3 scenes + VO + ambient bed + SFX, 16:9, ~35s */}
      <Composition
        id="SabiExplainer"
        component={SabiExplainer}
        durationInFrames={EXPLAINER_FRAMES}
        fps={30}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />
      {/* Sabi explainer scenes (standalone) */}
      <Composition
        id="SabiDashboard"
        component={SabiDashboard}
        durationInFrames={330}
        fps={30}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />
      <Composition
        id="SabiWorkflow"
        component={SabiWorkflow}
        durationInFrames={345}
        fps={30}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />
      <Composition
        id="SabiUiAd"
        component={SabiUiAd}
        durationInFrames={375}
        fps={30}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />
      <Composition
        id="SabiLogoReveal"
        component={SabiLogoReveal}
        durationInFrames={165}
        fps={30}
        width={LANDSCAPE_WIDTH}
        height={LANDSCAPE_HEIGHT}
      />
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
          const framesPerSlide = sps * FPS;
          const sumDurations = slides.reduce(
            (acc, s) => acc + ((s as { durationFrames?: number }).durationFrames ?? framesPerSlide),
            0,
          );
          const totalFrames = sumDurations - (slides.length - 1) * TRANSITION;
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
