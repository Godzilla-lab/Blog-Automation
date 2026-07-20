import React from 'react';
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { jakartaFamily } from './fonts';
import { SabiStory, STORY_FRAMES } from './SabiStory';

const GREEN_DEEP = '#067A4F';
const MUTED = '#5F7169';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const B6 = 1095; // green outro start (matches SabiStory)

// 9:16 wrapper: the 16:9 film centered in a branded daylight frame,
// with a full-frame green logo lock at the end.
export const SabiStoryVertical: React.FC = () => {
  const frame = useCurrentFrame();
  const green = interpolate(frame, [B6, B6 + 30], [0, 1], clamp);
  const logoIn = interpolate(frame, [B6 + 32, B6 + 58], [0, 1], clamp);
  const endOut = 1 - interpolate(frame, [STORY_FRAMES - 26, STORY_FRAMES - 2], [0, 1], clamp);
  const brand = interpolate(frame, [24, 54, B6 - 24, B6 - 2], [0, 1, 1, 0], clamp);
  const scale = 0.84;

  return (
    <AbsoluteFill style={{ background: 'linear-gradient(165deg,#F6F3EE 0%,#EEF1F0 55%,#E6EBEB 100%)' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(760px 900px at 24% 10%, rgba(255,251,238,0.85), transparent 60%)' }} />

      {/* the 16:9 film, scaled + centered (brings its own VO / SFX / ambient) */}
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 1920, height: 1080, transform: `scale(${scale})`, transformOrigin: 'center' }}>
          <SabiStory />
        </div>
      </AbsoluteFill>

      {/* brand frame (visible during beats 1-5) */}
      <div style={{ position: 'absolute', top: 196, width: '100%', display: 'flex', justifyContent: 'center', opacity: brand }}>
        <Img src={staticFile('sabi/icon.png')} style={{ height: 92, borderRadius: 23 }} />
      </div>
      <div style={{ position: 'absolute', bottom: 210, width: '100%', textAlign: 'center', opacity: brand, fontFamily: jakartaFamily, fontWeight: 600, fontSize: 38, color: MUTED, letterSpacing: 0.5 }}>
        www.sabiapp.co
      </div>

      {/* full-frame green logo lock */}
      <AbsoluteFill style={{ background: GREEN_DEEP, opacity: green * endOut, alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 40 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 30, opacity: logoIn, transform: `translateY(${(1 - logoIn) * 16}px)` }}>
          <Img src={staticFile('sabi/icon.png')} style={{ height: 200, borderRadius: 46, boxShadow: '0 20px 50px rgba(0,0,0,0.25)' }} />
          <div style={{ fontFamily: jakartaFamily, fontWeight: 800, fontSize: 150, color: '#fff', letterSpacing: -3 }}>sabi<span style={{ color: '#BFF3DE' }}>.</span></div>
        </div>
        <div style={{ opacity: interpolate(frame, [B6 + 52, B6 + 78], [0, 1], clamp), textAlign: 'center', color: 'rgba(255,255,255,0.94)', fontFamily: jakartaFamily, fontWeight: 500, fontSize: 48, lineHeight: 1.4, maxWidth: 860, padding: '0 70px' }}>
          One place for projects, funding, updates, and reporting.
        </div>
        <div style={{ opacity: interpolate(frame, [B6 + 66, B6 + 92], [0, 1], clamp), color: '#CFF6E6', fontFamily: jakartaFamily, fontWeight: 600, fontSize: 42 }}>
          www.sabiapp.co
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
