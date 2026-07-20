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
import { jakartaFamily } from './fonts';
import { Sfx } from './Sfx';

// ── Sabi brand tokens ─────────────────────────────────────────────────────────
const GREEN = '#00B87A';
const GREEN_DEEP = '#0E9E6C';
const BG = '#F3F7FC';
const INK = '#0B1F17';
const MUTED = '#6B7C75';
const CARD = '#FFFFFF';
const LINE = '#E7EEEA';
const SHADOW = '0 24px 60px rgba(10, 45, 30, 0.08)';
const FONT = jakartaFamily;

const springIn = (frame: number, fps: number, start: number, dur = 26) =>
  spring({ frame: frame - start, fps, config: { mass: 1, damping: 20, stiffness: 90 }, durationInFrames: dur });

const Card: React.FC<{ start: number; style?: React.CSSProperties; children: React.ReactNode }> = ({
  start,
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = springIn(frame, fps, start);
  return (
    <div
      style={{
        background: CARD,
        borderRadius: 28,
        boxShadow: SHADOW,
        border: `1px solid ${LINE}`,
        padding: 40,
        opacity: s,
        transform: `translateY(${(1 - s) * 28}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const cardLabel: React.CSSProperties = { fontFamily: FONT, fontSize: 24, color: MUTED, fontWeight: 600, letterSpacing: 0.3 };

const Header: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = springIn(frame, fps, 0, 24);
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', opacity: s, transform: `translateY(${(1 - s) * -14}px)` }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
        <Img src={staticFile('sabi/icon.png')} style={{ width: 58, height: 58, borderRadius: 15 }} />
        <div style={{ fontFamily: FONT, fontSize: 27, color: INK, fontWeight: 700 }}>Public overview</div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 12, height: 12, borderRadius: 999, background: GREEN, boxShadow: `0 0 14px ${GREEN}` }} />
        <div style={{ fontFamily: FONT, fontSize: 23, color: MUTED, fontWeight: 600 }}>Live · June 2026</div>
      </div>
    </div>
  );
};

const Hero: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [34, 92], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const val = Math.round(1284500 * p).toLocaleString('en-US');
  const d = interpolate(frame, [92, 106], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <div>
      <div style={cardLabel}>Contributed this month</div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 22, marginTop: 10 }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 118, lineHeight: 1, color: INK, fontVariantNumeric: 'tabular-nums' }}>
          <span style={{ color: GREEN }}>₦</span>
          {val}
        </div>
        <div
          style={{
            marginBottom: 20,
            opacity: d,
            transform: `scale(${0.8 + d * 0.2})`,
            background: 'rgba(0,184,122,0.12)',
            color: GREEN_DEEP,
            fontFamily: FONT,
            fontWeight: 700,
            fontSize: 28,
            padding: '9px 18px',
            borderRadius: 999,
            whiteSpace: 'nowrap',
          }}
        >
          ▲ 18.4%
        </div>
      </div>
    </div>
  );
};

const BARS = [
  { m: 'Jan', v: 142000 },
  { m: 'Feb', v: 208500 },
  { m: 'Mar', v: 173000 },
  { m: 'Apr', v: 296400 },
  { m: 'May', v: 251900 },
  { m: 'Jun', v: 318700 },
];
const BAR_START = 112;
const BarChart: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const max = Math.max(...BARS.map((b) => b.v));
  const H = 190;
  return (
    <div>
      <div style={{ ...cardLabel, marginBottom: 20 }}>Monthly contributions</div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 26 }}>
        {BARS.map((b, i) => {
          const s = springIn(frame, fps, BAR_START + i * 7, 24);
          const h = Math.max(6, (b.v / max) * H * s);
          const last = i === BARS.length - 1;
          return (
            <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{ height: H, width: '100%', display: 'flex', alignItems: 'flex-end' }}>
                <div
                  style={{
                    width: '100%',
                    height: h,
                    borderRadius: '10px 10px 5px 5px',
                    background: last ? GREEN : 'linear-gradient(180deg, #4CD9AB, #00B87A)',
                    boxShadow: last ? `0 10px 26px ${GREEN}55` : 'none',
                  }}
                />
              </div>
              <div style={{ fontFamily: FONT, fontSize: 20, color: MUTED, marginTop: 12, fontWeight: 600 }}>{b.m}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const RING_START = 140;
const Ring: React.FC = () => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [RING_START, RING_START + 46], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const pct = 62 * s;
  const r = 118;
  const C = 2 * Math.PI * r;
  const off = C * (1 - pct / 100);
  return (
    <div>
      <div style={cardLabel}>Community Improvement Plan</div>
      <div style={{ position: 'relative', width: 300, height: 300, margin: '14px auto 0' }}>
        <svg width={300} height={300}>
          <circle cx={150} cy={150} r={r} fill="none" stroke={LINE} strokeWidth={26} />
          <circle cx={150} cy={150} r={r} fill="none" stroke={GREEN} strokeWidth={26} strokeLinecap="round" strokeDasharray={C} strokeDashoffset={off} transform="rotate(-90 150 150)" />
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 76, color: INK, fontVariantNumeric: 'tabular-nums' }}>{Math.round(pct)}%</div>
          <div style={{ fontFamily: FONT, fontSize: 24, color: MUTED, fontWeight: 600 }}>funded</div>
        </div>
      </div>
    </div>
  );
};

const SPARK_START = 168;
const Spark: React.FC = () => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [SPARK_START, SPARK_START + 52], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const pts: [number, number][] = [[0, 78], [70, 64], [140, 70], [210, 44], [280, 50], [350, 24], [420, 14]];
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join(' ');
  const LEN = 620;
  const end = pts[pts.length - 1];
  return (
    <div>
      <div style={{ ...cardLabel, marginBottom: 14 }}>Verified proof uploaded</div>
      <svg width={420} height={94} style={{ overflow: 'visible', display: 'block', margin: '0 auto' }}>
        <path d={d} fill="none" stroke={GREEN} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={LEN} strokeDashoffset={LEN * (1 - draw)} />
        <circle cx={end[0]} cy={end[1]} r={7} fill={GREEN} opacity={draw > 0.92 ? 1 : 0} />
      </svg>
    </div>
  );
};

const KPIS = [
  { v: '1,284', l: 'contributors' },
  { v: '37', l: 'active projects' },
  { v: '94%', l: 'receipts verified' },
  { v: '₦4.82M', l: 'raised to date' },
  { v: '12', l: 'communities' },
];
const KPI_START = 205;
const KpiRow: React.FC = () => (
  <div style={{ display: 'flex', gap: 24 }}>
    {KPIS.map((k, i) => (
      <Card key={i} start={KPI_START + i * 13} style={{ flex: 1, padding: '28px 30px' }}>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 46, color: INK, fontVariantNumeric: 'tabular-nums' }}>{k.v}</div>
        <div style={{ fontFamily: FONT, fontSize: 22, color: MUTED, fontWeight: 600, marginTop: 6 }}>{k.l}</div>
      </Card>
    ))}
  </div>
);

export const SabiDashboard: React.FC<{ embedded?: boolean }> = ({ embedded = false }) => {
  const frame = useCurrentFrame();
  const fade = interpolate(frame, [0, 10, 315, 330], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: BG }}>
      {/* ── audio ── */}
      {!embedded && <Audio src={staticFile('sfx/ambient-tech.mp3')} volume={0.12} loop />}
      <Sequence from={10} layout="none">
        <Audio src={staticFile('sabi/vo1.wav')} />
      </Sequence>
      <Sfx src="sabi/ux/scroll_003.ogg" at={34} volume={0.34} />
      <Sfx src="sabi/ux/confirmation_001.ogg" at={92} volume={0.4} />
      <Sfx src="sabi/ux/select_002.ogg" at={95} volume={0.26} />
      {['glass_001', 'glass_002', 'glass_003', 'glass_004', 'glass_005', 'glass_006'].map((g, i) => (
        <Sfx key={`b${i}`} src={`sabi/ux/${g}.ogg`} at={BAR_START + i * 7 + 12} volume={0.3} />
      ))}
      <Sfx src="sabi/ux/maximize_005.ogg" at={RING_START} volume={0.34} />
      <Sfx src="sabi/ux/scroll_002.ogg" at={SPARK_START} volume={0.32} />
      {['select_001', 'select_003', 'select_004', 'select_005', 'select_006'].map((s, i) => (
        <Sfx key={`k${i}`} src={`sabi/ux/${s}.ogg`} at={KPI_START + i * 13} volume={0.3} />
      ))}

      {/* ── visuals ── */}
      <AbsoluteFill style={{ background: `radial-gradient(1300px 640px at 86% -12%, ${GREEN}1f, transparent 62%)` }} />
      <AbsoluteFill style={{ backgroundImage: `radial-gradient(${INK}0d 1px, transparent 1px)`, backgroundSize: '40px 40px', opacity: 0.5 }} />
      <AbsoluteFill style={{ padding: '60px 72px 64px', display: 'flex', flexDirection: 'column', opacity: fade }}>
        <Header />
        <div style={{ display: 'flex', gap: 32, marginTop: 30, flex: 1 }}>
          <div style={{ flex: 1.35, display: 'flex', flexDirection: 'column', gap: 26 }}>
            <Card start={18} style={{ flex: 'none' }}>
              <Hero />
            </Card>
            <Card start={96} style={{ flex: 1 }}>
              <BarChart />
            </Card>
          </div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 26 }}>
            <Card start={120} style={{ flex: 'none' }}>
              <Ring />
            </Card>
            <Card start={150} style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <Spark />
            </Card>
          </div>
        </div>
        <div style={{ marginTop: 28 }}>
          <KpiRow />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
