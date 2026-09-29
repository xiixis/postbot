// Раскладка клавиатуры: обычная ANSI на 61 клавишу с русскими и латинскими буквами.
// Единица длины — шаг клавиши. Ряд шириной 15 единиц, рядов пять.
export type Kind = 'char' | 'mod' | 'enter' | 'space';
export type Key = { id: string; row: number; x: number; z: number; w: number; en: string; ru: string; kind: Kind };

type Spec = [en: string, ru?: string, w?: number, kind?: Kind];

const ROWS: Spec[][] = [
  [['`', 'ё'], ['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7'], ['8'], ['9'], ['0'], ['-'], ['='], ['delete', '', 2, 'mod']],
  [['tab', '', 1.5, 'mod'], ['q', 'й'], ['w', 'ц'], ['e', 'у'], ['r', 'к'], ['t', 'е'], ['y', 'н'], ['u', 'г'], ['i', 'ш'], ['o', 'щ'], ['p', 'з'], ['[', 'х'], [']', 'ъ'], ['\\', '', 1.5]],
  [['caps', '', 1.75, 'mod'], ['a', 'ф'], ['s', 'ы'], ['d', 'в'], ['f', 'а'], ['g', 'п'], ['h', 'р'], ['j', 'о'], ['k', 'л'], ['l', 'д'], [';', 'ж'], ["'", 'э'], ['enter', '', 2.25, 'enter']],
  [['shift', '', 2.25, 'mod'], ['z', 'я'], ['x', 'ч'], ['c', 'с'], ['v', 'м'], ['b', 'и'], ['n', 'т'], ['m', 'ь'], [',', 'б'], ['.', 'ю'], ['/', '.'], ['shift', '', 2.75, 'mod']],
  [['ctrl', '', 1.25, 'mod'], ['opt', '', 1.25, 'mod'], ['cmd', '', 1.25, 'mod'], ['', '', 6.25, 'space'], ['cmd', '', 1.25, 'mod'], ['opt', '', 1.25, 'mod'], ['fn', '', 1.25, 'mod'], ['ctrl', '', 1.25, 'mod']],
];

export const WIDTH = 15;
export const DEPTH = ROWS.length;

export const KEYS: Key[] = ROWS.flatMap((specs, row) => {
  let from = 0;
  return specs.map(([en, ru = '', w = 1, kind = 'char'], i) => {
    const key: Key = { id: `${row}-${i}`, row, x: from + w / 2 - WIDTH / 2, z: row - (DEPTH - 1) / 2, w, en, ru, kind };
    from += w;
    return key;
  });
});

export const ENTER = KEYS.find((k) => k.kind === 'enter') as Key;
export const SPACE = KEYS.find((k) => k.kind === 'space') as Key;
export const LETTERS = KEYS.filter((k) => k.kind === 'char' && k.ru !== '' && k.row > 0);

export const byRu = (ch: string) => (ch === ' ' ? SPACE : (KEYS.find((k) => k.ru === ch && k.row > 0) as Key));
export const byEn = (ch: string) => KEYS.find((k) => k.en === ch && k.kind === 'char') as Key;
