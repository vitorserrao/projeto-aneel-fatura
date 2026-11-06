import React from 'react';
import type { Analise } from '../lib/analise';
import type { ResultadoSeries } from '../lib/series';
import type { InvoiceFormData } from '../types/energy';

/** Etapa 3 — Análise e E-PI (em construção). */
export const EtapaAnalise: React.FC<{
  analise: Analise;
  series: ResultadoSeries | null;
  progressoSeries: { feitas: number; total: number } | null;
  cacheCurva: Map<string, number | null>;
  aoAtualizarAcl: (m: Partial<InvoiceFormData>) => void;
  aoVoltar: () => void;
}> = () => null;
