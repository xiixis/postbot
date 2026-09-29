// Список роликов. Каждый ролик — своя папка в src и своя композиция здесь.
// defaultProps пишутся буквально: иначе кнопка Save в студии не сможет их переписать.
import { Composition, Folder } from 'remotion';
import { Film } from './claude-montage/Film';
import { GsapProbe } from './lab/GsapProbe';
import { ThreeProbe } from './lab/ThreeProbe';

const V = { fps: 30, width: 1080, height: 1920 } as const;

export const Root = () => (
  <>
    <Composition id="ClaudeMontage" component={Film} defaultProps={{ music: 'a' as const }} durationInFrames={450} {...V} />

    {/* Пробы приёмов: на них ссылаются наши скилы. Это не ролики, а проверенные образцы кода. */}
    <Folder name="lab">
      <Composition id="Lab-Gsap" component={GsapProbe} durationInFrames={150} {...V} />
      <Composition id="Lab-Three" component={ThreeProbe} durationInFrames={150} {...V} />
    </Folder>
  </>
);
