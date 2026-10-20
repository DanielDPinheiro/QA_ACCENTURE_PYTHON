
import base64
import re
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_EVIDENCIAS = PASTA_PROJETO / "evidencias"
PASTA_SCREENSHOTS = PASTA_EVIDENCIAS / "screenshots"


@pytest.fixture
def driver():
    """
    Inicializa e encerra o navegador para cada teste.
    """

    options = Options()
    options.add_argument("--start-maximized")

    navegador = webdriver.Chrome(options=options)

    yield navegador

    navegador.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Captura o screenshot no final da execucao do teste
    e incorpora a imagem ao relatorio pytest-html.
    """

    resultado = yield
    relatorio = resultado.get_result()

    setattr(
        item,
        f"rep_{relatorio.when}",
        relatorio
    )

    # Captura somente apos a etapa principal do teste
    if relatorio.when != "call":
        return

    navegador = item.funcargs.get("driver")

    if navegador is None:
        return

    status = (
        "PASSED"
        if relatorio.passed
        else "FAILED"
        if relatorio.failed
        else "SKIPPED"
    )

    PASTA_SCREENSHOTS.mkdir(
        parents=True,
        exist_ok=True
    )

    nome_teste = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        item.name
    )

    data = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    arquivo = (
        PASTA_SCREENSHOTS
        / f"{nome_teste}_{status}_{data}.png"
    )

    try:
        # Captura antes do teardown do navegador
        imagem = navegador.get_screenshot_as_png()

        arquivo.write_bytes(imagem)

        print(f"\nEVIDENCIA SALVA: {arquivo}")

        # Integra ao pytest-html, se estiver instalado
        plugin_html = item.config.pluginmanager.getplugin(
            "html"
        )

        if plugin_html is not None:
            imagem_base64 = base64.b64encode(
                imagem
            ).decode("ascii")

            extras = list(
                getattr(relatorio, "extras", [])
            )

            extras.append(
                plugin_html.extras.image(
                    imagem_base64,
                    mime_type="image/png",
                    extension="png",
                    name=f"Evidencia - {status}"
                )
            )

            relatorio.extras = extras

            print(
                "EVIDENCIA INCORPORADA AO HTML"
            )

    except Exception as erro:
        print(
            f"\nERRO NA CAPTURA DE EVIDENCIA: {erro}"
        )
