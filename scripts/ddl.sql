-- DDL inicial do projeto ACR x ACL (Sprint 2 — estrutura aprovada).
--
-- Estrutura aprovada (dec-2c889ec2080b7b85):
--   * CNPJ como identidade da distribuidora;
--   * as duas bases (Tarifa de Aplicação / Base Econômica) em dsc_base_tarifaria;
--   * TE/TUSD como componentes em linhas (tabela tarifa_aplicacao_componente);
--   * acessante como dimensão separada.
--
-- Este arquivo é a fonte declarativa do schema. Idempotente: usa
-- CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS.
-- NÃO contém regra regulatória nem dados ANEEL.

BEGIN;

CREATE TABLE IF NOT EXISTS distribuidora (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    num_cnpj      VARCHAR(18)  NOT NULL UNIQUE,
    sig_agente    VARCHAR(60)  NOT NULL,
    criada_em     TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT ck_distribuidora_cnpj_nao_vazio CHECK (num_cnpj <> '')
);

CREATE TABLE IF NOT EXISTS acessante (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sig_acessante  VARCHAR(120) NOT NULL UNIQUE,
    CONSTRAINT ck_acessante_sig_nao_vazio CHECK (sig_acessante <> '')
);

CREATE TABLE IF NOT EXISTS carga_aneel (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem          TEXT         NOT NULL,
    sha256_arquivo          VARCHAR(64)  NOT NULL UNIQUE,
    dat_geracao_conjunto    DATE         NULL,
    data_carga              TIMESTAMPTZ  NOT NULL DEFAULT now(),
    num_registros           INTEGER      NULL,
    observacoes             TEXT         NULL,
    CONSTRAINT ck_carga_arquivo_nao_vazio CHECK (arquivo_origem <> '')
);

CREATE TABLE IF NOT EXISTS tarifa_aplicacao_componente (
    id                        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    carga_id                  BIGINT  NOT NULL REFERENCES carga_aneel(id) ON DELETE RESTRICT,
    distribuidora_id          INTEGER NOT NULL REFERENCES distribuidora(id) ON DELETE RESTRICT,
    acessante_id              INTEGER NULL REFERENCES acessante(id) ON DELETE RESTRICT,

    dsc_reh                   TEXT NULL,
    dat_inicio_vigencia       DATE   NOT NULL,
    dat_fim_vigencia          DATE   NOT NULL,
    dsc_base_tarifaria        VARCHAR(40)  NOT NULL,
    dsc_sub_grupo             VARCHAR(20)  NOT NULL,
    dsc_modalidade_tarifaria  VARCHAR(60)  NOT NULL,
    dsc_classe                VARCHAR(60)  NOT NULL,
    dsc_sub_classe            VARCHAR(120) NOT NULL,
    dsc_detalhe               VARCHAR(60)  NOT NULL,
    nom_posto_tarifario       VARCHAR(60)  NOT NULL,
    dsc_unidade_terciaria     VARCHAR(10)  NOT NULL,

    componente                VARCHAR(4)   NOT NULL,
    valor                     NUMERIC(14,6) NOT NULL,

    linha_origem              INTEGER NOT NULL,
    hash_linha                VARCHAR(64) NOT NULL,
    criado_em                 TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_tarifa_carga_linha_componente UNIQUE (carga_id, linha_origem, componente),
    CONSTRAINT ck_tarifa_componente_valido CHECK (componente IN ('TE', 'TUSD')),
    CONSTRAINT ck_tarifa_valor_nao_nulo CHECK (valor IS NOT NULL),
    CONSTRAINT ck_tarifa_vigencia_valida CHECK (dat_inicio_vigencia <= dat_fim_vigencia)
);

-- Índices para as consultas reais do sistema.
CREATE INDEX IF NOT EXISTS ix_tarifa_distribuidora ON tarifa_aplicacao_componente (distribuidora_id);
CREATE INDEX IF NOT EXISTS ix_tarifa_carga ON tarifa_aplicacao_componente (carga_id);
CREATE INDEX IF NOT EXISTS ix_tarifa_acessante ON tarifa_aplicacao_componente (acessante_id);
CREATE INDEX IF NOT EXISTS ix_tarifa_consulta ON tarifa_aplicacao_componente
    (distribuidora_id, dsc_sub_grupo, dsc_modalidade_tarifaria, dsc_classe,
     dsc_sub_classe, nom_posto_tarifario, componente,
     dat_inicio_vigencia, dat_fim_vigencia);
CREATE INDEX IF NOT EXISTS ix_tarifa_vigencia ON tarifa_aplicacao_componente
    (dat_inicio_vigencia, dat_fim_vigencia);

COMMIT;
