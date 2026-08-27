import type { TextFieldProps } from '../a2ui/types';

interface TextFieldComponentProps extends TextFieldProps {
  onChange?: (name: string, value: string) => void;
}

export function TextField({
  name, label, placeholder, value, inputType, onChange,
}: TextFieldComponentProps) {
  return (
    <div className="flex flex-col gap-1.5 w-full">
      <label htmlFor={name} className="text-xs font-semibold uppercase tracking-wide text-gray-500">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={inputType}
        placeholder={placeholder}
        value={value ?? ''}
        onChange={(e) => onChange?.(name, e.target.value)}
        className="border border-gray-300 rounded-lg px-3.5 py-2.5 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
      />
    </div>
  );
}