import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { montserratFamily } from '../../lib/fonts';

/**
 * SyncedCaptions — word-by-word subtitle overlay synced to voiceover timestamps.
 *
 * Shows 3-5 words at a time at the bottom of the screen.
 * Current word highlighted in accent color, others white.
 * This is the standard viral caption style used on Instagram Reels.
 */

export interface WordTimestamp {
  word: string;
  startMs: number;
  endMs: number;
}

interface SyncedCaptionsProps {
  wordTimestamps: WordTimestamp[];
  accentColor: string;
}

// How many words to show at once. 3 keeps the pill within the 940px max-width
// even with long words like "EIGHTY-SEVEN" or "ATTRIBUTION" — 4 overflowed.
const WORDS_PER_GROUP = 3;

export const SyncedCaptions: React.FC<SyncedCaptionsProps> = ({
  wordTimestamps,
  accentColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!wordTimestamps || wordTimestamps.length === 0) return null;

  const currentTimeMs = (frame / fps) * 1000;

  // Find the current word index based on time
  let activeWordIndex = -1;
  for (let i = 0; i < wordTimestamps.length; i++) {
    if (currentTimeMs >= wordTimestamps[i].startMs && currentTimeMs < wordTimestamps[i].endMs) {
      activeWordIndex = i;
      break;
    }
    // If between words, stick with the last one that ended
    if (i < wordTimestamps.length - 1 &&
        currentTimeMs >= wordTimestamps[i].endMs &&
        currentTimeMs < wordTimestamps[i + 1].startMs) {
      activeWordIndex = i;
      break;
    }
  }

  // If past the last word, show nothing
  if (activeWordIndex === -1 && currentTimeMs > (wordTimestamps[wordTimestamps.length - 1]?.endMs ?? 0)) {
    return null;
  }
  // If before the first word, show nothing
  if (activeWordIndex === -1 && currentTimeMs < (wordTimestamps[0]?.startMs ?? 0)) {
    return null;
  }

  if (activeWordIndex === -1) return null;

  // Determine which group of words to display
  const groupIndex = Math.floor(activeWordIndex / WORDS_PER_GROUP);
  const groupStart = groupIndex * WORDS_PER_GROUP;
  const groupEnd = Math.min(groupStart + WORDS_PER_GROUP, wordTimestamps.length);
  const groupWords = wordTimestamps.slice(groupStart, groupEnd);

  // Container entrance animation (spring in when group changes)
  const groupStartMs = groupWords[0].startMs;
  const groupStartFrame = (groupStartMs / 1000) * fps;
  const containerSpring = spring({
    frame: frame - groupStartFrame,
    fps,
    config: { mass: 1, damping: 20, stiffness: 200 },
    durationInFrames: 10,
  });

  const containerY = interpolate(containerSpring, [0, 1], [20, 0]);
  const containerOpacity = containerSpring;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 180,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        padding: '0 40px',
        opacity: containerOpacity,
        transform: `translateY(${containerY}px)`,
      }}
    >
      <div
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          borderRadius: 12,
          padding: '16px 24px',
          display: 'flex',
          flexWrap: 'wrap',
          whiteSpace: 'normal',
          justifyContent: 'center',
          gap: '4px 10px',
          maxWidth: 940,
          overflow: 'hidden',
        }}
      >
        {groupWords.map((wt, i) => {
          const globalIndex = groupStart + i;
          const isActive = globalIndex === activeWordIndex;
          const isPast = globalIndex < activeWordIndex;

          // Word pop-in animation — opacity only. No translate, no scale, no
          // weight change — anything that affects layout causes flex re-flow,
          // which makes the entire caption box "shake" word-by-word.
          const wordStartFrame = (wt.startMs / 1000) * fps;
          const wordSpring = spring({
            frame: frame - wordStartFrame,
            fps,
            config: { mass: 1, damping: 22, stiffness: 250 },
            durationInFrames: 8,
          });

          return (
            <span
              key={`${groupIndex}-${i}`}
              style={{
                fontFamily: montserratFamily,
                fontSize: 52,
                fontWeight: 800, // constant — must not change between active/inactive
                color: isActive ? accentColor : isPast ? '#ffffff' : 'rgba(255, 255, 255, 0.55)',
                textTransform: 'uppercase',
                letterSpacing: 1,
                display: 'inline-block',
                opacity: wordSpring,
                textShadow: isActive
                  ? `0 0 24px ${accentColor}80, 0 2px 4px rgba(0,0,0,0.6)`
                  : '0 2px 4px rgba(0,0,0,0.6)',
              }}
            >
              {wt.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};
