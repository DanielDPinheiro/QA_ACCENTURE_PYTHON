
from pathlib import Path

from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.web_tables_page import WebTablesPage


PASTA_CRUD = (
    Path(__file__).resolve().parent.parent
    / "evidencias"
    / "crud"
)


def salvar_evidencia(driver, nome):
    PASTA_CRUD.mkdir(parents=True, exist_ok=True)

    arquivo = PASTA_CRUD / f"{nome}.png"

    if not driver.save_screenshot(str(arquivo)):
        raise RuntimeError(
            f"Falha ao salvar evidencia: {arquivo}"
        )

    print(f"EVIDENCIA CRUD SALVA: {arquivo}")


def test_crud_web_tables(driver):
    fake = Faker("pt_BR")
    pagina = WebTablesPage(driver)

    dados = {
        "nome": fake.first_name(),
        "sobrenome": fake.last_name(),
        "email": fake.unique.email(),
        "idade": 30,
        "salario": 5000,
        "departamento": "Quality Assurance",
    }

    email_original = dados["email"]
    email_novo = fake.unique.email()

    assert email_novo != email_original

    pagina.abrir()

    # CREATE - Cadastrar registro
    pagina.adicionar_registro(dados)

    # READ - Validar dados originais
    linha = pagina.aguardar_registro(email_original)

    assert dados["nome"] in linha.text
    assert dados["sobrenome"] in linha.text
    assert email_original in linha.text
    assert "5000" in linha.text

    print("CREATE: registro criado e validado")
    print(f"EMAIL ORIGINAL: {email_original}")
    print("SALARIO ORIGINAL: 5000")

    salvar_evidencia(driver, "01_cadastro_original")

    # UPDATE - Alterar salario
    pagina.editar_registro(email_original, 6500)

    linha = pagina.aguardar_registro(email_original)

    assert "6500" in linha.text

    print("UPDATE: salario alterado de 5000 para 6500")

    salvar_evidencia(driver, "02_salario_atualizado")

    # UPDATE - Alterar email
    pagina.editar_email(email_original, email_novo)

    # READ - Validar dados atualizados
    linha = pagina.aguardar_registro(email_novo)

    celulas = linha.find_elements(
        By.CSS_SELECTOR,
        ".rt-td, [role='gridcell'], td"
    )

    assert len(celulas) >= 6

    assert celulas[0].text.strip() == dados["nome"]
    assert celulas[1].text.strip() == dados["sobrenome"]
    assert celulas[2].text.strip() == "30"
    assert celulas[3].text.strip() == email_novo
    assert celulas[4].text.strip() == "6500"
    assert celulas[5].text.strip() == dados["departamento"]

    print(f"UPDATE EMAIL: {email_original} -> {email_novo}")
    print("READ: email e salario atualizados confirmados")

    salvar_evidencia(driver, "03_email_atualizado")

    # DELETE - Excluir pelo novo email
    pagina.excluir_registro(email_novo)

    WebDriverWait(driver, 20).until(
        lambda d: pagina.localizar_registro(email_novo) is None
    )

    print(f"DELETE: registro {email_novo} removido")

    salvar_evidencia(driver, "04_registro_excluido")

    print("CRUD COMPLETO: APROVADO")
