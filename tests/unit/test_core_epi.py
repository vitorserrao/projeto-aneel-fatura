"""Testes do Preço de Indiferença (PI) — docs/epi.md.

Cobre os três casos do enunciado, as validações de entrada e a agregação de
vários meses (somar componentes antes de dividir, sem média de PIs mensais).
"""

import pytest

from core.epi import calcular_pi, calcular_pi_meses

# PIS + COFINS = 0,0374 (a fórmula usa apenas a soma).
PIS = 0.0065
COFINS = 0.0309
ICMS = 0.17


def _args_base(**overrides):
    args = dict(
        e_ponta=30.0,
        e_fora_ponta=220.0,
        te_ponta=450.0,
        te_fora_ponta=280.0,
        pis=PIS,
        cofins=COFINS,
        icms=ICMS,
        k=0.03,
    )
    args.update(overrides)
    return args


def test_caso_1_sem_opex_capex():
    r = calcular_pi(**_args_base())

    assert r.pi == pytest.approx(302.98, abs=0.01)
    assert r.e == pytest.approx(250.0)
    assert r.c_te == pytest.approx(30 * 450 + 220 * 280)  # 75.100
    assert r.custos_acl == pytest.approx(0.0)
    assert r.aviso is None


def test_caso_2_com_opex_capex():
    r = calcular_pi(**_args_base(opex_mensal=1000.0, capex=20000.0, horizonte_meses=60))

    assert r.pi == pytest.approx(298.68, abs=0.01)
    assert r.custos_acl == pytest.approx(1000.0 + 20000.0 / 60.0)


def test_caso_3_omitir_opex_capex_equivale_a_zero():
    omitidos = calcular_pi(**_args_base())
    explicitos = calcular_pi(**_args_base(opex_mensal=0.0, capex=0.0))

    assert omitidos.pi == pytest.approx(explicitos.pi)
    assert omitidos.custos_acl == explicitos.custos_acl == 0.0


def test_componentes_batem_com_a_formula():
    r = calcular_pi(**_args_base(opex_mensal=1000.0, capex=20000.0))

    assert r.c_e_acr == pytest.approx(
        (r.c_te + r.e * 0.0) / ((1 - PIS - COFINS) * (1 - ICMS))
    )
    assert r.base_acl == pytest.approx(r.e * (1 + 0.03) / (1 - ICMS))
    assert r.pi == pytest.approx((r.c_e_acr - r.custos_acl) / r.base_acl)


# ---------------------------------------------------------------------------
# Validações
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("pis", -0.01),
        ("pis", 1.0),
        ("cofins", 1.5),
        ("icms", 1.0),
    ],
)
def test_aliquota_fora_do_intervalo_levanta(campo, valor):
    with pytest.raises(ValueError):
        calcular_pi(**_args_base(**{campo: valor}))


def test_pis_mais_cofins_nao_pode_zerar_denominador():
    with pytest.raises(ValueError):
        calcular_pi(**_args_base(pis=0.6, cofins=0.4))


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("e_ponta", -1.0),
        ("e_fora_ponta", -0.1),
        ("te_ponta", -1.0),
        ("bandeira", -1.0),
        ("encargos", -1.0),
        ("k", -0.01),
        ("opex_mensal", -1.0),
        ("capex", -1.0),
    ],
)
def test_valores_negativos_levantam(campo, valor):
    with pytest.raises(ValueError):
        calcular_pi(**_args_base(**{campo: valor}))


def test_consumo_total_zero_levanta():
    with pytest.raises(ValueError):
        calcular_pi(**_args_base(e_ponta=0.0, e_fora_ponta=0.0))


@pytest.mark.parametrize("horizonte", [0, -12, 1.5])
def test_horizonte_invalido_levanta(horizonte):
    with pytest.raises(ValueError):
        calcular_pi(**_args_base(horizonte_meses=horizonte))


def test_pi_negativo_gera_aviso():
    r = calcular_pi(**_args_base(opex_mensal=1_000_000.0))

    assert r.pi <= 0
    assert r.aviso


