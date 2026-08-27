// src/components/Container.tsx
import type { ContainerProps } from '../a2ui/types';

const alignClass: Record<NonNullable<ContainerProps['align']>, string> = {
  start: 'items-start',
  center: 'items-center',
  end: 'items-end',
  stretch: 'items-stretch',
};

interface ContainerComponentProps extends ContainerProps {
  children?: React.ReactNode;
}

export function Container({ direction, gap, align, children }: ContainerComponentProps) {
  const flexDir = direction === 'row' ? 'flex-row' : 'flex-col';
  const alignCls = align ? alignClass[align] : '';

  return (
    <div
      className={`flex ${flexDir} ${alignCls}`}
      style={{ gap: `${gap}px` }}
    >
      {children}
    </div>
  );
}