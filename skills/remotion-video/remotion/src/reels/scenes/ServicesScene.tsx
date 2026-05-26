import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { COLORS, SPRING_CONFIG } from '../../brand';
import { Background } from '../../components/shared/Background';
import { orbitronFamily, syneFamily } from '../../lib/fonts';

/**
 * Scene 4: What We Do (frames 0-900, 30 seconds)
 * Three service blocks with animated icons and kinetic text.
 * Each block gets ~10 seconds (300 frames).
 */

const SERVICES = [
  {
    name: 'AI Assistants',
    text: '24/7 customer response.\nZero missed leads.',
    accent: COLORS.primary,
    icon: 'chat',
  },
  {
    name: 'Lead Generation',
    text: 'Turn visitors into\nbooked appointments.',
    accent: COLORS.secondary,
    icon: 'funnel',
  },
  {
    name: 'Workflow Automation',
    text: 'Automate the tasks\nthat drain your team.',
    accent: COLORS.purple,
    icon: 'nodes',
  },
];

const BLOCK_DURATION = 300; // 10 seconds each

/** Animated chat bubble icon */
const ChatIcon: React.FC<{ accent: string; progress: number; cx: number; cy: number }> = ({
  accent,
  progress,
  cx,
  cy,
}) => (
  <svg width={120} height={120} style={{ position: 'absolute', left: cx - 60, top: cy - 60 }}>
    {/* Main bubble */}
    <rect
      x={15}
      y={15}
      width={90 * progress}
      height={60 * progress}
      rx={12}
      fill={`${accent}20`}
      stroke={accent}
      strokeWidth={2}
    />
    {/* Typing dots */}
    {[0, 1, 2].map((d) => {
      const dotDelay = d * 0.15;
      const dotOpacity = progress > 0.8 + dotDelay ? 1 : 0;
      const bounce = Math.sin((progress - 0.8 - dotDelay) * Math.PI * 4) * 3;
      return (
        <circle
          key={d}
          cx={40 + d * 18}
          cy={45 + (dotOpacity ? bounce : 0)}
          r={4}
          fill={accent}
          opacity={dotOpacity * 0.8}
        />
      );
    })}
    {/* Tail */}
    <polygon
      points="30,75 45,75 35,90"
      fill={`${accent}20`}
      stroke={accent}
      strokeWidth={2}
      strokeLinejoin="round"
      opacity={progress}
    />
  </svg>
);

/** Animated funnel icon */
const FunnelIcon: React.FC<{ accent: string; progress: number; cx: number; cy: number }> = ({
  accent,
  progress,
  cx,
  cy,
}) => {
  const dropY = 20 + progress * 70;
  const dropOpacity = interpolate(progress, [0.4, 0.6, 0.9, 1], [0, 1, 1, 0]);
  return (
    <svg width={120} height={120} style={{ position: 'absolute', left: cx - 60, top: cy - 60 }}>
      {/* Funnel shape */}
      <path
        d={`M 20,20 L 100,20 L 70,65 L 70,95 L 50,95 L 50,65 Z`}
        fill={`${accent}15`}
        stroke={accent}
        strokeWidth={2}
        strokeDasharray={300}
        strokeDashoffset={300 * (1 - progress)}
      />
      {/* Dropping lead dot */}
      <circle cx={60} cy={dropY} r={5} fill={accent} opacity={dropOpacity}>
        <animate attributeName="opacity" values="1;0.5;1" dur="0.5s" repeatCount="indefinite" />
      </circle>
    </svg>
  );
};

/** Animated workflow nodes icon */
const NodesIcon: React.FC<{ accent: string; progress: number; frame: number; cx: number; cy: number }> = ({
  accent,
  progress,
  frame,
  cx,
  cy,
}) => {
  const nodes = [
    { x: 30, y: 30 },
    { x: 90, y: 30 },
    { x: 60, y: 70 },
    { x: 30, y: 100 },
    { x: 90, y: 100 },
  ];
  const connections = [
    [0, 1], [0, 2], [1, 2], [2, 3], [2, 4],
  ];

  // Traveling pulse along connections
  const pulseIdx = Math.floor((frame / 20) % connections.length);

  return (
    <svg width={120} height={120} style={{ position: 'absolute', left: cx - 60, top: cy - 60 }}>
      {connections.map(([a, b], i) => {
        const lineOpacity = progress > (i + 1) / connections.length * 0.8 ? 0.5 : 0;
        const isPulse = i === pulseIdx && progress > 0.8;
        return (
          <line
            key={i}
            x1={nodes[a].x}
            y1={nodes[a].y}
            x2={nodes[b].x}
            y2={nodes[b].y}
            stroke={accent}
            strokeWidth={isPulse ? 3 : 1.5}
            opacity={lineOpacity + (isPulse ? 0.4 : 0)}
          />
        );
      })}
      {nodes.map((n, i) => {
        const nodeOpacity = progress > (i + 1) / nodes.length * 0.6 ? 1 : 0;
        return (
          <circle
            key={i}
            cx={n.x}
            cy={n.y}
            r={8}
            fill={`${accent}30`}
            stroke={accent}
            strokeWidth={2}
            opacity={nodeOpacity}
          />
        );
      })}
    </svg>
  );
};

