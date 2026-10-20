import os
import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class PracticeFormPage:

    URL = "https://demoqa.com/automation-practice-form"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    # Controle de velocidade da demonstracao
    def pausa(self, segundos=None):
        if segundos is None:
            segundos = float(os.getenv("DEMO_DELAY", "0"))

        if segundos > 0:
            time.sleep(segundos)

    # Abertura do formulario
    def abrir(self):
        self.driver.get(self.URL)

        self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "firstName")
            )
        )

        self.pausa()

    # Preenchimento completo
    def preencher(self, dados, arquivo):

        campos = {
            "firstName": dados["nome"],
            "lastName": dados["sobrenome"],
            "userEmail": dados["email"],
            "userNumber": dados["telefone"],
            "currentAddress": dados["endereco"],
        }

        # Preencher cada campo apenas uma vez
        for identificador, valor in campos.items():

            elemento = self.driver.find_element(
                By.ID, identificador
            )

            elemento.send_keys(valor)
            self.pausa()

        # Genero dinamico
            opcoes_genero = {
            "Male": "gender-radio-1",
            "Female": "gender-radio-2",
            "Other": "gender-radio-3",
          }

        genero = dados["genero"]

        self.driver.find_element(
          By.CSS_SELECTOR,
          f"label[for='{opcoes_genero[genero]}']"
        ).click()


        self.pausa()

        # Data de nascimento
        nascimento = self.driver.find_element(
            By.ID, "dateOfBirthInput"
        )

        nascimento.click()

        Select(
            self.driver.find_element(
                By.CLASS_NAME,
                "react-datepicker__month-select"
            )
        ).select_by_value("4")

        Select(
            self.driver.find_element(
                By.CLASS_NAME,
                "react-datepicker__year-select"
            )
        ).select_by_value("2000")

        self.driver.find_element(
            By.CSS_SELECTOR,
            ".react-datepicker__day--015:not(.react-datepicker__day--outside-month)"
        ).click()

        self.pausa()

        # Materia
        materias = self.driver.find_element(
            By.ID, "subjectsInput"
        )

        materias.send_keys("Maths")
        materias.send_keys(Keys.ENTER)

        self.pausa()

        # Hobby
        self.driver.find_element(
            By.CSS_SELECTOR,
            "label[for='hobbies-checkbox-1']"
        ).click()

        self.pausa()

        # Upload do arquivo TXT
        caminho = Path(arquivo).resolve()

        if not caminho.is_file():
            raise FileNotFoundError(
                f"Arquivo nao encontrado: {caminho}"
            )

        self.driver.find_element(
            By.ID, "uploadPicture"
        ).send_keys(str(caminho))

        self.pausa()

        # Estado
        estado = self.driver.find_element(
            By.ID, "state"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            estado
        )

        estado.click()

        self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[text()='NCR']")
            )
        ).click()

        self.pausa()

        # Cidade
        self.driver.find_element(
            By.ID, "city"
        ).click()

        self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[text()='Delhi']")
            )
        ).click()

        self.pausa()

    # Enviar formulario
    def enviar(self):

        botao = self.driver.find_element(
            By.ID, "submit"
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            botao
        )

        self.pausa()

        botao.click()

    # Validar resultados do popup
    def obter_resultados(self):

        self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "example-modal-sizes-title-lg")
            )
        )

        self.pausa(3 if float(
            os.getenv("DEMO_DELAY", "0")
        ) > 0 else 0)

        linhas = self.driver.find_elements(
            By.CSS_SELECTOR,
            ".table-responsive tbody tr"
        )

        resultados = {}

        for linha in linhas:

            colunas = linha.find_elements(
                By.TAG_NAME, "td"
            )

            if len(colunas) == 2:
                resultados[colunas[0].text] = colunas[1].text

        return resultados

    # Fechar popup
    def fechar_popup(self):

        botao = self.wait.until(
            EC.presence_of_element_located(
                (By.ID, "closeLargeModal")
            )
        )

        self.pausa()

        self.driver.execute_script(
            "arguments[0].click();",
            botao
        )