import type { CardProps } from '../a2ui/types';

interface CardComponentProps extends CardProps {
  children?: React.ReactNode;
}

export function Card({ title, subtitle, children }: CardComponentProps) {
  return (
    <div className="rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-shadow p-6 bg-white">
      {title && <h3 className="text-xl font-semibold text-gray-900">{title}</h3>}
      {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      <div className="mt-4 flex flex-col gap-3 items-start">{children}</div>
    </div>
  );
}