export const ServicesScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isLandscape = width > height;

  // Determine which block is active
  const blockIndex = Math.min(
    Math.floor(frame / BLOCK_DURATION),
    SERVICES.length - 1,
  );
  const blockFrame = frame - blockIndex * BLOCK_DURATION;

  const service = SERVICES[blockIndex];

  // Block transition
  const blockEntry = spring({
    frame: blockFrame,
    fps,
    config: { ...SPRING_CONFIG, stiffness: 100 },
    durationInFrames: 25,
  });

  // Exit (fade out before next block)
  const blockExit =
    blockFrame > BLOCK_DURATION - 20
      ? interpolate(blockFrame, [BLOCK_DURATION - 20, BLOCK_DURATION], [1, 0], {
          extrapolateRight: 'clamp',
        })
      : 1;

  const opacity = blockEntry * blockExit;

  // Icon animation progress
  const iconProgress = interpolate(blockFrame, [10, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Name text
  const nameSpring = spring({
    frame: blockFrame - 15,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 25,
  });

  // Description text
  const descOpacity = interpolate(blockFrame, [40, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const descY = interpolate(blockFrame, [40, 60], [20, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Step number badge
  const badgeSpring = spring({
    frame: blockFrame - 5,
    fps,
    config: SPRING_CONFIG,
    durationInFrames: 20,
  });

  const iconX = isLandscape ? width * 0.35 : width * 0.5;
  const iconY = isLandscape ? height * 0.45 : height * 0.3;

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.background, opacity }}>
      <Background accent={service.accent} />

      {/* Step number badge */}
      <div
        style={{
          position: 'absolute',
          top: isLandscape ? 50 : 60,
          right: isLandscape ? 80 : undefined,
          left: isLandscape ? undefined : 0,
          width: isLandscape ? undefined : '100%',
          display: 'flex',
          justifyContent: isLandscape ? 'flex-end' : 'center',
          transform: `scale(${badgeSpring})`,
          opacity: badgeSpring,
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,
            borderRadius: '50%',
            border: `2px solid ${service.accent}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: orbitronFamily,
            fontSize: 20,
            fontWeight: 900,
            color: service.accent,
          }}
        >
          {blockIndex + 1}
        </div>
      </div>

      {/* Icon */}
      {service.icon === 'chat' && (
        <ChatIcon accent={service.accent} progress={iconProgress} cx={iconX} cy={iconY} />
      )}
      {service.icon === 'funnel' && (
        <FunnelIcon accent={service.accent} progress={iconProgress} cx={iconX} cy={iconY} />
      )}
      {service.icon === 'nodes' && (
        <NodesIcon accent={service.accent} progress={iconProgress} frame={blockFrame} cx={iconX} cy={iconY} />
      )}

      {/* Service name */}
      <div
        style={{
          position: 'absolute',
          top: isLandscape ? iconY + 80 : iconY + 100,
          left: isLandscape ? iconX - 250 : 0,
          width: isLandscape ? 500 : '100%',
          textAlign: 'center',
          fontFamily: orbitronFamily,
          fontSize: isLandscape ? 40 : 36,
          fontWeight: 900,
          color: service.accent,
          textShadow: `0 0 30px ${service.accent}50`,
          transform: `scale(${nameSpring})`,
          opacity: nameSpring,
        }}
      >
        {service.name}
      </div>

      {/* Description */}
      <div
        style={{
          position: 'absolute',
          top: isLandscape ? iconY + 140 : iconY + 160,
          left: isLandscape ? iconX - 250 : 0,
          width: isLandscape ? 500 : '100%',
          textAlign: 'center',
          fontFamily: syneFamily,
          fontSize: isLandscape ? 26 : 24,
          color: COLORS.textPrimary,
          lineHeight: 1.5,
          whiteSpace: 'pre-line',
          opacity: descOpacity,
          transform: `translateY(${descY}px)`,
          padding: isLandscape ? 0 : '0 60px',
        }}
      >
        {service.text}
      </div>

      {/* Horizontal accent line */}
      <div
        style={{
          position: 'absolute',
          top: isLandscape ? iconY + 210 : iconY + 240,
          left: '50%',
          transform: 'translateX(-50%)',
          width: interpolate(blockFrame, [60, 80], [0, 200], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
          height: 2,
          backgroundColor: service.accent,
          opacity: 0.4,
        }}
      />
    </AbsoluteFill>
  );
};
