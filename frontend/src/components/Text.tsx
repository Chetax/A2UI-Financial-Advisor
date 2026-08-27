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
  heading: 'text-2xl font-bold text-gray-900',
  subheading: 'text-lg font-semibold text-gray-800',
  body: 'text-base text-gray-700',
  caption: 'text-sm text-gray-500',
  metric: 'text-3xl font-bold text-blue-600',
  label: 'text-xs font-medium uppercase tracking-wide text-gray-500',
};

export function Text({ content, variant }: TextProps) {
  const Tag = variantTag[variant];
  return <Tag className={variantClass[variant]}>{content}</Tag>;
}