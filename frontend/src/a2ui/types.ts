// src/a2ui/types.ts
// TypeScript mirror of backend/app/schema.py — the frontend half of the
// A2UI contract. No `any` on any of these.

// --- shared building blocks -------------------------------------------

export interface Action {
  id: string,
  payload?: Record<string, unknown>;
}

export interface TextProps {
  content: string
  variant: "heading" | "subheading" | "body" | "caption" | "metric" | "label"
}

// --- leaf components -----------------------------------------------------
// each one is `{ type: '<literal>', props: <PropsType> }` — no children

export interface TextComponent {
  type: 'text';
  props: TextProps;
}

export interface ButtonProps {
  label: string;
  action: Action;
  variant: 'primary' | 'secondary' | 'ghost';
}
export interface ButtonComponent {
  type: 'button';
  props: ButtonProps;
}

export interface TextFieldProps {
  name: string;
  label: string;
  placeholder?: string;
  value?: string;
  inputType: 'text' | 'number' | 'email';
}

export interface TextFieldComponent {
  type: 'text-field';
  props: TextFieldProps;
}


// --- branch components -----------------------------------------------
// these have `children: Component[]` — Component isn't defined yet below,
// but TS resolves that forward reference for free

// ContainerProps -> ContainerComponent (direction, gap, align?)
export interface ContainerProps {
  direction: 'row' | 'column';
  gap: number;
  align?: 'start' | 'center' | 'end' | 'stretch';
}
export interface ContainerComponent {
  type: 'container';
  props: ContainerProps;
  children: Component[];
}



export interface CardProps {
  title?: string;
  subtitle?: string;
}

export interface CardComponent {
  type: 'card';
  props: CardProps;
  children: Component[];
}

export interface FormProps {
  submitLabel: string;
  action: Action;
}

export interface FormComponent {
  type: 'form';
  props: FormProps;
  children: Component[];
}

// --- the discriminated union -------------------------------------------

export type Component =
  | ContainerComponent
  | CardComponent
  | TextComponent
  | ButtonComponent
  | TextFieldComponent
  | FormComponent;

// --- top-level envelope --------------------------------------------------

export interface A2UIResponse {
  message?: string;
  component: Component;
}
// --- the /chat request contract (mirrors main.py's ChatRequest) ---------

export interface ChatRequest {
  session_id: string;
  message?: string;
  action_id?: string;
  action_payload?: Record<string, unknown>;
}