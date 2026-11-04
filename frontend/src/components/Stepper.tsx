import React from 'react';
import { Check, Edit2 } from 'lucide-react';

interface StepperProps {
  currentStep: 1 | 2;
  onGoToStep: (step: 1 | 2) => void;
}

export const Stepper: React.FC<StepperProps> = ({ currentStep, onGoToStep }) => {
  return (
    <nav aria-label="Progresso do Fluxo" className="w-full mb-8 no-print">
      <div className="w-full bg-white p-2 rounded-2xl shadow-sm flex flex-col sm:flex-row items-center gap-2 border border-slate-200/80">
        {/* ========================================================================= */}
        {/* CARD DO PASSO 1 */}
        {/* ========================================================================= */}
        {currentStep === 1 ? (
          /* Passo 1 Ativo */
          <div className="w-full sm:flex-1 flex items-center justify-between sm:justify-center gap-3 py-3 px-5 rounded-xl bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-500 text-slate-950 shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-black bg-slate-950 text-amber-300 shadow-sm shrink-0">
                1
              </div>
              <div className="flex flex-col">
                <span className="text-sm text-slate-950 font-bold">
                  Passo 1: Dados de Consumo
                </span>
                <span className="text-xs text-slate-900/85 font-medium">
                  Inserir parâmetros da fatura
                </span>
              </div>
            </div>
            <span className="w-2.5 h-2.5 rounded-full bg-slate-950 animate-ping"></span>
          </div>
        ) : (
          /* Passo 1 Concluído (Clicável para voltar e editar) */
          <button
            onClick={() => onGoToStep(1)}
            type="button"
            className="w-full sm:flex-1 flex items-center justify-between sm:justify-center gap-3 py-3 px-5 rounded-xl transition-all duration-200 bg-slate-50 hover:bg-slate-100 text-left group cursor-pointer border border-slate-200/50"
          >
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-amber-500 text-slate-950 font-bold shadow-sm shrink-0">
                <Check className="w-4 h-4 stroke-[3]" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm text-slate-900 font-semibold group-hover:text-slate-950">
                  Passo 1: Dados de Consumo
                </span>
                <span className="text-xs text-amber-700 flex items-center gap-1 group-hover:underline font-medium">
                  Editar dados inseridos
                  <Edit2 className="w-3 h-3 text-amber-600 inline" />
                </span>
              </div>
            </div>
            <span className="text-[10px] bg-amber-100/90 text-amber-900 border border-amber-300/80 px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">
              Concluído
            </span>
          </button>
        )}

        {/* ========================================================================= */}
        {/* CARD DO PASSO 2 */}
        {/* ========================================================================= */}
        {currentStep === 2 ? (
          /* Passo 2 Ativo */
          <div className="w-full sm:flex-1 flex items-center justify-between sm:justify-center gap-3 py-3 px-5 rounded-xl bg-gradient-to-r from-amber-400 via-amber-500 to-yellow-500 text-slate-950 shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-sm font-black bg-slate-950 text-amber-300 shadow-sm shrink-0">
                2
              </div>
              <div className="flex flex-col">
                <span className="text-sm text-slate-950 font-bold">
                  Passo 2: Diagnóstico &amp; Fatura
                </span>
                <span className="text-xs text-slate-900/85 font-medium">
                  Análise Tarifária ANEEL
                </span>
              </div>
            </div>
            <span className="w-2.5 h-2.5 rounded-full bg-slate-950 animate-ping"></span>
          </div>
        ) : (
          /* Passo 2 Inativo (Pendente) */
          <button
            onClick={() => onGoToStep(2)}
            type="button"
            className="w-full sm:flex-1 flex items-center justify-between sm:justify-center gap-3 py-3 px-5 rounded-xl transition-all duration-200 bg-slate-50 hover:bg-slate-100 text-left group cursor-pointer border border-slate-200/50"
          >
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-slate-200 text-slate-700 font-bold text-xs shadow-xs shrink-0">
                2
              </div>
              <div className="flex flex-col">
                <span className="text-sm text-slate-700 font-semibold group-hover:text-slate-900 transition-colors">
                  Passo 2: Diagnóstico &amp; Fatura
                </span>
                <span className="text-xs text-slate-500 font-medium">
                  Análise Tarifária ANEEL
                </span>
              </div>
            </div>
            <span className="text-[10px] bg-slate-200/80 text-slate-600 px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">
              Pendente
            </span>
          </button>
        )}
      </div>
    </nav>
  );
};
