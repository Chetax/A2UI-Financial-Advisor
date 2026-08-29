import type { TextFieldProps } from '../a2ui/types';

interface TextFieldComponentProps extends TextFieldProps {
  onChange?: (name: string, value: string) => void;
}

export function TextField({
  name, label, placeholder, value, inputType, onChange,
}: TextFieldComponentProps) {
  return (
    <div className="flex flex-col gap-1.5 w-full">
      <label htmlFor={name} className="text-xs font-medium uppercase tracking-wider text-muted">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={inputType}
        placeholder={placeholder}
        value={value ?? ''}
        onChange={(e) => onChange?.(name, e.target.value)}
        className="bg-ink border border-hairline rounded-lg px-3.5 py-2.5 text-sm text-inkText placeholder:text-muted font-mono focus:outline-none focus:ring-2 focus:ring-gold focus:border-gold transition-colors"
      />
    </div>
  );
}