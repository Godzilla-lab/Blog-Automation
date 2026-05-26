import React from 'react';
import { AbsoluteFill, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { SFX } from '../lib/remotion-compat';
import { COLORS } from '../brand';
import { HookScene } from './scenes/HookScene';
import { ProblemScene } from './scenes/ProblemScene';
import { LogoRevealScene } from './scenes/LogoRevealScene';
import { ServicesScene } from './scenes/ServicesScene';
import { ResultsScene } from './scenes/ResultsScene';
import { CTAScene } from './scenes/CTAScene';

/**
 * Hexa AI Agency — Launch Video
 * 90 seconds @ 30fps = 2700 frames
 *
 * Scene timeline:
 *   1. Hook         0-5s    (0-150)     "Your business is leaking money."
 *   2. Problem      5-18s   (150-540)   Stat cards with red accent
 *   3. Logo Reveal  18-28s  (540-840)   Brand space transition + tagline
 *   4. Services     28-58s  (840-1740)  3 service blocks, 10s each
 *   5. Results      58-72s  (1740-2160) Animated stat counters
 *   6. CTA          72-90s  (2160-2700) Book a call + URL + shimmer
 */

// Scene durations in frames
const SCENE_1_HOOK = 150;       // 5s
const SCENE_2_PROBLEM = 390;    // 13s
const SCENE_3_REVEAL = 300;     // 10s
const SCENE_4_SERVICES = 900;   // 30s
const SCENE_5_RESULTS = 420;    // 14s
const SCENE_6_CTA = 540;        // 18s

// Scene start frames
const S1 = 0;
const S2 = SCENE_1_HOOK;
const S3 = S2 + SCENE_2_PROBLEM;
const S4 = S3 + SCENE_3_REVEAL;
const S5 = S4 + SCENE_4_SERVICES;
const S6 = S5 + SCENE_5_RESULTS;

export const Launch: React.FC = () => {
  const frame = useCurrentFrame();

  // Ambient music volume: fade in, sustain, fade out at end
  const musicVolume = interpolate(
    frame,
    [0, 60, 2500, 2700],
    [0, 0.35, 0.35, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      {/* Background ambient music — loops to fill 90s */}
      <SFX
        src={staticFile('sfx/ambient-tech.mp3')}
        volume={musicVolume}
        loop
      />

      {/* Whoosh on scene transitions */}
      <Sequence from={S2 - 5} durationInFrames={60} name="Whoosh-1">
        <SFX src={staticFile('sfx/whoosh.mp3')} volume={0.5} />
      </Sequence>
      <Sequence from={S3 - 5} durationInFrames={60} name="Whoosh-2">
        <SFX src={staticFile('sfx/whoosh.mp3')} volume={0.4} />
      </Sequence>
      <Sequence from={S5 - 5} durationInFrames={60} name="Whoosh-3">
        <SFX src={staticFile('sfx/whoosh.mp3')} volume={0.4} />
      </Sequence>
      <Sequence from={S6 - 5} durationInFrames={60} name="Whoosh-4">
        <SFX src={staticFile('sfx/whoosh.mp3')} volume={0.4} />
      </Sequence>

      {/* Impact on logo reveal */}
      <Sequence from={S3 + 25} durationInFrames={60} name="Impact">
        <SFX src={staticFile('sfx/impact.mp3')} volume={0.6} />
      </Sequence>

      {/* Impact on each service block transition */}
      <Sequence from={S4 + 300} durationInFrames={60} name="Impact-2">
        <SFX src={staticFile('sfx/impact.mp3')} volume={0.3} />
      </Sequence>
      <Sequence from={S4 + 600} durationInFrames={60} name="Impact-3">
        <SFX src={staticFile('sfx/impact.mp3')} volume={0.3} />
      </Sequence>

      {/* Visual scenes */}
      <Sequence from={S1} durationInFrames={SCENE_1_HOOK} name="Hook">
        <HookScene />
      </Sequence>

      <Sequence from={S2} durationInFrames={SCENE_2_PROBLEM} name="Problem">
        <ProblemScene />
      </Sequence>

      <Sequence from={S3} durationInFrames={SCENE_3_REVEAL} name="Logo Reveal">
        <LogoRevealScene />
      </Sequence>

      <Sequence from={S4} durationInFrames={SCENE_4_SERVICES} name="Services">
        <ServicesScene />
      </Sequence>

      <Sequence from={S5} durationInFrames={SCENE_5_RESULTS} name="Results">
        <ResultsScene />
      </Sequence>

      <Sequence from={S6} durationInFrames={SCENE_6_CTA} name="CTA">
        <CTAScene />
      </Sequence>
    </AbsoluteFill>
  );
};
