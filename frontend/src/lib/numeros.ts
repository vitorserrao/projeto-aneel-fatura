import type { NumOpc } from '../types/energy';

/** Campo não informado (null/undefined/NaN). */
export const vazio = (v: NumOpc | undefined): boolean =>
  v === null || v === undefined || Number.isNaN(v);

/** Valor para a API depois da validação (null só chega aqui em campo não aplicável). */
export const num = (v: NumOpc | undefined): number => (vazio(v) ? 0 : (v as number));
