
import json
import numpy as np
from pyscript import document, fetch
from html import escape
from math import isfinite

eventos = 0


def registrar_evento(mensagem):
    global eventos

    eventos += 1

    document.getElementById(
        "telemetria-status"
    ).innerText = mensagem

    document.getElementById(
        "telemetria-eventos"
    ).innerText = f"Eventos registrados: {eventos}"


def validar_fruta(fruta):

    campos_obrigatorios = [
        "id", "nome", "preco", "estoque",
        "unidade", "calorias", "vetor"
    ]

    for campo in campos_obrigatorios:
        if campo not in fruta:
            return False

    if not isinstance(fruta["nome"], str):
        return False

    if not fruta["nome"].strip():
        return False

    if not isinstance(fruta["preco"], (int, float)):
        return False

    if not isfinite(fruta["preco"]) or fruta["preco"] < 0:
        return False

    if not isinstance(fruta["estoque"], int):
        return False

    if fruta["estoque"] < 0:
        return False

    if not isinstance(fruta["calorias"], (int, float)):
        return False

    if not isfinite(fruta["calorias"]) or fruta["calorias"] < 0:
        return False

    vetor = fruta["vetor"]

    if not isinstance(vetor, list) or len(vetor) != 3:
        return False

    for valor in vetor:
        if not isinstance(valor, (int, float)):
            return False

        if not isfinite(valor) or valor < 0:
            return False

    return True


def calcular_norma(vetor):

    vetor_numpy = np.array(vetor, dtype=float)

    norma = np.linalg.norm(vetor_numpy)

    return norma


def exibir_frutas(frutas):

    lista = document.getElementById("lista-frutas")

    conteudo = ""

    for fruta in frutas:

        nome = escape(fruta["nome"])
        unidade = escape(fruta["unidade"])

        imagem = {
            "Maçã": "maca.jpg",
            "Banana": "banana.jpg",
            "Laranja": "laranja.jpg",
            "Morango": "morango.jpg",
            "Uva": "uva.jpg"
        }.get(fruta["nome"], "")

        if imagem:
            elemento_imagem = f"""
                <img
                    src="src/assets/{imagem}"
                    alt="{nome}"
                    onerror="this.style.display='none'"
                >
            """
        else:
            elemento_imagem = ""

        conteudo += f"""
            <article class="fruta-card">

                {elemento_imagem}

                <h3>{nome}</h3>

                <p class="preco">
                    R$ {fruta["preco"]:.2f}
                </p>

                <p>
                    Estoque: {fruta["estoque"]} {unidade}
                </p>

                <p>
                    Calorias: {fruta["calorias"]} kcal
                </p>

            </article>
        """

    lista.innerHTML = conteudo

def atualizar_indicadores(frutas):

    total_produtos = len(frutas)

    total_estoque = sum(
        fruta["estoque"] for fruta in frutas
    )

    document.getElementById(
        "total-produtos"
    ).innerText = str(total_produtos)

    document.getElementById(
        "total-estoque"
    ).innerText = str(total_estoque)

    document.getElementById(
        "status-sistema"
    ).innerText = "Online"

def processar_vetores(frutas):

    resultados = []

    for fruta in frutas:

        norma = calcular_norma(fruta["vetor"])

        resultados.append(
            f'{fruta["nome"]}: norma euclidiana = {norma:.2f}'
        )

    document.getElementById(
        "resultado-vetorial"
    ).innerText = " | ".join(resultados)


async def iniciar_sistema():

    registrar_evento("Iniciando sistema...")

    try:
        resposta = await fetch("src/python/dados.json")

        if not resposta.ok:
            raise Exception(
                f"Falha ao carregar dados.json. "
                f"Status HTTP: {resposta.status}"
            )

        conteudo = await resposta.text()

        try:
            dados = json.loads(conteudo)
        except json.JSONDecodeError:
            raise ValueError(
                "O arquivo dados.json possui formato JSON inválido."
            )

        if not isinstance(dados, dict):
            raise ValueError(
                "A estrutura principal do JSON deve ser um objeto."
            )

        if "frutas" not in dados:
            raise ValueError(
                "A lista de frutas não foi encontrada no JSON."
            )

        frutas_originais = dados["frutas"]

        if not isinstance(frutas_originais, list):
            raise ValueError(
                "O campo frutas precisa ser uma lista."
            )

        frutas_validas = []
        frutas_rejeitadas = 0

        for fruta in frutas_originais:
            if validar_fruta(fruta):
                frutas_validas.append(fruta)
            else:
                frutas_rejeitadas += 1
                

        exibir_frutas(frutas_validas)

        atualizar_indicadores(frutas_validas)

        processar_vetores(frutas_validas)

        registrar_evento(
            f"Processamento concluído. "
            f"{len(frutas_validas)} frutas válidas."
        )

        if frutas_rejeitadas > 0:
            registrar_evento(
                f"Atenção: {frutas_rejeitadas} registros rejeitados."
            )

    except Exception as erro:

        registrar_evento(f"Erro no sistema: {erro}")

        document.getElementById(
            "status-sistema"
        ).innerText = "Erro"


import asyncio

asyncio.create_task(iniciar_sistema())
