// Список роликов. Каждый ролик — своя папка в src и своя композиция здесь.
// defaultProps пишутся буквально: иначе кнопка Save в студии не сможет их переписать.
import { Composition, Folder } from 'remotion';
import { Film } from './claude-montage/Film';
import { GsapProbe } from './lab/GsapProbe';
import { ThreeProbe } from './lab/ThreeProbe';
import { Words } from './v2-words/Words';
import { Keys } from './v3-keys/Keys';
import { Desk } from './v4-desk/Desk';
import { Type } from './r4-type/Type';
import { Space } from './r5-space/Space';
import { Voice } from './r6-voice/Voice';
import { MockDots } from './mock/Dots';
import { WordsLayer } from './mock/WordsLayer';
import { MockLayers } from './mock/Layers';
import { MockPencil } from './mock/Pencil';
import { MockChain } from './mock/Chain';
import { Chain } from './r7-chain/Chain';
import { LENGTH as CHAIN } from './r7-chain/motion';
import { LayersReel } from './r8-layers/Layers';
import { LENGTH as LAYERS_LENGTH } from './r8-layers/motion';
import { LENGTH } from './series/grid';

const V = { fps: 30, width: 1080, height: 1920 } as const;

export const Root = () => (
  <>
    <Composition id="ClaudeMontage" component={Film} defaultProps={{ music: 'a' as const }} durationInFrames={450} {...V} />
    <Composition id="ClaudeWords" component={Words} defaultProps={{ music: true }} durationInFrames={450} {...V} />
    <Composition id="ClaudeKeys" component={Keys} defaultProps={{ music: true }} durationInFrames={450} {...V} />
    <Composition id="ClaudeDesk" component={Desk} defaultProps={{ music: true }} durationInFrames={450} {...V} />

    {/* Серия 2: «дал текст, подключил скилы, Claude смонтировал» */}
    <Composition id="SeriesType" component={Type} defaultProps={{ music: true }} durationInFrames={LENGTH} {...V} />
    <Composition id="SeriesSpace" component={Space} defaultProps={{ music: true }} durationInFrames={LENGTH} {...V} />
    <Composition id="SeriesVoice" component={Voice} defaultProps={{ music: true }} durationInFrames={LENGTH} {...V} />

    {/* Серия 3: три разных мира */}
    <Composition id="Chain" component={Chain} defaultProps={{ music: true }} durationInFrames={CHAIN} {...V} />
    <Composition id="Layers" component={LayersReel} defaultProps={{ music: true }} durationInFrames={LAYERS_LENGTH} {...V} />

    {/* Макеты третьей серии: ключевые кадры, по одному на кадр композиции */}
    <Folder name="mock">
      <Composition id="MockDots" component={MockDots} durationInFrames={4} {...V} />
      <Composition id="WordsLayer" component={WordsLayer} defaultProps={{ layer: 0 }} durationInFrames={1} {...V} />
      <Composition id="MockLayers" component={MockLayers} durationInFrames={4} {...V} />
      <Composition id="MockPencil" component={MockPencil} durationInFrames={4} {...V} />
      <Composition id="MockChain" component={MockChain} durationInFrames={4} {...V} />
    </Folder>

    {/* Пробы приёмов: на них ссылаются наши скилы. Это не ролики, а проверенные образцы кода. */}
    <Folder name="lab">
      <Composition id="Lab-Gsap" component={GsapProbe} durationInFrames={150} {...V} />
      <Composition id="Lab-Three" component={ThreeProbe} durationInFrames={150} {...V} />
    </Folder>
  </>
);
