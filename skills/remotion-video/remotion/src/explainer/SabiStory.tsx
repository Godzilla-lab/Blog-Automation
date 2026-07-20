import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import { frauncesFamily, jakartaFamily } from './fonts';
import { Sfx } from './Sfx';
import { MacBook } from './MacBook';
import { AppWindow } from './AppWindow';
import { Cursor } from './Cursor';

const GREEN = '#00B87A';
const GREEN_DEEP = '#067A4F';
const INK = '#14231C';
const MUTED = '#5F7169';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// ── beat boundaries (frames @30) ──
const B1 = 0;
const B2 = 105;
const B3 = 315;
const B4 = 630;
const B5 = 795;
const B6 = 1095;
export const STORY_FRAMES = 1305;

// display coords (inside the MacBook screen: 1168 x 728), center ~ (584, 364)
const APPS = [
  { name: 'WhatsApp', color: '#25D366', letter: 'W', sx: 110, sy: 118 },
  { name: 'Spreadsheet', color: '#217346', letter: 'S', sx: 449, sy: 118 },
  { name: 'Google Drive', color: '#1A73E8', letter: 'D', sx: 788, sy: 118 },
  { name: 'Bank', color: '#0F766E', letter: '$', sx: 110, sy: 330 },
  { name: 'Email', color: '#EA4335', letter: '@', sx: 449, sy: 330 },
  { name: 'Meeting Notes', color: '#8E44AD', letter: 'N', sx: 788, sy: 330 },
];
const cluster = (i: number) => ({ x: 400 + (i - 2.5) * 16, y: 250 + (i % 2) * 14 });
const gather = (i: number) => ({ x: 430 + (i - 2.5) * 8, y: 300 + (i % 2) * 6 });

