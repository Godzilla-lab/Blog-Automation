/**
 * Remotion 4.0 has overly strict TypeScript types for Audio and Img components.
 * These wrappers suppress the false-positive errors while keeping usage clean.
 */
import React from 'react';
import { Audio as RemotionAudio, Img as RemotionImg } from 'remotion';

type AudioProps = {
  src: string;
  volume?: number | ((frame: number) => number);
  loop?: boolean;
  startFrom?: number;
  endAt?: number;
  playbackRate?: number;
};

type ImgProps = {
  src: string;
  style?: React.CSSProperties;
  className?: string;
};

export const SFX: React.FC<AudioProps> = (props) => {
  return <RemotionAudio {...(props as any)} />;
};

export const Logo: React.FC<ImgProps> = (props) => {
  return <RemotionImg {...(props as any)} />;
};
