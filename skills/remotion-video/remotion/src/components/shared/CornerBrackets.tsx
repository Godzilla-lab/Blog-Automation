import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { COLORS, WIDTH, HEIGHT } from '../../brand';

const BRACKET_SIZE = 40;
const BRACKET_THICKNESS = 2;
const MARGIN = 40;

const Bracket: React.FC<{
  corner: 'tl' | 'tr' | 'bl' | 'br';
  accent: string;
  progress: number;
}> = ({ corner, accent, progress }) => {
  const isTop = corner.startsWith('t');
  const isLeft = corner.endsWith('l');

  return (
    <div
      style={{
        position: 'absolute',
        top: isTop ? MARGIN : undefined,
        bottom: !isTop ? MARGIN : undefined,
        left: isLeft ? MARGIN : undefined,
        right: !isLeft ? MARGIN : undefined,
        width: BRACKET_SIZE,
        height: BRACKET_SIZE,
        opacity: 0.4 * progress,
      }}
    >
      {/* Horizontal line */}
      <div
        style={{
          position: 'absolute',
          [isTop ? 'top' : 'bottom']: 0,
          [isLeft ? 'left' : 'right']: 0,
          width: BRACKET_SIZE * progress,
          height: BRACKET_THICKNESS,
          backgroundColor: accent,
        }}
      />
      {/* Vertical line */}
      <div
        style={{
          position: 'absolute',
          [isTop ? 'top' : 'bottom']: 0,
          [isLeft ? 'left' : 'right']: 0,
          width: BRACKET_THICKNESS,
          height: BRACKET_SIZE * progress,
          backgroundColor: accent,
        }}
      />
    </div>
  );
};

export const CornerBrackets: React.FC<{ accent?: string }> = ({
  accent = COLORS.primary,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [10, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <>
      <Bracket corner="tl" accent={accent} progress={progress} />
      <Bracket corner="tr" accent={accent} progress={progress} />
      <Bracket corner="bl" accent={accent} progress={progress} />
      <Bracket corner="br" accent={accent} progress={progress} />
    </>
  );
};
