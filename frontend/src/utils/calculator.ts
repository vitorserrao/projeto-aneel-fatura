/**
 * Listas de apoio do formulário (fallback quando a API não responde) e
 * formatação. NENHUM cálculo tarifário vive no front: toda fatura, comparação,
 * planejamento e E-PI vêm da API (motor validado com faturas reais).
 */
import { Distributor, TariffModalidade } from '../types/energy';

export const DISTRIBUTORS: Distributor[] = [
  {
    id: 'COPEL-DIS',
    sigAgente: 'COPEL-DIS',
    name: 'Copel Distribuição (Paraná)',
    state: 'PR',
    region: 'Sul',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B', 'B3'],
    baseTusdDemanda: 23.90,
    baseTePonta: 0.795,
    baseTeForaPonta: 0.078,
    baseTusdPonta: 0.498,
    baseTusdForaPonta: 0.026,
    baseConvencionalKwh: 0.492,
  },
  {
    id: 'ENEL-SP',
    sigAgente: 'ENEL-SP',
    name: 'Enel Distribuição São Paulo',
    state: 'SP',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B', 'B3'],
    baseTusdDemanda: 25.44,
    baseTePonta: 0.812,
    baseTeForaPonta: 0.082,
    baseTusdPonta: 0.5164,
    baseTusdForaPonta: 0.0282,
    baseConvencionalKwh: 0.518,
  },
  {
    id: 'CEMIG-D',
    sigAgente: 'CEMIG-D',
    name: 'Cemig Distribuição (Minas Gerais)',
    state: 'MG',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B', 'B3'],
    baseTusdDemanda: 28.12,
    baseTePonta: 0.845,
    baseTeForaPonta: 0.089,
    baseTusdPonta: 0.542,
    baseTusdForaPonta: 0.031,
    baseConvencionalKwh: 0.548,
  },
  {
    id: 'CPFL-PAULISTA',
    sigAgente: 'CPFL-PAULISTA',
    name: 'CPFL Paulista',
    state: 'SP',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B'],
    baseTusdDemanda: 26.85,
    baseTePonta: 0.822,
    baseTeForaPonta: 0.085,
    baseTusdPonta: 0.528,
    baseTusdForaPonta: 0.029,
    baseConvencionalKwh: 0.532,
  },
  {
    id: 'LIGHT',
    sigAgente: 'LIGHT',
    name: 'Light Serviços de Eletricidade (Rio de Janeiro)',
    state: 'RJ',
    region: 'Sudeste',
    subgroups: ['A4', 'A3a', 'A2', 'Optante B'],
    baseTusdDemanda: 29.80,
    baseTePonta: 0.865,
    baseTeForaPonta: 0.092,
    baseTusdPonta: 0.565,
    baseTusdForaPonta: 0.033,
    baseConvencionalKwh: 0.568,
  },
];

export const SUBGROUPS = [
  { id: 'A1', label: 'A1 (≥ 230 kV)' },
  { id: 'A2', label: 'A2 (88 kV a 138 kV)' },
  { id: 'A3', label: 'A3 (69 kV)' },
  { id: 'A3a', label: 'A3a (30 kV a 44 kV)' },
  { id: 'A4', label: 'A4 (2,3 kV a 25 kV)' },
  { id: 'AS', label: 'AS (Subterrâneo)' },
  { id: 'B1', label: 'B1 (Residencial)' },
  { id: 'B2', label: 'B2 (Rural)' },
  { id: 'B3', label: 'B3 (Demais classes)' },
  { id: 'B4', label: 'B4 (Iluminação Pública)' },
];

export const MODALIDADE_OPTIONS: { id: TariffModalidade; label: string }[] = [
  { id: 'verde', label: 'Verde' },
  { id: 'azul', label: 'Azul' },
  { id: 'optante_b', label: 'Optante B' },
  { id: 'branca', label: 'Branca' },
  { id: 'convencional', label: 'Convencional Monômia' },
];

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}
