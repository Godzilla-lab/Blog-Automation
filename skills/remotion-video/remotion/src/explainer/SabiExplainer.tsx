import React from 'react';
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { Sfx } from './Sfx';
import { SabiLogoReveal } from './SabiLogoReveal';
import { SabiDashboard } from './SabiDashboard';
import { SabiWorkflow } from './SabiWorkflow';
import { SabiUiAd } from './SabiUiAd';

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const L = 165; // logo reveal cold-open
const S1 = 330; // dashboard
const S2 = 345; // workflow
const S3 = 375; // ui-ad
export const EXPLAINER_FRAMES = L + S1 + S2 + S3; // 1215

// dip-to-dark transition overlay pinned to a boundary frame
const Dip: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [at - 9, at, at + 9], [0, 1, 0], clamp);
  return <AbsoluteFill style={{ background: '#05100B', opacity: o, pointerEvents: 'none' }} />;
};

export const SabiExplainer: React.FC = () => {
  const frame = useCurrentFrame();
  const music = interpolate(frame, [0, 30, EXPLAINER_FRAMES - 40, EXPLAINER_FRAMES], [0, 0.11, 0.11, 0], clamp);
  return (
    <AbsoluteFill style={{ background: '#05100B' }}>
      {/* continuous ambient bed across the whole film */}
      <Audio src={staticFile('sfx/ambient-tech.mp3')} volume={music} loop />

      <Sequence from={0} durationInFrames={L}>
        <SabiLogoReveal embedded />
      </Sequence>
      <Sequence from={L} durationInFrames={S1}>
        <SabiDashboard embedded />
      </Sequence>
      <Sequence from={L + S1} durationInFrames={S2}>
        <SabiWorkflow embedded />
      </Sequence>
      <Sequence from={L + S1 + S2} durationInFrames={S3}>
        <SabiUiAd embedded />
      </Sequence>

      <Sfx src="sfx/whoosh.mp3" at={L - 5} volume={0.34} />
      <Sfx src="sfx/whoosh.mp3" at={L + S1 - 5} volume={0.34} />
      <Sfx src="sfx/whoosh.mp3" at={L + S1 + S2 - 5} volume={0.34} />
      <Dip at={L} />
      <Dip at={L + S1} />
      <Dip at={L + S1 + S2} />
    </AbsoluteFill>
  );
};
