import React from 'react';
import { jakartaFamily } from './fonts';

export const AppWindow: React.FC<{
  title: string;
  color: string;
  letter: string;
  x: number;
  y: number;
  w?: number;
  opacity?: number;
  scale?: number;
  blur?: number;
}> = ({ title, color, letter, x, y, w = 300, opacity = 1, scale = 1, blur = 0 }) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      width: w,
      background: '#ffffff',
      borderRadius: 16,
      border: '1px solid #EEF1EF',
      boxShadow: '0 18px 44px rgba(20,30,25,0.13)',
      overflow: 'hidden',
      opacity,
      transform: `scale(${scale})`,
      filter: blur ? `blur(${blur}px)` : undefined,
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px', borderBottom: '1px solid #F1F4F2' }}>
      <div style={{ width: 26, height: 26, borderRadius: 7, background: color, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontFamily: jakartaFamily, fontWeight: 800, fontSize: 14 }}>{letter}</div>
      <div style={{ fontFamily: jakartaFamily, fontWeight: 600, fontSize: 16, color: '#12201A' }}>{title}</div>
    </div>
    <div style={{ padding: '14px', display: 'flex', flexDirection: 'column', gap: 9 }}>
      <div style={{ height: 8, borderRadius: 4, background: '#EBEFEC', width: '82%' }} />
      <div style={{ height: 8, borderRadius: 4, background: '#F2F5F3', width: '62%' }} />
      <div style={{ height: 8, borderRadius: 4, background: '#F2F5F3', width: '72%' }} />
    </div>
  </div>
);
