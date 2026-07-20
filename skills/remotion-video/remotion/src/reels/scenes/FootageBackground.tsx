import React from 'react';
import { Sequence, Video, staticFile, useVideoConfig } from 'remotion';

/**
 * Renders either a single background or rotates between multiple sub-clips
 * during one slide. Use case: a slide whose voiceover is >6s would feel
 * monotonous on one Pexels clip; provide 2-3 srcs and the renderer cycles
 * between them evenly.
 *
 * Single-src back-compat: pass `srcs={["clip-1.mp4"]}` (or just `src`).
 * Multi-src: pass `srcs={["clip-1a.mp4", "clip-1b.mp4"]}`.
 *
 * Uses Remotion <Video> for .mp4/.webm/.mov (Chrome's native video decoder
 * — never OffthreadVideo, it bakes stripe artifacts into every frame).
 * Falls back to <img> for .jpg/.png stills.
 *
 * For video: ignores transform styles (Ken Burns zoom) since video has its
 * own motion. For images: passes all styles through including zoom transforms.
 *
 * `durationInFrames` is needed when srcs.length > 1 so the renderer can
 * divide the slide window evenly across sub-clips.
 */

interface FootageBackgroundProps {
  src?: string;
  srcs?: string[];
  style?: React.CSSProperties;
  durationInFrames?: number;
}

const isVideoFile = (s: string) => /\.(mp4|webm|mov)$/i.test(s);

const SingleBackground: React.FC<{src: string; style: React.CSSProperties}> = ({src, style}) => {
  const resolved = staticFile(src);
  if (isVideoFile(src)) {
    return (
      <Video
        src={resolved}
        muted
        loop
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover' as const,
        }}
      />
    );
  }
  return (
    <img
      src={resolved}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
        ...style,
      }}
    />
  );
};

export const FootageBackground: React.FC<FootageBackgroundProps> = ({
  src,
  srcs,
  style = {},
  durationInFrames,
}) => {
  const config = useVideoConfig();
  const list = (srcs && srcs.length > 0) ? srcs : (src ? [src] : []);

  if (list.length === 0) {
    return null;
  }

  if (list.length === 1) {
    return <SingleBackground src={list[0]} style={style} />;
  }

  // Multi-clip slide: divide the slide window evenly across srcs.
  // The parent Sequence's window dictates the effective length; we read it
  // from durationInFrames if provided, otherwise fall back to the composition
  // (which would be wrong, so the prop should be passed).
  const total = durationInFrames ?? config.durationInFrames;
  const segmentFrames = Math.floor(total / list.length);

  return (
    <>
      {list.map((s, i) => {
        const from = i * segmentFrames;
        // Last segment soaks up any remainder so the visual covers the whole window.
        const segDur = i === list.length - 1 ? total - from : segmentFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={segDur} layout="none">
            <div style={{position: 'absolute', inset: 0}}>
              <SingleBackground src={s} style={style} />
            </div>
          </Sequence>
        );
      })}
    </>
  );
};
