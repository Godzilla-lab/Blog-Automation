import React from 'react';
import { Video, staticFile } from 'remotion';

/**
 * Renders either a video or still image background based on file extension.
 * Uses Remotion <Video> for .mp4/.webm/.mov (Chrome's native video decoder).
 * Falls back to <img> for .jpg/.png stills.
 *
 * For video: ignores transform styles (Ken Burns zoom) since video has its own motion.
 * For images: passes all styles through including zoom transforms.
 */

interface FootageBackgroundProps {
  src: string;
  style?: React.CSSProperties;
}

export const FootageBackground: React.FC<FootageBackgroundProps> = ({
  src,
  style = {},
}) => {
  const resolvedSrc = staticFile(src);
  const isVideo = /\.(mp4|webm|mov)$/i.test(src);

  if (isVideo) {
    // Video already has motion — skip Ken Burns zoom/transform styles
    return (
      <Video
        src={resolvedSrc}
        muted
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
      src={resolvedSrc}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
        ...style,
      }}
    />
  );
};
