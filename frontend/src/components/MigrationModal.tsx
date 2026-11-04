import React, { useState } from 'react';
import {
  X,
  FileCheck2,
  Download,
  Copy,
  Check,
  Building,
  ShieldCheck,
  Calendar,
  AlertCircle,
} from 'lucide-react';
import { AuditResult, InvoiceFormData } from '../types/energy';
import { formatCurrency } from '../utils/calculator';

interface MigrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  audit: AuditResult;
  formData: InvoiceFormData;
}

export const MigrationModal: React.FC<MigrationModalProps> = ({
  isOpen,
  onClose,
  audit,
  formData,
}) => {
  const [copied, setCopied] = useState(false);
  const [protocolSubmitted, setProtocolSubmitted] = useState(false);
  const [protocolNumber] = useState(
    () => `PROT-ANEEL-${new Date().getFullYear()}-${Math.floor(100000 + Math.random() * 900000)}`
  );

  if (!isOpen) return null;

  const formalPetitionText = `ILMO. SR. DIRETOR DE RELACIONAMENTO COM CLIENTES CORPORATIVOS
CONCESSIONÁRIA: ${audit.distribuidoraNome.toUpperCase()}

REFERÊNCIA: SOLICITAÇÃO FORMAL DE ENQUADRAMENTO TARIFÁRIO - RESOLUÇÃO NORMATIVA ANEEL Nº 1.000/2021
UNIDADE CONSUMIDORA (UC): ${formData.ucCode} - ${formData.unidadeNome}
SUBGRUPO TARIFÁRIO: ${audit.subgrupo} (TENSÃO NOMINAL DE ATENDIMENTO)
DEMANDA CONTRATADA: ${formData.demandaContratada} kW

Prezados Senhores,

Vimos por meio desta solicitar formalmente a alteração da modalidade tarifária de faturamento da Unidade Consumidora supracitada:

1. Modalidade Atual de Faturamento: CONVENCIONAL
2. Modalidade Solicitada: HORÁRIA VERDE (Artigo 145 e seguintes da REN 1.000/2021)
3. Demanda Única Contratada: ${formData.demandaContratada} kW no posto Fora de Ponta.
4. Economia Estimada em Auditoria Regulatória: ${formatCurrency(audit.economiaMensal)}/mês (${formatCurrency(audit.economiaAnual)}/ano).

Informamos que a unidade já dispõe de medição eletrônica horossazonal apta à tarifação diferenciada nos postos Ponta e Fora Ponta. Solicitamos a efetivação no ciclo de faturamento subsequente, conforme os prazos regulatórios vigentes.

Termos em que,
Pede Deferimento.

Data: ${new Date().toLocaleDateString('pt-BR')}
Auditoria Certificada: ACR × ACL • Simulador & Reenquadramento Tarifário - ID #${audit.simId}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(formalPetitionText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownload = () => {
    const blob = new Blob([formalPetitionText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Requerimento_Migracao_Tarifa_Verde_${formData.ucCode}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[92vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="p-5 sm:p-6 bg-gradient-to-r from-amber-50 to-yellow-50 border-b border-amber-200/70 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-400 text-slate-950 flex items-center justify-center shadow-2xs font-bold">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold text-slate-900">
                Solicitação de Migração para Tarifa Verde
              </h3>
              <p className="text-xs text-slate-600">
                Enquadramento homologado sem custo de migração pela ANEEL
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/50 flex items-center justify-center transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-5 text-sm text-slate-700">
          {protocolSubmitted ? (
            <div className="p-6 bg-emerald-50 rounded-2xl border border-emerald-200 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center mx-auto shadow-md">
                <Check className="w-6 h-6 stroke-[3]" />
              </div>
              <h4 className="text-lg font-bold text-emerald-950">
                Dossiê Formal de Migração Gerado com Sucesso!
              </h4>
              <p className="text-xs text-emerald-800 max-w-md mx-auto">
                Seu requerimento técnico foi compilado em conformidade com o Art. 145 da Resolução
                Normativa ANEEL nº 1.000/2021.
              </p>
              <div className="p-3 bg-white rounded-xl border border-emerald-300 font-mono-num font-bold text-slate-800 text-sm inline-block shadow-2xs">
                Protocolo: {protocolNumber}
              </div>
              <p className="text-[11px] text-emerald-700">
                Prazo regulatório da concessionária: até 1 ciclo de faturamento para implementação
                sem interrupção de energia.
              </p>
            </div>
          ) : (
            <>
              {/* Resumo da Mudança */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">
                    Distribuidora
                  </span>
                  <span className="text-xs font-bold text-slate-800 line-clamp-1">
                    {audit.distribuidoraNome}
                  </span>
                </div>
                <div className="p-3 bg-amber-50 rounded-xl border border-amber-200">
                  <span className="text-[10px] uppercase font-bold text-amber-800 block">
                    Nova Modalidade
                  </span>
                  <span className="text-xs font-black text-amber-950">Tarifa Horária Verde</span>
                </div>
                <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                  <span className="text-[10px] uppercase font-bold text-emerald-800 block">
                    Economia Estimada
                  </span>
                  <span className="text-xs font-black text-emerald-700">
                    {formatCurrency(audit.economiaMensal)}/mês
                  </span>
                </div>
              </div>

              {/* Informações Regulatórias */}
              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 flex items-start gap-3 text-xs text-slate-600">
                <ShieldCheck className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <span className="font-bold text-slate-800 block">
                    Direito Regulatório Assegurado (REN 1.000/2021)
                  </span>
                  <p>
                    A distribuidora não pode cobrar taxas para alteração de modalidade tarifária no
                    Grupo A, desde que a unidade atenda aos requisitos técnicos do subgrupo {audit.subgrupo}.
                  </p>
                </div>
              </div>

              {/* Pré-visualização do Documento Formal */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Minuta do Requerimento Oficial
                  </span>
                  <span className="text-[11px] text-slate-400">Pronto para envio</span>
                </div>
                <pre className="p-4 bg-slate-900 text-slate-100 rounded-xl font-mono-num text-[11px] leading-relaxed overflow-x-auto max-h-48 border border-slate-800 whitespace-pre-wrap selection:bg-amber-400 selection:text-slate-900">
                  {formalPetitionText}
                </pre>
              </div>
            </>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 sm:p-5 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={handleCopy}
              type="button"
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-colors cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-emerald-600" />
                  <span>Copiado!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 text-slate-500" />
                  <span>Copiar Minuta</span>
                </>
              )}
            </button>

            <button
              onClick={handleDownload}
              type="button"
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-colors cursor-pointer"
            >
              <Download className="w-4 h-4 text-slate-500" />
              <span>Baixar .TXT</span>
            </button>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            {!protocolSubmitted ? (
              <button
                onClick={() => setProtocolSubmitted(true)}
                type="button"
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-amber-400 hover:bg-amber-500 text-slate-950 font-bold text-xs shadow-md transition-all cursor-pointer ring-1 ring-amber-300"
              >
                Formalizar Requerimento
              </button>
            ) : (
              <button
                onClick={onClose}
                type="button"
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-md transition-all cursor-pointer"
              >
                Concluir e Fechar
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
