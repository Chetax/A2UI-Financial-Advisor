import type { CardProps } from '../a2ui/types';

interface CardComponentProps extends CardProps {
  children?: React.ReactNode;
}

export function Card({ title, subtitle, children }: CardComponentProps) {
  return (
    <div className="rounded-xl border border-hairline bg-surface p-6">
      {title && <h3 className="font-serif text-xl text-inkText">{title}</h3>}
      {subtitle && <p className="text-sm text-muted mt-1">{subtitle}</p>}
      {title && <div className="mt-3 h-0.5 w-8 bg-gold" />}
      <div className="mt-4 flex flex-col gap-3 items-start">{children}</div>
    </div>
  );
}