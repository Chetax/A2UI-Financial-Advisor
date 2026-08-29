import type { ButtonProps, Action } from '../a2ui/types';

interface ButtonComponentProps extends ButtonProps {
  onAction?: (action: Action) => void;
}

const variantClass: Record<ButtonProps['variant'], string> = {
  primary: 'bg-gold text-ink hover:brightness-95 active:scale-[0.98]',
  secondary: 'bg-surface text-inkText border border-hairline hover:border-muted active:scale-[0.98]',
  ghost: 'bg-transparent text-gold hover:bg-surface active:scale-[0.98]',
};

export function Button({ label, action, variant, onAction }: ButtonComponentProps) {
  return (
    <button
      type="button"
      className={`px-4 py-2.5 rounded-lg font-semibold text-sm transition-all ${variantClass[variant]}`}
      onClick={() => onAction?.(action)}
    >
      {label}
    </button>
  );
}