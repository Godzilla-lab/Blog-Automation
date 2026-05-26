// Hexa AI Agency — Brand Constants
// Source: hexaaiagency.com

// Portrait (Story highlights)
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;
export const DURATION = 180; // 6 seconds

// Landscape (YouTube / general)
export const LANDSCAPE_WIDTH = 1920;
export const LANDSCAPE_HEIGHT = 1080;

// Colors
export const COLORS = {
  background: '#07070f',
  primary: '#00e5cc',
  secondary: '#00b4ff',
  purple: '#7b61ff',
  orangeStart: '#ff6b00',
  orangeEnd: '#ff00aa',
  textPrimary: '#ffffff',
  textMuted: '#666680',
  surface: '#0f0f1a',
  faqAccent: '#ff6b6b',
} as const;

// Spring config — premium, not bouncy
export const SPRING_CONFIG = {
  mass: 1,
  damping: 18,
  stiffness: 80,
} as const;

// Stagger delay between elements (frames)
export const STAGGER = 6;
