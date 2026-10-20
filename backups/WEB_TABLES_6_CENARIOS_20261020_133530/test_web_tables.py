
from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.web_tables_page import WebTablesPage


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

    pagina.abrir()

    # CREATE
    pagina.adicionar_registro(dados)

    # Filtrar pelo email do registro criado
    
    linha = pagina.aguardar_registro(dados["email"])

    assert dados["nome"] in linha.text
    assert dados["sobrenome"] in linha.text
    assert dados["email"] in linha.text
    assert "5000" in linha.text

    print("CREATE: registro criado e validado")

    # UPDATE
    pagina.editar_registro(dados["email"], 6500)

    linha = pagina.aguardar_registro(dados["email"])

    assert "6500" in linha.text

    print("UPDATE: salario alterado para 6500")

    # DELETE
    pagina.excluir_registro(dados["email"])

    WebDriverWait(driver, 20).until(
        lambda d:
        pagina.localizar_registro(dados["email"]) is None
    )

    print("DELETE: registro removido com sucesso")
