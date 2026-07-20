import React from 'react';
import { Audio, Sequence, staticFile } from 'remotion';

/** One sound effect pinned to an exact frame (frame-accurate sound design). */
export const Sfx: React.FC<{ src: string; at: number; volume?: number }> = ({ src, at, volume = 0.5 }) => (
  <Sequence from={Math.max(0, Math.round(at))} layout="none">
    <Audio src={staticFile(src)} volume={volume} />
  </Sequence>
);
