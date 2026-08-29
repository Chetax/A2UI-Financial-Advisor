// src/components/Text.tsx
import type { TextProps } from '../a2ui/types';
import type { JSX } from 'react';

const variantTag: Record<TextProps['variant'], keyof JSX.IntrinsicElements> = {
  heading: 'h2',
  subheading: 'h3',
  body: 'p',
  caption: 'span',
  metric: 'span',
  label: 'span',
};

const variantClass: Record<TextProps['variant'], string> = {
  heading: 'font-serif text-2xl text-inkText',
  subheading: 'font-serif text-lg text-inkText',
  body: 'text-base text-inkText',
  caption: 'text-sm text-muted',
  metric: 'font-mono text-3xl text-gold',
  label: 'text-xs font-medium uppercase tracking-wider text-muted',
};

export function Text({ content, variant }: TextProps) {
  const Tag = variantTag[variant];
  return <Tag className={variantClass[variant]}>{content}</Tag>;
}