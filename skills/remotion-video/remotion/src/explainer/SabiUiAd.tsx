import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
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
const BG = '#EDF3F0';
const INK = '#0B1F17';
const MUTED = '#6B7C75';
const CARD = '#FFFFFF';
const LINE = '#E7EEEA';
const FONT = jakartaFamily;
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const PHONE_W = 440;
const PHONE_H = 900;
const springAt = (frame: number, fps: number, start: number, dur = 24, stiffness = 90) =>
  spring({ frame: frame - start, fps, config: { mass: 1, damping: 18, stiffness }, durationInFrames: dur });

// A project row inside the app
const ProjectRow: React.FC<{ start: number; title: string; sub: string; checked?: boolean; checkAt?: number }> = ({
  start,
  title,
  sub,
  checked,
  checkAt = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = springAt(frame, fps, start);
  const chk = checked ? springAt(frame, fps, checkAt, 18, 130) : 0;
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        background: '#F6FAF8',
        border: `1px solid ${LINE}`,
        borderRadius: 20,
        padding: '18px 20px',
        opacity: s,
        transform: `translateY(${(1 - s) * 16}px)`,
      }}
    >
      <div style={{ width: 44, height: 44, borderRadius: 12, background: '#E4F3EC', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 18, height: 18, borderRadius: 5, background: GREEN }} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 24, color: INK }}>{title}</div>
        <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 18, color: MUTED, marginTop: 2 }}>{sub}</div>
      </div>
      {checked && (
        <div style={{ width: 40, height: 40, borderRadius: '50%', background: GREEN, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: chk, transform: `scale(${0.5 + chk * 0.5})`, boxShadow: `0 0 16px ${GREEN}88` }}>
          <div style={{ width: 16, height: 9, borderLeft: '4px solid #fff', borderBottom: '4px solid #fff', transform: 'rotate(-45deg) translate(1px,-2px)' }} />
        </div>
      )}
    </div>
  );
};

