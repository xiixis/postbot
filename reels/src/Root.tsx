// Список роликов. Каждый ролик — своя папка в src и своя композиция здесь.
// defaultProps пишутся буквально: иначе кнопка Save в студии не сможет их переписать.
import { Composition } from 'remotion';
import { Film } from './claude-montage/Film';

export const Root = () => (
  <>
    <Composition
      id="ClaudeMontage"
      component={Film}
      defaultProps={{ music: 'a' as const }}
      durationInFrames={450}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
