// Настройки рендера. Размер, длина и частота кадров задаются у композиции в src/Root.tsx.
import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('png');     // без потерь до кодека: тёмные градиенты в jpeg идут полосами
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('angle');   // без этого трёхмерные сцены в безголовом Chrome не рисуются
