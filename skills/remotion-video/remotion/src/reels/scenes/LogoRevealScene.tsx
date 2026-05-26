import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { Background } from '../../components/shared/Background';
import { CornerBrackets } from '../../components/shared/CornerBrackets';
import { orbitronFamily, syneFamily } from '../../lib/fonts';

/**
 * Scene 3: Logo Reveal / The Shift (frames 0-300, 10 seconds)
 * Transition from dark to brand space.
 * Logo appears with expanding glow ring + particles.
 * Tagline types in below.
 */

export const LogoRevealScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const accent = COLORS.primary;

  // Background fade in (brand space emerges)
  const bgOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Logo scale and entry
  const logoSpring = spring({
    frame: frame - 25,
    fps,
    config: { mass: 1, damping: 14, stiffness: 60 },
    durationInFrames: 40,
  });

  // Expanding glow ring
  const ringProgress = interpolate(frame, [30, 70], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ringRadius = 60 + ringProgress * 180;
  const ringOpacity = interpolate(ringProgress, [0, 0.5, 1], [0, 0.8, 0], {
    extrapolateRight: 'clamp',
  });

  // Second ring (delayed)
  const ring2Progress = interpolate(frame, [45, 90], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ring2Radius = 60 + ring2Progress * 250;
  const ring2Opacity = interpolate(
    ring2Progress,
    [0, 0.4, 1],
    [0, 0.5, 0],
    { extrapolateRight: 'clamp' },
  );

  // Logo glow pulse after reveal
  const glowPulse =
    frame > 60
      ? interpolate((frame - 60) % 90, [0, 45, 90], [0.3, 0.6, 0.3], {
          extrapolateRight: 'clamp',
        })
      : 0.2;

  // Tagline typewriter
  const tagline = 'AI Solutions for Service Businesses';
  const typeStart = 80;
  const charsVisible = Math.max(
    0,
    Math.floor((frame - typeStart) * 0.8),
  );
  const displayedTagline = tagline.slice(0, charsVisible);
  const cursorVisible = frame >= typeStart && (frame - typeStart) % 16 < 10;

  // Tagline underline
  const underlineWidth = interpolate(
    frame,
    [typeStart + tagline.length / 0.8 + 5, typeStart + tagline.length / 0.8 + 25],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  const centerX = width / 2;
  const logoY = height * 0.3;
  const logoSize = width > height ? 140 : 120;

  // Particle burst
  const particles = Array.from({ length: 20 }).map((_, i) => {
    const angle = (i / 20) * Math.PI * 2;
    const burstStart = 35;
    const burstProgress = interpolate(
      frame,
      [burstStart, burstStart + 30],
      [0, 1],
      { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
    );
    const distance = burstProgress * (120 + (i % 5) * 30);
    const x = centerX + Math.cos(angle) * distance;
    const y = logoY + Math.sin(angle) * distance;
    const opacity = interpolate(burstProgress, [0, 0.3, 1], [0, 0.8, 0], {
      extrapolateRight: 'clamp',
    });
    const size = 2 + (i % 3);
    return { x, y, opacity, size };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background }}>
      <div style={{ opacity: bgOpacity }}>
        <Background accent={accent} />
      </div>
      <div style={{ opacity: bgOpacity }}>
        <CornerBrackets accent={accent} />
      </div>

      {/* Expanding glow rings */}
      <div
        style={{
          position: 'absolute',
          left: centerX - ringRadius,
          top: logoY - ringRadius + logoSize / 2,
          width: ringRadius * 2,
          height: ringRadius * 2,
          borderRadius: '50%',
          border: `2px solid ${accent}`,
          opacity: ringOpacity,
          boxShadow: `0 0 20px ${accent}60`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: centerX - ring2Radius,
          top: logoY - ring2Radius + logoSize / 2,
          width: ring2Radius * 2,
          height: ring2Radius * 2,
          borderRadius: '50%',
          border: `1px solid ${accent}`,
          opacity: ring2Opacity,
        }}
      />

      {/* Particle burst */}
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: p.x,
            top: p.y,
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            backgroundColor: accent,
            opacity: p.opacity,
            boxShadow: `0 0 6px ${accent}`,
          }}
        />
      ))}

      {/* Logo glow */}
      <div
        style={{
          position: 'absolute',
          left: centerX - logoSize,
          top: logoY - logoSize / 2,
          width: logoSize * 2,
          height: logoSize * 2,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${accent}50, transparent 70%)`,
          filter: 'blur(30px)',
          opacity: glowPulse * logoSpring,
        }}
      />

      {/* Logo */}
      <div
        style={{
          position: 'absolute',
          left: centerX - logoSize / 2,
          top: logoY,
          width: logoSize,
          height: logoSize,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${logoSpring})`,
          opacity: logoSpring,
        }}
      >
        <img
          src={staticFile('hexa.png')}
          style={{
            width: logoSize,
            height: logoSize,
            objectFit: 'contain',
          }}
        />
      </div>

      {/* Tagline */}
      <div
        style={{
          position: 'absolute',
          top: logoY + logoSize + 50,
          left: 0,
          right: 0,
          textAlign: 'center',
        }}
      >
        <span
          style={{
            fontFamily: orbitronFamily,
            fontSize: width > height ? 36 : 30,
            fontWeight: 700,
            color: COLORS.textPrimary,
            letterSpacing: 3,
          }}
        >
          {displayedTagline}
        </span>
        {cursorVisible && (
          <span
            style={{
              fontFamily: orbitronFamily,
              fontSize: width > height ? 36 : 30,
              fontWeight: 700,
              color: accent,
            }}
          >
            |
          </span>
        )}

        {/* Underline */}
        <div
          style={{
            margin: '16px auto 0',
            width: `${underlineWidth * 60}%`,
            maxWidth: 400,
            height: 2,
            backgroundColor: accent,
            opacity: 0.6,
          }}
        />
      </div>

      {/* "We are" small label above logo */}
      <div
        style={{
          position: 'absolute',
          top: logoY - 50,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: syneFamily,
          fontSize: 18,
          fontWeight: 600,
          color: COLORS.textMuted,
          letterSpacing: 8,
          textTransform: 'uppercase',
          opacity: interpolate(frame, [15, 30], [0, 0.6], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
        }}
      >
        INTRODUCING
      </div>
    </AbsoluteFill>
  );
};
