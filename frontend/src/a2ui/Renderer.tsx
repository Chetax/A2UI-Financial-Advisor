// src/a2ui/Renderer.tsx
import type { Component, Action } from './types';
import { Text } from '../components/Text';
import { Button } from '../components/Button';
import { TextField } from '../components/TextField';
import { Container } from '../components/Container';
import { Card } from '../components/Card';
import { Form } from '../components/Form';
import { useFormContext } from './FormContext';

interface RendererProps {
  node: Component;
  onAction?: (action: Action) => void;
  onSubmit?: (action: Action, payload: Record<string, string>) => void;
}

export function Renderer({ node, onAction, onSubmit }: RendererProps) {
  const form = useFormContext();

  switch (node.type) {
    case 'text':
      return <Text {...node.props} />;

    case 'button':
      return <Button {...node.props} onAction={onAction} />;

    case 'text-field':
      return (
        <TextField
          {...node.props}
          value={form ? form.values[node.props.name] ?? '' : node.props.value}
          onChange={form ? form.setValue : undefined}
        />
      );

    case 'container':
      return (
        <Container {...node.props}>
          {node.children.map((child, i) => (
            <Renderer node={child} key={i} onAction={onAction} onSubmit={onSubmit} />
          ))}
        </Container>
      );

    case 'card':
      return (
        <Card {...node.props}>
          {node.children.map((child, i) => (
            <Renderer node={child} key={i} onAction={onAction} onSubmit={onSubmit} />
          ))}
        </Card>
      );

    case 'form':
      return (
        <Form {...node.props} onSubmit={onSubmit}>
          {node.children.map((child, i) => (
            <Renderer node={child} key={i} onAction={onAction} onSubmit={onSubmit} />
          ))}
        </Form>
      );

    default: {
      const _exhaustive: never = node;
      return null;
    }
  }
}