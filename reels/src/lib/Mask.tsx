// Шторка для строки: строка выезжает из-под неё снизу, выносные элементы букв не режутся.
// Сама строка получает className, по нему её находит таймлайн GSAP.
import React from 'react';
import { sans } from './brand';

type Props = { px: number; color: string; children: React.ReactNode; className?: string; weight?: number; style?: React.CSSProperties };

export const Mask: React.FC<Props> = ({ px, color, children, className, weight = 800, style }) => (
  <div style={{ overflow: 'hidden', height: px * 1.24, marginBottom: -px * 0.2 }}>
    <div className={className} style={{
      fontFamily: sans, fontWeight: weight, fontSize: px, lineHeight: `${px * 1.24}px`,
      letterSpacing: '-0.04em', whiteSpace: 'nowrap', color, ...style,
    }}>
      {children}
    </div>
  </div>
);
