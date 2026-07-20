import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { loadFont as loadJakarta } from '@remotion/google-fonts/PlusJakartaSans';

const fraunces = loadFraunces('normal', { weights: ['400', '600', '700', '900'], subsets: ['latin'] });
const jakarta = loadJakarta('normal', { weights: ['400', '500', '600', '700', '800'], subsets: ['latin'] });

// Fraunces = editorial display serif (Sabi headlines/tagline). Jakarta = UI / numbers.
export const frauncesFamily = fraunces.fontFamily;
export const jakartaFamily = jakarta.fontFamily;
