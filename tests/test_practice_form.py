
from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.web_tables_page import WebTablesPage


from pathlib import Path

PASTA_EVIDENCIAS_CRUD = (
    Path(__file__).resolve().parent.parent
    / "evidencias"
    / "crud"
)


def salvar_evidencia(driver, nome):
    PASTA_EVIDENCIAS_CRUD.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo = PASTA_EVIDENCIAS_CRUD / f"{nome}.png"

    if not driver.save_screenshot(str(arquivo)):
        raise RuntimeError(
            f"Nao foi possivel salvar: {arquivo}"
        )

    print(f"EVIDENCIA CRUD: {arquivo}")



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

    # CREATE
    pagina.adicionar_registro(dados)

    # READ - Cadastro original
    linha = pagina.aguardar_registro(email_original)

    assert dados["nome"] in linha.text
    assert dados["sobrenome"] in linha.text
    assert email_original in linha.text
    assert "5000" in linha.text

    print("CREATE: registro criado e validado")

    # UPDATE 1 - Salario de 5000 para 6500
    pagina.editar_registro(email_original, 6500)

    linha = pagina.aguardar_registro(email_original)
    assert "6500" in linha.text

    print("UPDATE: salario alterado de 5000 para 6500")

    # UPDATE 2 - Alterar somente o email
    pagina.editar_email(email_original, email_novo)

    # READ - Validar novo email e salario preservado
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

    print(f"UPDATE: email antigo = {email_original}")
    print(f"UPDATE: email novo = {email_novo}")
    print("READ: novo email e salario 6500 validados")

    # DELETE - Excluir utilizando o novo email
    pagina.excluir_registro(email_novo)

    WebDriverWait(driver, 20).until(
        lambda d: pagina.localizar_registro(email_novo) is None
    )

    print("DELETE: registro removido com sucesso")
    print("CRUD COMPLETO: APROVADO")