# ---------------------------------------------------------------------------
# Encargos (ESS) — lado ACL
# ---------------------------------------------------------------------------


def test_encargos_entram_no_lado_acl_e_reduzem_o_pi():
    sem = calcular_pi(**_args_base())
    com = calcular_pi(**_args_base(encargos=3.0))

    # ES = E·(1+k)·encargos entra no numerador (custo do ACL), não na TE.
    assert com.custos_acl == pytest.approx(com.e * (1 + 0.03) * 3.0)
    # Redução no PI = encargos·(1 − ICMS), pela divisão por E·(1+k)/(1−ICMS).
    assert com.pi == pytest.approx(sem.pi - 3.0 * (1 - ICMS))


# ---------------------------------------------------------------------------
# Vários meses
# ---------------------------------------------------------------------------


def test_varios_meses_soma_componentes_antes_de_dividir():
    meses = [
        {"e_ponta": 30.0, "e_fora_ponta": 220.0, "te_ponta": 450.0, "te_fora_ponta": 280.0},
        {
            "e_ponta": 10.0,
            "e_fora_ponta": 100.0,
            "te_ponta": 400.0,
            "te_fora_ponta": 250.0,
            "bandeira": 5.0,
        },
    ]

    r = calcular_pi_meses(
        meses,
        pis=PIS,
        cofins=COFINS,
        icms=ICMS,
        k=0.03,
        opex_mensal=1000.0,
        capex=20000.0,
    )

    m1 = calcular_pi(**_args_base(opex_mensal=1000.0, capex=20000.0))
    m2 = calcular_pi(
        **_args_base(
            e_ponta=10.0,
            e_fora_ponta=100.0,
            te_ponta=400.0,
            te_fora_ponta=250.0,
            bandeira=5.0,
            opex_mensal=1000.0,
            capex=20000.0,
        )
    )
    esperado = (m1.c_e_acr + m2.c_e_acr - (m1.custos_acl + m2.custos_acl)) / (
        m1.base_acl + m2.base_acl
    )

    assert r.pi == pytest.approx(esperado)
    assert r.meses == 2
    assert r.e == pytest.approx(m1.e + m2.e)


def test_meses_iguais_dao_mesmo_pi_que_um_mes():
    mes = {"e_ponta": 30.0, "e_fora_ponta": 220.0, "te_ponta": 450.0, "te_fora_ponta": 280.0}
    r = calcular_pi_meses([mes, mes], pis=PIS, cofins=COFINS, icms=ICMS, k=0.03)

    assert r.pi == pytest.approx(calcular_pi(**_args_base()).pi)
    assert r.meses == 2


def test_meses_vazio_levanta():
    with pytest.raises(ValueError):
        calcular_pi_meses([], pis=PIS, cofins=COFINS, icms=ICMS)


# ---------------------------------------------------------------------------
# Caso TCC — CELESC A4 Azul, dez/2025 (validação contra Lemos, 2025)
# ---------------------------------------------------------------------------


def test_caso_tcc_celesc_dez2025():
    """Reproduz o PI = 302,20 do TCC com a TE do ciclo anterior ao reajuste.

    O TCC usa a TE por posto da CELESC A4 Azul com acessante/detalhe
    "Não se aplica". A vigência 2024-08-22..2025-08-21 (TE ponta 456,91 /
    fora ponta 286,47) reproduz exatamente o resultado do TCC — a vigência
    2025-08-22..2025-12-31 (483,63 / 301,23) daria 318,20.
    """
    r = calcular_pi(
        e_ponta=1425.83,
        e_fora_ponta=14125.16,
        te_ponta=456.91,
        te_fora_ponta=286.47,
        pis=0.0067,
        cofins=0.0307,
        icms=0.17,
        encargos=3.0,
        k=0.03,
        horizonte_meses=60,
    )

    assert r.pi == pytest.approx(302.20, abs=0.01)
    assert r.custos_acl == pytest.approx(r.e * (1 + 0.03) * 3.0)
