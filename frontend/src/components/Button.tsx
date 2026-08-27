import type { ButtonProps, Action } from '../a2ui/types';

interface ButtonComponentProps extends ButtonProps {
  onAction?: (action: Action) => void;
}

const variantClass: Record<ButtonProps['variant'], string> = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98] shadow-sm',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 active:scale-[0.98]',
  ghost: 'bg-transparent text-blue-600 hover:bg-blue-50 active:scale-[0.98]',
};

export function Button({ label, action, variant, onAction }: ButtonComponentProps) {
  return (
    <button
      type="button"
      className={`px-4 py-2.5 rounded-lg font-medium text-sm transition-all ${variantClass[variant]}`}
      onClick={() => onAction?.(action)}
    >
      {label}
    </button>
  );
}