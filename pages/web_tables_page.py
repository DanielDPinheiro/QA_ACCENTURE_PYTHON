import os
import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WebTablesPage:
    URL = "https://demoqa.com/webtables"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def pausa(self):
        segundos = float(os.getenv("DEMO_DELAY", "0"))
        if segundos > 0:
            time.sleep(segundos)

    def abrir(self):
        self.driver.get(self.URL)
        self.wait.until(EC.element_to_be_clickable((By.ID, "addNewRecordButton")))
        self.pausa()

    def pesquisar_registro(self, email):
        campo = self.wait.until(EC.element_to_be_clickable((By.ID, "searchBox")))
        campo.clear()
        campo.send_keys(email)
        self.pausa()

    def localizar_registro(self, email):
        # Encontra a linha pelo botao de edicao e pelo texto da celula de email.
        # Nao depende das classes .rt-tr-group, que podem mudar.
        return self.driver.execute_script("""
            const esperado = arguments[0].replace(/\\s+/g, '').toLowerCase();
            const botoes = document.querySelectorAll('[id^="edit-record-"]');
            for (const botao of botoes) {
                let no = botao.parentElement;
                while (no && no !== document.body) {
                    const celulas = no.querySelectorAll('.rt-td, [role="gridcell"], td');
                    if (celulas.length >= 6 &&
                        no.querySelector('[id^="delete-record-"]')) {
                        const encontrado = (celulas[3].textContent || '')
                            .replace(/\\s+/g, '').toLowerCase();
                        if (encontrado === esperado) return no;
                        break;
                    }
                    no = no.parentElement;
                }
            }
            return null;
        """, email)

    def _diagnostico(self, email):
        print(f"DIAGNOSTICO: email esperado={email!r}")
        print("URL:", self.driver.current_url)
        print("Botoes editar:", len(self.driver.find_elements(By.CSS_SELECTOR, '[id^="edit-record-"]')))
        print("Celulas .rt-td:", len(self.driver.find_elements(By.CSS_SELECTOR, '.rt-td')))
        print("Linhas .rt-tr-group:", len(self.driver.find_elements(By.CSS_SELECTOR, '.rt-tr-group')))
        print("Linhas tr:", len(self.driver.find_elements(By.CSS_SELECTOR, 'tr')))
        print("HTML da tabela:", self.driver.execute_script("""
            const el = document.querySelector('.rt-table, table, [role="table"], [role="grid"]');
            return el ? el.outerHTML.slice(0, 5000) : 'Tabela nao encontrada';
        """))

    def aguardar_registro(self, email):
        self.pesquisar_registro(email)
        try:
            return self.wait.until(
                lambda _: self.localizar_registro(email),
                message=f"Registro nao encontrado: {email}",
            )
        except TimeoutException:
            self._diagnostico(email)
            raise

    def preencher_campos(self, dados):
        campos = {
            "firstName": dados["nome"],
            "lastName": dados["sobrenome"],
            "userEmail": dados["email"],
            "age": str(dados["idade"]),
            "salary": str(dados["salario"]),
            "department": dados["departamento"],
        }
        for id_campo, valor in campos.items():
            elemento = self.wait.until(EC.visibility_of_element_located((By.ID, id_campo)))
            elemento.clear()
            elemento.send_keys(valor)
            self.pausa()

    def adicionar_registro(self, dados):
        self.wait.until(EC.element_to_be_clickable((By.ID, "addNewRecordButton"))).click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "registration-form-modal")))
        self.pausa()
        self.preencher_campos(dados)
        self.wait.until(EC.element_to_be_clickable((By.ID, "submit"))).click()
        self.wait.until(EC.invisibility_of_element_located((By.ID, "registration-form-modal")))
        linha = self.aguardar_registro(dados["email"])
        print(f"CREATE OK: {dados['email']}")
        self.pausa()
        return linha

    def editar_registro(self, email, novo_salario):
        linha = self.aguardar_registro(email)
        linha.find_element(By.CSS_SELECTOR, '[id^="edit-record-"]').click()
        salario = self.wait.until(EC.visibility_of_element_located((By.ID, "salary")))
        salario.clear()
        salario.send_keys(str(novo_salario))
        self.pausa()
        self.wait.until(EC.element_to_be_clickable((By.ID, "submit"))).click()
        self.wait.until(EC.invisibility_of_element_located((By.ID, "registration-form-modal")))

        def atualizado(_):
            registro = self.localizar_registro(email)
            if registro is None:
                return False
            celulas = registro.find_elements(By.CSS_SELECTOR, '.rt-td, [role="gridcell"], td')
            return len(celulas) >= 6 and celulas[4].get_attribute('textContent').strip() == str(novo_salario)

        self.wait.until(atualizado, message=f"Salario nao atualizado: {email}")
        print(f"UPDATE OK: {email} -> {novo_salario}")
        self.pausa()

    
    def editar_salario_e_email(self, email_atual, novo_salario, novo_email):
        """
        Atualiza salario e email de um registro existente.
        Confirma as duas alteracoes na tabela.
        """

        if email_atual == novo_email:
            raise ValueError("O novo email deve ser diferente do atual")

        # Localiza o registro original
        linha = self.aguardar_registro(email_atual)

        # Abre o formulario de edicao
        linha.find_element(
            By.CSS_SELECTOR,
            '[id^="edit-record-"]'
        ).click()

        self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "registration-form-modal")
            )
        )

        # Atualiza salario
        campo_salario = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "salary")
            )
        )
        campo_salario.clear()
        campo_salario.send_keys(str(novo_salario))
        self.pausa()

        # Atualiza email
        campo_email = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "userEmail")
            )
        )
        campo_email.clear()
        campo_email.send_keys(novo_email)
        self.pausa()

        # Salva as alteracoes
        self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, "submit")
            )
        ).click()

        self.wait.until(
            EC.invisibility_of_element_located(
                (By.ID, "registration-form-modal")
            )
        )

        # A busca anterior pode estar filtrando pelo email antigo
        linha_atualizada = self.aguardar_registro(novo_email)

        def validar_atualizacao(_):
            registro = self.localizar_registro(novo_email)

            if registro is None:
                return False

            celulas = registro.find_elements(
                By.CSS_SELECTOR,
                '.rt-td, [role="gridcell"], td'
            )

            if len(celulas) < 6:
                return False

            email_tabela = celulas[3].text.strip()
            salario_tabela = celulas[4].text.strip()

            return (
                email_tabela == novo_email
                and salario_tabela == str(novo_salario)
            )

        self.wait.until(
            validar_atualizacao,
            message="Email ou salario nao atualizado"
        )

        print(
            f"UPDATE OK: {email_atual} -> {novo_email}"
        )
        print(
            f"UPDATE OK: salario -> {novo_salario}"
        )

        self.pausa()

        return linha_atualizada

    
    def editar_email(self, email_atual, novo_email):
        """Altera apenas o email e valida o novo valor."""

        linha = self.aguardar_registro(email_atual)

        linha.find_element(
            By.CSS_SELECTOR,
            '[id^="edit-record-"]'
        ).click()

        campo_email = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "userEmail")
            )
        )

        campo_email.clear()
        campo_email.send_keys(novo_email)
        self.pausa()

        self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, "submit")
            )
        ).click()

        self.wait.until(
            EC.invisibility_of_element_located(
                (By.ID, "registration-form-modal")
            )
        )

        # A busca precisa utilizar o novo email
        linha_atualizada = self.aguardar_registro(novo_email)

        celulas = linha_atualizada.find_elements(
            By.CSS_SELECTOR,
            ".rt-td, [role='gridcell'], td"
        )

        assert celulas[3].text.strip() == novo_email

        print(
            f"EMAIL ATUALIZADO: {email_atual} -> {novo_email}"
        )

        self.pausa()
    
    

    def excluir_registro(self, email):
        linha = self.aguardar_registro(email)
        linha.find_element(By.CSS_SELECTOR, '[id^="delete-record-"]').click()
        self.wait.until(lambda _: self.localizar_registro(email) is None,
                        message=f"Registro nao excluido: {email}")
        print(f"DELETE OK: {email}")
        self.pausa()