const PhoneScreen: React.FC = () => {
  const frame = useCurrentFrame();
  // ring climbs 58 -> 62 between 110 and 150
  const ringP = interpolate(frame, [110, 150], [58, 62], clamp);
  const r = 66;
  const C = 2 * Math.PI * r;
  const off = C * (1 - ringP / 100);
  return (
    <div style={{ position: 'absolute', inset: 16, borderRadius: 44, background: '#F3F7FC', overflow: 'hidden', padding: '26px 24px' }}>
      {/* status bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: FONT, fontWeight: 600, fontSize: 18, color: INK, opacity: 0.8 }}>
        <span>9:41</span>
        <span>●●● ▮</span>
      </div>
      {/* header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 18 }}>
        <Img src={staticFile('sabi/icon.png')} style={{ width: 40, height: 40, borderRadius: 11 }} />
        <div>
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 22, color: INK }}>Community Plan</div>
          <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 16, color: MUTED }}>Public overview</div>
        </div>
      </div>
      {/* progress card */}
      <div style={{ marginTop: 20, background: CARD, border: `1px solid ${LINE}`, borderRadius: 22, padding: 22, display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{ position: 'relative', width: 160, height: 160 }}>
          <svg width={160} height={160}>
            <circle cx={80} cy={80} r={r} fill="none" stroke={LINE} strokeWidth={16} />
            <circle cx={80} cy={80} r={r} fill="none" stroke={GREEN} strokeWidth={16} strokeLinecap="round" strokeDasharray={C} strokeDashoffset={off} transform="rotate(-90 80 80)" />
          </svg>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 40, color: INK }}>{Math.round(ringP)}%</div>
            <div style={{ fontFamily: FONT, fontWeight: 600, fontSize: 15, color: MUTED }}>funded</div>
          </div>
        </div>
        <div>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 30, color: INK }}>₦1.25M</div>
          <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 17, color: MUTED, marginTop: 2 }}>raised of ₦2M</div>
        </div>
      </div>
      {/* project rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 18 }}>
        <ProjectRow start={150} title="Water Project" sub="Borehole · receipts" checked checkAt={170} />
        <ProjectRow start={200} title="School Fund" sub="₦775,000 of ₦1.25M" />
        <ProjectRow start={230} title="Clinic Renovation" sub="Timeline updated" />
      </div>
    </div>
  );
};

const Notification: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = springAt(frame, fps, 40, 22, 120);
  const out = interpolate(frame, [104, 120], [1, 0], clamp);
  const y = interpolate(inn, [0, 1], [-140, 0]);
  return (
    <div
      style={{
        position: 'absolute',
        top: 40,
        left: 30,
        right: 30,
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        background: 'rgba(255,255,255,0.96)',
        border: `1px solid ${LINE}`,
        borderRadius: 20,
        padding: '16px 18px',
        boxShadow: '0 18px 40px rgba(10,40,28,0.18)',
        opacity: inn * out,
        transform: `translateY(${y}px)`,
      }}
    >
      <div style={{ width: 44, height: 44, borderRadius: 12, background: GREEN, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Img src={staticFile('sabi/icon.png')} style={{ width: 44, height: 44, borderRadius: 12 }} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 22, color: INK }}>Ada contributed ₦25,000</div>
        <div style={{ fontFamily: FONT, fontWeight: 500, fontSize: 17, color: MUTED }}>just now · Water Project</div>
      </div>
    </div>
  );
};

const LogoLock: React.FC = () => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [300, 330], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: `rgba(237,243,240,${0.86 * s})`, alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 26, opacity: s }}>
      <Img src={staticFile('sabi/wordmark.png')} style={{ height: 92, transform: `translateY(${(1 - s) * 14}px)` }} />
      <div style={{ fontFamily: frauncesFamily, fontStyle: 'italic', fontWeight: 600, fontSize: 46, color: INK }}>
        See where <span style={{ color: GREEN }}>shared money</span> goes.
      </div>
    </AbsoluteFill>
  );
};

export const SabiUiAd: React.FC<{ embedded?: boolean }> = ({ embedded = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = springAt(frame, fps, 0, 28, 70);
  const tilt = interpolate(frame, [260, 290], [0, -5], clamp) * interpolate(frame, [298, 312], [1, 0], clamp);
  const lift = interpolate(frame, [260, 290], [0, -8], clamp);
  const fade = interpolate(frame, [0, 12, 362, 375], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill style={{ background: BG }}>
      {/* audio */}
      {!embedded && <Audio src={staticFile('sfx/ambient-tech.mp3')} volume={0.12} loop />}
      <Sequence from={10} layout="none">
        <Audio src={staticFile('sabi/vo3.wav')} />
      </Sequence>
      <Sfx src="sabi/ux/maximize_002.ogg" at={40} volume={0.32} />
      <Sfx src="sabi/ux/select_003.ogg" at={58} volume={0.34} />
      <Sfx src="sabi/ux/scroll_001.ogg" at={110} volume={0.3} />
      <Sfx src="sabi/ux/confirmation_003.ogg" at={170} volume={0.42} />
      <Sfx src="sabi/ux/select_005.ogg" at={200} volume={0.28} />
      <Sfx src="sabi/ux/tick_004.ogg" at={230} volume={0.34} />
      <Sfx src="sfx/whoosh.mp3" at={262} volume={0.22} />
      <Sfx src="sabi/ux/bong_001.ogg" at={303} volume={0.45} />
      <Sfx src="sabi/ux/glass_002.ogg" at={306} volume={0.24} />

      {/* studio bg */}
      <AbsoluteFill style={{ background: `radial-gradient(1100px 700px at 50% 8%, ${GREEN}18, transparent 60%)` }} />

      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', opacity: fade }}>
        <div
          style={{
            position: 'relative',
            width: PHONE_W,
            height: PHONE_H,
            borderRadius: 60,
            background: '#0B0F0D',
            boxShadow: `0 50px 120px rgba(10,40,28,0.28), 0 0 60px ${GREEN}22`,
            opacity: enter,
            transform: `translateY(${(1 - enter) * 40 + lift}px) rotate(${tilt}deg)`,
            border: '2px solid #16211C',
          }}
        >
          <PhoneScreen />
          <Notification />
          {/* notch */}
          <div style={{ position: 'absolute', top: 18, left: '50%', transform: 'translateX(-50%)', width: 120, height: 26, borderRadius: 20, background: '#0B0F0D' }} />
        </div>
        <LogoLock />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
