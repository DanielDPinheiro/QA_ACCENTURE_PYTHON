
import random
from pathlib import Path

from faker import Faker
from pages.practice_form_page import PracticeFormPage


def normalizar_texto(texto):
    return " ".join(texto.split())


def test_cadastro_completo(driver):
    fake = Faker("pt_BR")

    # Gerar nome de acordo com o genero
    genero = random.choice(["Male", "Female"])

    if genero == "Male":
        nome = fake.first_name_male()
    else:
        nome = fake.first_name_female()

    # Massa de dados
    dados = {
        "nome": nome,
        "sobrenome": fake.last_name(),
        "email": fake.user_name() + "@teste.com",
        "telefone": "1198765432",
        "endereco": fake.address(),
        "genero": genero,
    }

    # Criar arquivo TXT para upload
    arquivo = Path("fixtures/arquivo_teste.txt")
    arquivo.parent.mkdir(parents=True, exist_ok=True)

    arquivo.write_text(
        "Arquivo de teste QA Accenture - Selenium Python",
        encoding="utf-8"
    )

    # Inicializar Page Object
    pagina = PracticeFormPage(driver)

    # Executar fluxo de cadastro
    pagina.abrir()
    pagina.preencher(dados, arquivo)
    pagina.enviar()

    # Obter dados do popup
    resultados = pagina.obter_resultados()

    # Validar nome completo
    assert resultados["Student Name"] == (
        f"{dados['nome']} {dados['sobrenome']}"
    )

    # Validar email e genero
    assert resultados["Student Email"] == dados["email"]
    assert resultados["Gender"] == dados["genero"]

    # Validar telefone
    assert resultados["Mobile"] == dados["telefone"]

    # Validar data de nascimento
    assert resultados["Date of Birth"] == "15 May,2000"

    # Validar materia e hobby
    assert resultados["Subjects"] == "Maths"
    assert resultados["Hobbies"] == "Sports"

    # Validar arquivo enviado
    assert resultados["Picture"] == arquivo.name

    # Validar endereco ignorando quebras de linha
    assert normalizar_texto(
        resultados["Address"]
    ) == normalizar_texto(
        dados["endereco"]
    )

    # Validar estado e cidade
    assert resultados["State and City"] == "NCR Delhi"

    # Fechar popup
    pagina.fechar_popup()
