import { useState } from 'react';
import type { FormProps, Action } from '../a2ui/types';
import { FormContext } from '../a2ui/FormContext';

interface FormComponentProps extends FormProps {
  children?: React.ReactNode;
  onSubmit?: (action: Action, payload: Record<string, string>) => void;
}

export function Form({ submitLabel, action, children, onSubmit }: FormComponentProps) {
  const [values, setValues] = useState<Record<string, string>>({});

  const setValue = (name: string, value: string) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.(action, values);
  };

  return (
    <FormContext.Provider value={{ values, setValue }}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full">
        {children}
        <button
          type="submit"
          className="self-start px-5 py-2.5 rounded-lg bg-gold text-ink font-semibold text-sm hover:brightness-95 active:scale-[0.98] transition-all"
        >
          {submitLabel}
        </button>
      </form>
    </FormContext.Provider>
  );
}