export const SabiStory: React.FC = () => {
  const frame = useCurrentFrame();
  const eio = (a: number, b: number, from = 0, to = 1) =>
    interpolate(frame, [a, b], [from, to], { easing: Easing.inOut(Easing.cubic), ...clamp });

  // ── camera: slow push-in ──
  const cam = interpolate(frame, [0, B5], [1.0, 1.09], { easing: Easing.inOut(Easing.cubic), ...clamp });

  // ── beat 1 : opening line ──
  const b1 = eio(B1 + 10, B1 + 36) * (1 - eio(B2 - 26, B2 - 2));
  const b1y = (1 - eio(B1 + 10, B1 + 44)) * 26;

  // ── beat 2 : document + typing ──
  const docIn = eio(B2 + 10, B2 + 40);
  const docOut = 1 - eio(B3 - 24, B3 - 2);
  const heading = 'Community Learning Centre';
  const nCh = Math.max(0, Math.min(heading.length, Math.floor(interpolate(frame, [B2 + 48, B2 + 120], [0, heading.length], clamp))));
  const statusIn = eio(B2 + 126, B2 + 142);
  const fundIn = eio(B2 + 140, B2 + 156);
  const progIn = eio(B2 + 154, B2 + 172);
  const updIn = eio(B2 + 168, B2 + 184);
  const curP = eio(B2 + 10, B2 + 46); // cursor travels to doc
  const curX = interpolate(curP, [0, 1], [880, 470]);
  const curY = interpolate(curP, [0, 1], [560, 300]);

  // ── beats 3-5 : windows drift / blur / reconnect ──
  const spreadP = eio(B3 + 20, B4 - 6);
  const gatherP = eio(B5 + 10, B5 + 150);
  const winBlur = interpolate(frame, [B4, B4 + 36, B5 + 6, B5 + 50], [0, 9, 9, 0], clamp);
  const winFade = eio(B3 + 4, B3 + 24) * (1 - eio(B5 + 96, B5 + 150));

  // ── beat 4 : "everywhere" line ──
  const b4 = eio(B4 + 26, B4 + 54) * (1 - eio(B5 - 44, B5 - 12));

  // ── beat 5 : word stack ──
  const WORDS = ['Projects', 'Funding', 'Updates', 'Reporting', 'One Story'];

  // ── beat 6 : green + logo ──
  const green = eio(B6, B6 + 30);
  const logoIn = eio(B6 + 32, B6 + 58);
  const endOut = 1 - eio(STORY_FRAMES - 26, STORY_FRAMES - 2);

  return (
    <AbsoluteFill>
      {/* ─────────── AUDIO ─────────── */}
      <Audio src={staticFile('sfx/ambient-tech.mp3')} volume={0.08} loop />
      <Sequence from={B1 + 12} layout="none"><Audio src={staticFile('sabi/story_vo1.mp3')} /></Sequence>
      <Sequence from={B2 + 12} layout="none"><Audio src={staticFile('sabi/story_vo2.mp3')} /></Sequence>
      <Sequence from={B3 + 8} layout="none"><Audio src={staticFile('sabi/story_vo3.mp3')} /></Sequence>
      <Sequence from={B4 + 14} layout="none"><Audio src={staticFile('sabi/story_vo4.mp3')} /></Sequence>
      <Sequence from={B5 + 12} layout="none"><Audio src={staticFile('sabi/story_vo5.mp3')} /></Sequence>
      <Sequence from={B6 + 8} layout="none"><Audio src={staticFile('sabi/story_vo6.mp3')} /></Sequence>
      {/* soft transitions */}
      <Sfx src="sfx/whoosh.mp3" at={B2} volume={0.16} />
      <Sfx src="sabi/ux/open_002.ogg" at={B2 + 12} volume={0.3} />
      {Array.from({ length: heading.length }, (_, i) => (
        <Sfx key={`t${i}`} src="sabi/ux/tick_002.ogg" at={B2 + 48 + i * 2.9} volume={0.1} />
      ))}
      <Sfx src="sabi/ux/select_004.ogg" at={B2 + 126} volume={0.2} />
      <Sfx src="sabi/ux/select_002.ogg" at={B2 + 140} volume={0.16} />
      <Sfx src="sabi/ux/select_002.ogg" at={B2 + 154} volume={0.16} />
      <Sfx src="sabi/ux/select_002.ogg" at={B2 + 168} volume={0.16} />
      <Sfx src="sfx/whoosh.mp3" at={B3} volume={0.16} />
      {APPS.map((_, i) => (
        <Sfx key={`w${i}`} src="sabi/ux/open_001.ogg" at={B3 + 12 + i * 8} volume={0.2} />
      ))}
      <Sfx src="sabi/ux/minimize_003.ogg" at={B4 + 4} volume={0.22} />
      <Sfx src="sfx/whoosh.mp3" at={B5 + 8} volume={0.2} />
      {WORDS.map((_, i) => (
        <Sfx key={`wd${i}`} src={i === 4 ? 'sabi/ux/glass_003.ogg' : 'sabi/ux/select_002.ogg'} at={B5 + 44 + i * 30} volume={i === 4 ? 0.34 : 0.2} />
      ))}
      <Sfx src="sfx/whoosh.mp3" at={B6 - 4} volume={0.26} />
      <Sfx src="sabi/ux/bong_001.ogg" at={B6 + 32} volume={0.42} />

      {/* ─────────── DESK / DAYLIGHT BACKGROUND ─────────── */}
      <AbsoluteFill style={{ background: 'linear-gradient(160deg,#F6F3EE 0%,#EEF1F0 55%,#E6EBEB 100%)' }} />
      <AbsoluteFill style={{ background: 'radial-gradient(950px 640px at 22% 6%, rgba(255,251,238,0.9), transparent 60%)' }} />
      <AbsoluteFill style={{ background: 'radial-gradient(1300px 320px at 50% 110%, rgba(20,30,25,0.07), transparent 72%)' }} />

      {/* ─────────── MACBOOK (camera push-in) ─────────── */}
      <AbsoluteFill style={{ transform: `scale(${cam})`, transformOrigin: '50% 46%' }}>
        <MacBook>
          {/* Beat 1 — opening line */}
          <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', opacity: b1, transform: `translateY(${b1y}px)` }}>
            <div style={{ textAlign: 'center', fontFamily: jakartaFamily, fontWeight: 600, fontSize: 64, color: INK, lineHeight: 1.16, letterSpacing: -1 }}>
              Every project<br />starts with a <span style={{ color: GREEN }}>goal.</span>
            </div>
          </AbsoluteFill>

          {/* Beat 2 — document + typing */}
          <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', opacity: docIn * docOut }}>
            <div style={{ width: 720, height: 430, background: '#fff', borderRadius: 18, boxShadow: '0 26px 60px rgba(20,30,25,0.16)', border: '1px solid #EEF1EF', overflow: 'hidden', transform: `scale(${0.94 + docIn * 0.06})` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '14px 18px', borderBottom: '1px solid #F1F4F2' }}>
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#F0625C' }} />
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#F6BD3B' }} />
                <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#3FCB5B' }} />
                <div style={{ marginLeft: 12, fontFamily: jakartaFamily, fontSize: 16, color: MUTED, fontWeight: 500 }}>Untitled — Document</div>
              </div>
              <div style={{ padding: '30px 40px' }}>
                <div style={{ fontFamily: jakartaFamily, fontWeight: 700, fontSize: 40, color: INK, minHeight: 50 }}>
                  {heading.slice(0, nCh)}
                  <span style={{ opacity: frame % 20 < 10 ? 1 : 0, color: GREEN }}>|</span>
                </div>
                <div style={{ marginTop: 22, display: 'flex', flexDirection: 'column', gap: 15, fontFamily: jakartaFamily, fontSize: 24 }}>
                  <div style={{ opacity: statusIn, display: 'flex', gap: 12 }}>
                    <span style={{ color: MUTED, width: 160 }}>Status</span>
                    <span style={{ color: GREEN, fontWeight: 700 }}>● Active</span>
                  </div>
                  <div style={{ opacity: fundIn, display: 'flex', gap: 12 }}>
                    <span style={{ color: MUTED, width: 160 }}>Funding</span>
                    <span style={{ color: INK, fontWeight: 700 }}>₦12,450,000</span>
                  </div>
                  <div style={{ opacity: progIn, display: 'flex', gap: 12, alignItems: 'center' }}>
                    <span style={{ color: MUTED, width: 160 }}>Progress</span>
                    <span style={{ color: INK, fontWeight: 700, width: 56 }}>68%</span>
                    <div style={{ flex: 1, height: 10, borderRadius: 6, background: '#EEF1EF', overflow: 'hidden' }}>
                      <div style={{ width: `${68 * progIn}%`, height: '100%', background: GREEN, borderRadius: 6 }} />
                    </div>
                  </div>
                  <div style={{ opacity: updIn, display: 'flex', gap: 12 }}>
                    <span style={{ color: MUTED, width: 160 }}>Last update</span>
                    <span style={{ color: MUTED }}>2 hours ago</span>
                  </div>
                </div>
              </div>
            </div>
            <Cursor x={curX} y={curY} opacity={docIn} scale={1 - Math.max(0, eio(B2 + 46, B2 + 54)) * 0.12} />
          </AbsoluteFill>

          {/* Beats 3-5 — windows */}
          <AbsoluteFill style={{ filter: winBlur ? `blur(${winBlur}px)` : undefined }}>
            {APPS.map((a, i) => {
              const cl = cluster(i);
              const ga = gather(i);
              const bx = cl.x + (a.sx - cl.x) * spreadP;
              const by = cl.y + (a.sy - cl.y) * spreadP;
              const x = bx + (ga.x - bx) * gatherP;
              const y = by + (ga.y - by) * gatherP;
              const appear = eio(B3 + 8 + i * 7, B3 + 8 + i * 7 + 22);
              return (
                <AppWindow key={i} title={a.name} color={a.color} letter={a.letter} x={x} y={y} w={268} opacity={appear * winFade} scale={0.9 + appear * 0.1} />
              );
            })}
          </AbsoluteFill>

          {/* Beat 4 — everywhere line */}
          <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', opacity: b4 }}>
            <div style={{ textAlign: 'center', fontFamily: jakartaFamily, fontWeight: 600, fontSize: 52, color: INK, lineHeight: 1.25 }}>
              Nothing is missing.<br />
              <span style={{ color: MUTED }}>It's just… </span><span style={{ color: GREEN }}>everywhere.</span>
            </div>
          </AbsoluteFill>

          {/* Beat 5 — word stack */}
          <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 6 }}>
            {WORDS.map((w, i) => {
              const s = B5 + 46 + i * 30;
              const op = eio(s, s + 18);
              const last = i === 4;
              return (
                <div key={i} style={{ opacity: op, transform: `translateY(${(1 - op) * 12}px)`, textAlign: 'center' }}>
                  {i > 0 && <div style={{ fontSize: 22, color: MUTED, margin: '0 0 4px', opacity: 0.7 }}>↓</div>}
                  <div style={{ fontFamily: last ? frauncesFamily : jakartaFamily, fontStyle: last ? 'italic' : 'normal', fontWeight: last ? 700 : 600, fontSize: last ? 60 : 34, color: last ? GREEN : INK }}>{w}</div>
                </div>
              );
            })}
          </AbsoluteFill>
        </MacBook>
      </AbsoluteFill>

      {/* ─────────── BEAT 6 — green + logo (full frame) ─────────── */}
      <AbsoluteFill style={{ background: GREEN_DEEP, opacity: green * endOut, alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 30 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 22, opacity: logoIn, transform: `translateY(${(1 - logoIn) * 14}px)` }}>
          <Img src={staticFile('sabi/icon.png')} style={{ height: 128, borderRadius: 30, boxShadow: '0 20px 50px rgba(0,0,0,0.25)' }} />
          <div style={{ fontFamily: jakartaFamily, fontWeight: 800, fontSize: 120, color: '#fff', letterSpacing: -2 }}>sabi<span style={{ color: '#BFF3DE' }}>.</span></div>
        </div>
        <div style={{ opacity: eio(B6 + 52, B6 + 78), textAlign: 'center', color: 'rgba(255,255,255,0.94)', fontFamily: jakartaFamily, fontWeight: 500, fontSize: 34, lineHeight: 1.4 }}>
          One place for projects, funding, updates, and reporting.
        </div>
        <div style={{ opacity: eio(B6 + 66, B6 + 92), color: '#CFF6E6', fontFamily: jakartaFamily, fontWeight: 600, fontSize: 30, letterSpacing: 0.5 }}>
          www.sabiapp.co
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
