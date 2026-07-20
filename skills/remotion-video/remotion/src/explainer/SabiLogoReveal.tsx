import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { frauncesFamily, jakartaFamily } from './fonts';
import { Sfx } from './Sfx';

const GREEN = '#00B87A';
const BG = '#05100B';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const CX = 960;
const CY = 452;

// green particles that swirl inward and coalesce at the logo center
const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const dots = Array.from({ length: 60 }, (_, i) => {
    const ang = (i / 60) * Math.PI * 2 + Math.sin(i * 13.1) * 1.6;
    const rad = 320 + Math.abs(Math.sin(i * 7.3)) * 560;
    const sx = CX + Math.cos(ang) * rad;
    const sy = CY + Math.sin(ang) * rad;
    const p = interpolate(frame, [0, 40], [0, 1], clamp);
    const e = p * p * (3 - 2 * p); // smoothstep
    const x = interpolate(e, [0, 1], [sx, CX + Math.cos(ang) * 10]);
    const y = interpolate(e, [0, 1], [sy, CY + Math.sin(ang) * 10]);
    const op = interpolate(frame, [0, 6, 32, 44], [0, 0.85, 0.85, 0], clamp);
    const s = interpolate(frame, [0, 40], [7, 1.5], clamp);
    return { x, y, op, s, i };
  });
  return (
    <AbsoluteFill>
      {dots.map((d) => (
        <div key={d.i} style={{ position: 'absolute', left: d.x, top: d.y, width: d.s, height: d.s, borderRadius: '50%', background: GREEN, opacity: d.op, filter: 'blur(1px)', boxShadow: `0 0 8px ${GREEN}` }} />
      ))}
    </AbsoluteFill>
  );
};

export const SabiLogoReveal: React.FC<{ embedded?: boolean }> = ({ embedded = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const lockS = spring({ frame: frame - 32, fps, config: { mass: 1, damping: 12, stiffness: 120 }, durationInFrames: 28 });
  const lockOp = interpolate(frame, [32, 42], [0, 1], clamp);
  const flash = interpolate(frame, [36, 44, 66], [0, 0.85, 0], clamp);
  const sweep = interpolate(frame, [44, 76], [-0.25, 1.25], clamp);
  const sweepOp = interpolate(frame, [44, 50, 70, 76], [0, 0.55, 0.55, 0], clamp);
  const tag = interpolate(frame, [92, 116], [0, 1], clamp);
  const underline = interpolate(frame, [98, 128], [0, 1], clamp);
  const glow = interpolate(frame, [118, 140, 165], [0.15, 1, 0.6], clamp);
  const fade = interpolate(frame, [0, 10], [0, 1], clamp);

  return (
    <AbsoluteFill style={{ background: BG }}>
      {/* audio */}
      {!embedded && <Audio src={staticFile('sfx/ambient-tech.mp3')} volume={0.12} loop />}
      <Sfx src="sabi/ux/maximize_009.ogg" at={8} volume={0.34} />
      <Sfx src="sfx/whoosh.mp3" at={26} volume={0.4} />
      <Sfx src="sabi/ux/confirmation_004.ogg" at={36} volume={0.4} />
      <Sfx src="sfx/impact.mp3" at={36} volume={0.3} />
      <Sfx src="sabi/ux/scroll_004.ogg" at={46} volume={0.3} />
      <Sfx src="sabi/ux/tick_002.ogg" at={96} volume={0.34} />
      <Sfx src="sabi/ux/bong_001.ogg" at={118} volume={0.5} />

      {/* environment glow */}
      <AbsoluteFill style={{ background: `radial-gradient(1000px 720px at 50% 34%, ${GREEN}22, transparent 60%)`, opacity: 0.55 + glow * 0.45 }} />
      <Particles />

      <AbsoluteFill style={{ opacity: fade }}>
        {/* flash burst at the punch-in */}
        <AbsoluteFill style={{ background: `radial-gradient(420px 420px at ${CX}px ${CY}px, rgba(255,255,255,${flash}), transparent 70%)` }} />

        {/* full logo lockup */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: CY - 80,
            display: 'flex',
            justifyContent: 'center',
            opacity: lockOp,
            transform: `scale(${0.62 + lockS * 0.38})`,
            filter: `drop-shadow(0 0 ${34 * glow}px ${GREEN}aa)`,
          }}
        >
          <div style={{ position: 'relative' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 22 }}>
              <Img src={staticFile('sabi/icon.png')} style={{ height: 150, borderRadius: 34 }} />
              <div style={{ fontFamily: jakartaFamily, fontWeight: 800, fontSize: 128, color: '#FFFFFF', letterSpacing: -2, lineHeight: 1 }}>
                sabi<span style={{ color: GREEN }}>.</span>
              </div>
            </div>
            {/* specular light sweep */}
            <AbsoluteFill
              style={{
                background: `linear-gradient(105deg, transparent ${sweep * 100 - 14}%, rgba(255,255,255,0.75) ${sweep * 100}%, transparent ${sweep * 100 + 14}%)`,
                mixBlendMode: 'screen',
                opacity: sweepOp,
              }}
            />
          </div>
        </div>

        {/* tagline */}
        <div style={{ position: 'absolute', left: 0, right: 0, top: CY + 150, textAlign: 'center', opacity: tag, transform: `translateY(${(1 - tag) * 10}px)` }}>
          <div style={{ fontFamily: frauncesFamily, fontStyle: 'italic', fontWeight: 600, fontSize: 44, color: '#EAF2EC' }}>
            See where <span style={{ color: GREEN }}>shared money</span> goes.
          </div>
          <div style={{ height: 3, width: underline * 360, background: GREEN, margin: '18px auto 0', borderRadius: 3, boxShadow: `0 0 12px ${GREEN}` }} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
