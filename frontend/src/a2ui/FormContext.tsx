// src/a2ui/FormContext.tsx
import { createContext, useContext } from 'react';

interface FormContextValue {
  values: Record<string, string>;
  setValue: (name: string, value: string) => void;
}

// null default = "no Form ancestor" — lets text-field detect whether
// it's inside a form at all, and behave as a plain uncontrolled field
// if not (e.g. if the LLM ever puts a text-field outside a form).
const FormContext = createContext<FormContextValue | null>(null);

export function useFormContext() {
  return useContext(FormContext);
}

export { FormContext };