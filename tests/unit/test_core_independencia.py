"""Garante a regra estrutural central: core/ não depende de infraestrutura.

O core deve ser importável sem PostgreSQL, FastAPI, Streamlit, dotenv ou
qualquer dependência de infraestrutura. Verificamos isso em um subprocesso
isolado: importamos apenas `core` e confirmamos que nenhum pacote de
infraestrutura foi carregado.
"""

import subprocess
import sys

_BLOCKED = {"fastapi", "sqlalchemy", "streamlit", "psycopg", "dotenv", "pandas", "numpy", "scipy"}


def test_core_importa_sem_infra_dependencias():
    code = (
        "import sys;"
        "import core;"
        "import core.models;"
        "import core.tarifas;"
        "import core.motor_calculo;"
        "import core.otimizador;"
        "import core.epi;"
        "loaded=set(sys.modules);"
        "blocked=set(%r);"
        "deps=sorted(loaded & blocked);"
        "print('DEPS=' + ','.join(deps));"
        "sys.exit(1 if deps else 0);"
    ) % sorted(_BLOCKED)

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
    )
    out = result.stdout.strip()
    assert "DEPS=" in out, f"saída inesperada do subprocesso: {out}"
    deps = out.split("DEPS=", 1)[1]
    assert deps == "", f"`core` carregou dependência de infraestrutura: {deps}"
    assert result.returncode == 0, (
        f"importação do core falhou no subprocesso isolado: {result.stderr}"
    )
