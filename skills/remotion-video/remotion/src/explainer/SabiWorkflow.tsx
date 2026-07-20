import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { frauncesFamily, jakartaFamily } from './fonts';
import { Sfx } from './Sfx';

const GREEN = '#00B87A';
const BG = '#060B08';
const INK = '#EAF2EC';
const MUTED = '#7C8F86';
const NODE_BASE = '#10231A';
const NODE_BORDER = '#1E3A2C';

const STEPS = [
  { n: '01', t: 'Contribute' },
  { n: '02', t: 'Track' },
  { n: '03', t: 'Verify proof' },
  { n: '04', t: 'Update timeline' },
  { n: '05', t: 'See impact' },
];
const CX = [260, 620, 980, 1340, 1700];
const CY = 560;
const R = 72;
const activeAt = (i: number) => 45 + i * 50;
const PULSE = 285;
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const Dust: React.FC = () => {
  const frame = useCurrentFrame();
  const dots = Array.from({ length: 46 }, (_, i) => {
    const rx = (Math.sin(i * 12.9898) * 43758.5453) % 1;
    const ry = (Math.sin(i * 78.233) * 12543.213) % 1;
    const x = (Math.abs(rx) * 1920 + Math.sin(frame / 60 + i) * 14) % 1920;
    const y = (Math.abs(ry) * 1080 + Math.cos(frame / 70 + i) * 12) % 1080;
    const op = 0.12 + 0.18 * (0.5 + 0.5 * Math.sin(frame / 30 + i));
    const s = 2 + (Math.abs(rx) * 3);
    return { x, y, op, s, i };
  });
  return (
    <AbsoluteFill>
      {dots.map((d) => (
        <div key={d.i} style={{ position: 'absolute', left: d.x, top: d.y, width: d.s, height: d.s, borderRadius: '50%', background: GREEN, opacity: d.op, filter: 'blur(0.5px)' }} />
      ))}
    </AbsoluteFill>
  );
};

const Connector: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const x1 = CX[i] + R;
  const x2 = CX[i + 1] - R;
  const w = x2 - x1;
  const draw = interpolate(frame, [activeAt(i) + 14, activeAt(i) + 40], [0, 1], clamp);
  const pulse = interpolate(frame, [PULSE, PULSE + 26], [0, 1], clamp);
  return (
    <div style={{ position: 'absolute', left: x1, top: CY - 2, width: w, height: 4 }}>
      <div style={{ position: 'absolute', inset: 0, background: NODE_BORDER, borderRadius: 4 }} />
      <div style={{ position: 'absolute', left: 0, top: 0, height: 4, width: `${draw * 100}%`, background: GREEN, borderRadius: 4, boxShadow: `0 0 ${8 + pulse * 16}px ${GREEN}` }} />
    </div>
  );
};

const Node: React.FC<{ i: number }> = ({ i }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = activeAt(i);
  const s = spring({ frame: frame - a, fps, config: { mass: 1, damping: 18, stiffness: 90 }, durationInFrames: 22 });
  const lit = interpolate(frame, [a, a + 16], [0, 1], clamp);
  const pulse = interpolate(frame, [PULSE, PULSE + 24], [0, 1], clamp);
  const glow = Math.max(lit * 0.7, pulse);
  const step = STEPS[i];
  return (
    <>
      <div
        style={{
          position: 'absolute',
          left: CX[i] - R,
          top: CY - R,
          width: 2 * R,
          height: 2 * R,
          borderRadius: '50%',
          background: lit > 0.5 ? `radial-gradient(circle at 50% 40%, ${GREEN}, #05996A)` : NODE_BASE,
          border: `2px solid ${lit > 0.5 ? GREEN : NODE_BORDER}`,
          boxShadow: `0 0 ${30 * glow}px ${GREEN}${glow > 0 ? 'aa' : '00'}, 0 0 ${70 * glow}px ${GREEN}55`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: s,
          transform: `scale(${0.7 + s * 0.3})`,
        }}
      >
        <div style={{ fontFamily: jakartaFamily, fontWeight: 800, fontSize: 40, color: lit > 0.5 ? '#04120B' : MUTED }}>{step.n}</div>
      </div>
      <div
        style={{
          position: 'absolute',
          left: CX[i] - 110,
          top: CY + R + 22,
          width: 220,
          textAlign: 'center',
          fontFamily: jakartaFamily,
          fontWeight: 700,
          fontSize: 28,
          color: lit > 0.4 ? INK : MUTED,
          opacity: interpolate(frame, [a + 4, a + 18], [0, 1], clamp),
        }}
      >
        {step.t}
      </div>
    </>
  );
};

export const SabiWorkflow: React.FC<{ embedded?: boolean }> = ({ embedded = false }) => {
  const frame = useCurrentFrame();
  const fade = interpolate(frame, [0, 12, 330, 345], [0, 1, 1, 0], clamp);
  const titleS = spring({ frame: frame - 8, fps: 30, config: { damping: 20 }, durationInFrames: 26 });
  return (
    <AbsoluteFill style={{ background: BG }}>
      {/* audio */}
      {!embedded && <Audio src={staticFile('sfx/ambient-tech.mp3')} volume={0.12} loop />}
      <Sequence from={10} layout="none">
        <Audio src={staticFile('sabi/vo2.wav')} />
      </Sequence>
      {STEPS.map((_, i) => {
        const conf = ['confirmation_001', 'confirmation_002', 'confirmation_003', 'confirmation_004', 'select_007'][i];
        return (
          <React.Fragment key={i}>
            <Sfx src={`sabi/ux/switch_00${i + 1}.ogg`} at={activeAt(i)} volume={0.26} />
            <Sfx src={`sabi/ux/${conf}.ogg`} at={activeAt(i) + 16} volume={0.32} />
          </React.Fragment>
        );
      })}
      <Sfx src="sabi/ux/maximize_009.ogg" at={PULSE} volume={0.4} />
      <Sfx src="sfx/impact.mp3" at={PULSE} volume={0.28} />

      {/* environment */}
      <AbsoluteFill style={{ background: `radial-gradient(1200px 700px at 50% -8%, ${GREEN}22, transparent 60%)` }} />
      <Dust />
      <AbsoluteFill style={{ background: 'radial-gradient(1400px 900px at 50% 50%, transparent 55%, rgba(0,0,0,0.55) 100%)' }} />

      <AbsoluteFill style={{ opacity: fade }}>
        <div style={{ position: 'absolute', top: 150, width: '100%', textAlign: 'center', opacity: titleS, transform: `translateY(${(1 - titleS) * -12}px)` }}>
          <div style={{ fontFamily: frauncesFamily, fontStyle: 'italic', fontWeight: 600, fontSize: 58, color: INK }}>
            How <span style={{ color: GREEN }}>Sabi</span> works
          </div>
        </div>
        {[0, 1, 2, 3].map((i) => (
          <Connector key={i} i={i} />
        ))}
        {STEPS.map((_, i) => (
          <Node key={i} i={i} />
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
