import { loadFont as loadOrbitron } from '@remotion/google-fonts/Orbitron';
import { loadFont as loadSyne } from '@remotion/google-fonts/Syne';
import { loadFont as loadBebas } from '@remotion/google-fonts/BebasNeue';
import { loadFont as loadMontserrat } from '@remotion/google-fonts/Montserrat';

const orbitron = loadOrbitron('normal', { subsets: ['latin'] });
const syne = loadSyne('normal', { subsets: ['latin'] });
const bebas = loadBebas('normal', { subsets: ['latin'] });
const montserrat = loadMontserrat('normal', { subsets: ['latin'] });

export const orbitronFamily = orbitron.fontFamily;
export const syneFamily = syne.fontFamily;

// Reel fonts — bold, punchy, great for kinetic captions
export const bebasFamily = bebas.fontFamily;
export const montserratFamily = montserrat.fontFamily;
