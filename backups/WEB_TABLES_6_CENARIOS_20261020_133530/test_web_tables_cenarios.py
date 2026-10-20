
import pytest
from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.web_tables_page import WebTablesPage


@pytest.fixture
def contexto(driver):
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
    return pagina, dados


def test_ct01_cadastrar_registro(contexto):
    pagina, dados = contexto

    pagina.adicionar_registro(dados)

    linha = pagina.aguardar_registro(dados["email"])

    assert linha is not None
    assert dados["email"] in linha.text

    print("CT-01 PASSED: cadastro validado")


def test_ct02_pesquisar_registro(contexto):
    pagina, dados = contexto

    pagina.adicionar_registro(dados)

    linha = pagina.aguardar_registro(dados["email"])

    assert linha is not None
    assert dados["nome"] in linha.text

    print("CT-02 PASSED: pesquisa validada")



def test_ct03_editar_salario(contexto):
    pagina, dados = contexto

    pagina.adicionar_registro(dados)
    pagina.editar_registro(dados["email"], 6500)

    # Consulta novamente o registro atualizado
    pagina.pesquisar_registro(dados["email"])

    def salario_confirmado(driver):
        linha = pagina.localizar_registro(dados["email"])

        if linha is None:
            return False

        texto = " ".join(linha.text.split())

        return (
            dados["email"] in texto
            and "6500" in texto
        )

    pagina.wait.until(
        salario_confirmado,
        message="Salario atualizado nao encontrado"
    )

    print("CT-03 PASSED: salario atualizado para 6500")



def test_ct04_excluir_registro(contexto):
    pagina, dados = contexto

    pagina.adicionar_registro(dados)
    pagina.excluir_registro(dados["email"])

    assert pagina.localizar_registro(dados["email"]) is None

    print("CT-04 PASSED: exclusao validada")


def test_ct05_campos_obrigatorios(contexto):
    pagina, _ = contexto

    pagina.wait.until(
        EC.element_to_be_clickable(
            (By.ID, "addNewRecordButton")
        )
    ).click()

    pagina.wait.until(
        EC.element_to_be_clickable((By.ID, "submit"))
    ).click()

    formulario = pagina.driver.find_element(
        By.ID, "userForm"
    )

    assert formulario.get_attribute("class").find(
        "was-validated"
    ) != -1

    print("CT-05 PASSED: campos obrigatorios validados")




def test_ct06_email_invalido(contexto):
    pagina, dados = contexto

    dados["email"] = "email-invalido"

    pagina.wait.until(
        EC.element_to_be_clickable(
            (By.ID, "addNewRecordButton")
        )
    ).click()

    pagina.preencher_campos(dados)

    pagina.wait.until(
        EC.element_to_be_clickable(
            (By.ID, "submit")
        )
    ).click()

    campo_email = pagina.wait.until(
        EC.visibility_of_element_located(
            (By.ID, "userEmail")
        )
    )

    validacao = pagina.driver.execute_script(
        """
        const campo = arguments[0];

        return {
            valor: campo.value,
            tipo: campo.type,
            pattern: campo.pattern,
            valido: campo.validity.valid,
            typeMismatch: campo.validity.typeMismatch,
            patternMismatch: campo.validity.patternMismatch
        };
        """,
        campo_email
    )

    print(f"DIAGNOSTICO CT-06: {validacao}")

    formulario_aberto = pagina.driver.find_element(
        By.ID, "registration-form-modal"
    ).is_displayed()

    assert validacao["valor"] == "email-invalido"

    assert validacao["valido"] is False, (
        "O campo aceitou um email invalido"
    )

    assert formulario_aberto is True, (
        "O formulario foi fechado inesperadamente"
    )

    # Evidencia visual do teste
    from pathlib import Path

    pasta = Path("evidencias")
    pasta.mkdir(parents=True, exist_ok=True)

    pagina.driver.save_screenshot(
        str(pasta / "CT06_email_invalido.png")
    )

    print("CT-06 PASSED: email invalido rejeitado")
    print("Evidencia salva: evidencias/CT06_email_invalido.png")
