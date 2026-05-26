import React from 'react';
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';

export const LogoBadge: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: SPRING_CONFIG, durationInFrames: 30 });
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div
      style={{
        position: 'absolute',
        top: 80,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      {/* Glow behind logo */}
      <div
        style={{
          position: 'absolute',
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${COLORS.primary}40, transparent 70%)`,
          filter: 'blur(20px)',
        }}
      />
      <Img
        src={staticFile('hexa.png')}
        style={{ width: 80, height: 80, objectFit: 'contain' }}
      />
    </div>
  );
};
