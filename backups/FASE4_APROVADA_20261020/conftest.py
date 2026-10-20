
import re
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Pasta principal das evidencias
PASTA_EVIDENCIAS = Path(__file__).resolve().parent / "evidencias"
PASTA_SCREENSHOTS = PASTA_EVIDENCIAS / "screenshots"


@pytest.fixture
def driver(request):
    """
    Inicializa o Chrome para cada teste.
    Captura a evidencia antes de fechar o navegador.
    """

    options = Options()
    options.add_argument("--start-maximized")

    navegador = webdriver.Chrome(options=options)

    yield navegador

    # Identifica o resultado do teste
    relatorio = getattr(request.node, "rep_call", None)

    if relatorio is None:
        status = "SEM_RESULTADO"
    elif relatorio.passed:
        status = "PASSED"
    elif relatorio.failed:
        status = "FAILED"
    else:
        status = "SKIPPED"

    # Prepara a pasta de screenshots
    PASTA_SCREENSHOTS.mkdir(
        parents=True,
        exist_ok=True
    )

    # Remove caracteres invalidos do nome
    nome_teste = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        request.node.name
    )

    data = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    arquivo = (
        PASTA_SCREENSHOTS
        / f"{nome_teste}_{status}_{data}.png"
    )

    # Captura antes de encerrar o Chrome
    try:
        navegador.save_screenshot(str(arquivo))
        print(f"\nEVIDENCIA SALVA: {arquivo}")

    except Exception as erro:
        print(f"\nERRO AO CAPTURAR EVIDENCIA: {erro}")

    finally:
        navegador.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Armazena o resultado de cada etapa do teste.
    """

    resultado = yield
    relatorio = resultado.get_result()

    setattr(
        item,
        f"rep_{relatorio.when}",
        relatorio
    )
