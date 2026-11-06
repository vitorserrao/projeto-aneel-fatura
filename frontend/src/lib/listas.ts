/**
 * Listas de apoio do formulário, usadas só quando a API não responde às
 * consultas de distribuidoras/subgrupos. Nenhum valor tarifário aqui.
 */

export const DISTRIBUIDORAS_APOIO: string[] = ['COPEL-DIS', 'ENEL-SP', 'CEMIG-D', 'CPFL-PAULISTA', 'LIGHT'];

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
