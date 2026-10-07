import json
import os
import random
import time
import threading
import requests
import flet as ft
import tempfile  # <-- IMPORTANTE: Adicione esta importação

# ---------------- CONFIGURAÇÃO E PERSISTÊNCIA CORRIGIDA PARA ANDROID ----------------
# Em vez de salvar na pasta local, usamos a pasta temporária do sistema,
# que sempre tem permissão de escrita no Android.
NOME_ARQUIVO_CONFIG = "config_telegram.json"
CONFIG_FILE = os.path.join(tempfile.gettempdir(), NOME_ARQUIVO_CONFIG)

TELEGRAM_BOT_TOKEN = "8893504897:AAFBfBgCvtWmrkyuYAKMSHhM1KPTGyse0h0"  # Substitua pelo Token do @BotFather

def carregar_chat_id():
    """Carrega o Chat ID salvo no arquivo JSON local."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get("chat_id", "")
        except Exception as e:
            print(f"Erro ao carregar arquivo de config: {e}")
    return ""

def salvar_chat_id(chat_id):
    """Salva o Chat ID no arquivo JSON local de forma persistente."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"chat_id": chat_id}, f, indent=4)
        print(f"Chat ID '{chat_id}' salvo com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar arquivo de config: {e}")

def enviar_telegram_alerta(mensagem, chat_id_destino):
    """Envia o alerta em background via API do Telegram."""
    def _enviar():
        chat_id_limpo = chat_id_destino.strip()
        if not chat_id_limpo:
            print("Chat ID do Telegram não configurado no painel Admin.")
            return

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id_limpo,
            "text": f"⚠️ *VITAL ALERTA MÉDICO* ⚠️\n\n{mensagem}",
            "parse_mode": "Markdown"
        }

        try:
            resposta = requests.post(url, json=payload, timeout=8)
            dados = resposta.json()
            if dados.get("ok"):
                print(f"Alerta enviado com sucesso para o Chat ID: {chat_id_limpo}!")
            else:
                print(f"Erro Telegram: {dados.get('description')}")
        except Exception as err:
            print(f"Erro na requisição HTTP Telegram: {err}")

    threading.Thread(target=_enviar, daemon=True).start()

# ---------------- APLICAÇÃO FLET ----------------

def main(page: ft.Page):

    #page.window.width = 400
    #page.window.height = 780
    page.title = "Vital"
    page.bgcolor = "#0B191E"
    page.scroll = ft.ScrollMode.AUTO

    em_alerta_anterior = False
    
    # Carrega o Chat ID previamente salvo ao iniciar a aplicação
    telegram_chat_id_salvo = carregar_chat_id()

    texto_termos_completo = (
        "TERMOS DE USO E ISENÇÃO DE RESPONSABILIDADE\n\n"
        "1. CARÁTER EXPERIMENTAL:\n"
        "Este aplicativo (Vital) está atualmente em fase de testes e desenvolvimento experimental.\n\n"
        "2. NÃO SUBSTITUI AVALIAÇÃO MÉDICA:\n"
        "As informações exibidas por este aplicativo NÃO constituem diagnóstico médico.\n\n"
        "3. USO POR SUA CONTA E RISCO:\n"
        "Ao utilizar este aplicativo, você concorda que o faz por sua própria conta e risco."
    )

    status_padrao = "Tudo parece bem"

    def gerar_sinais_saudaveis():
        bpm_val = random.randint(65, 85)
        o2_val = random.randint(96, 99)
        temp_val = round(random.uniform(36.2, 36.8), 1)
        return str(bpm_val), str(o2_val), str(temp_val).replace(".", ",")

    bpm, oxigenio, temperatura = gerar_sinais_saudaveis()

    txt_nome = ft.Text("Olá, Usuário", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    txt_subtitulo = ft.Text("Veja como seu corpo está hoje.", size=14, color=ft.Colors.WHITE54)
    
    txt_status = ft.Text(
        f"Status: {status_padrao}", 
        size=16, 
        weight=ft.FontWeight.BOLD, 
        color=ft.Colors.GREEN_400
    )

    txt_bpm = ft.Text(f"Frequência cardíaca: {bpm} bpm", color=ft.Colors.WHITE)
    txt_oxigenio = ft.Text(f"Saturação de O2: {oxigenio}%", color=ft.Colors.WHITE)
    txt_temperatura = ft.Text(f"Temperatura: {temperatura} °C", color=ft.Colors.WHITE)

    def toggle_sintoma(e):
        btn = e.control
        btn.selected = not btn.selected

        if btn.selected:
            btn.style = ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_700 if btn.grave else ft.Colors.BLUE_700,
                side=ft.BorderSide(1, ft.Colors.RED_400 if btn.grave else ft.Colors.BLUE_400),
            )
        else:
            btn.style = ft.ButtonStyle(
                color=ft.Colors.WHITE70,
                bgcolor=None,
                side=ft.BorderSide(1, ft.Colors.WHITE24),
            )

        verificar_sinais(e)

    def criar_botao_sintoma(texto, grave=False):
        btn = ft.OutlinedButton(
            text=texto,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE70,
                side=ft.BorderSide(1, ft.Colors.WHITE24),
            ),
            on_click=toggle_sintoma
        )
        btn.selected = False
        btn.grave = grave
        return btn

    botoes_sintomas = [
        criar_botao_sintoma("Dor de cabeça", grave=False),
        criar_botao_sintoma("Cansaço", grave=False),
        criar_botao_sintoma("Tontura", grave=False),
        criar_botao_sintoma("Enjoado/Náusea", grave=False),
        criar_botao_sintoma("Dor no corpo", grave=False),
        criar_botao_sintoma("Falta de ar", grave=True),
        criar_botao_sintoma("Palpitações", grave=True),
        criar_botao_sintoma("Dor no peito", grave=True),
        criar_botao_sintoma("Formigamento", grave=True),
    ]

    def resetar_botoes_sintomas():
        for btn in botoes_sintomas:
            btn.selected = False
            btn.style = ft.ButtonStyle(
                color=ft.Colors.WHITE70,
                bgcolor=None,
                side=ft.BorderSide(1, ft.Colors.WHITE24),
            )

    def verificar_sinais(e=None):
        nonlocal em_alerta_anterior

        txt_bpm.value = f"Frequência cardíaca: {input_bpm.value} bpm"
        txt_oxigenio.value = f"Saturação de O2: {input_oxigenio.value}%"
        txt_temperatura.value = f"Temperatura: {input_temperatura.value} °C"

        motivos = []
        sintomas_leves_selecionados = []

        for btn in botoes_sintomas:
            if btn.selected:
                if btn.grave:
                    motivos.append(btn.text)
                else:
                    sintomas_leves_selecionados.append(btn.text)

        if len(sintomas_leves_selecionados) >= 3:
            motivos.append(f"Múltiplos sintomas leves ({', '.join(sintomas_leves_selecionados)})")

        try:
            val_bpm = float(input_bpm.value.replace(",", "."))
            val_o2 = float(input_oxigenio.value.replace(",", "."))
            val_temp = float(input_temperatura.value.replace(",", "."))

            if val_bpm < 60:
                motivos.append(f"BPM baixo ({int(val_bpm)})")
            elif val_bpm > 100:
                motivos.append(f"BPM alto ({int(val_bpm)})")

            if val_o2 < 95:
                motivos.append(f"Saturação de O2 baixa ({int(val_o2)}%)")

            if val_temp < 35.0:
                motivos.append(f"Hipotermia ({val_temp:.1f}°C)")
            elif val_temp > 37.5:
                motivos.append(f"Febre ({val_temp:.1f}°C)")

        except ValueError:
            pass

        if motivos:
            detalhes = ", ".join(motivos)
            txt_status.value = f"Status: ALERTA! CHAME UM MÉDICO!\nMotivo(s): {detalhes}"
            txt_status.color = ft.Colors.RED_400

            if not em_alerta_anterior:
                em_alerta_anterior = True
                msg_telegram = f"Alerta do usuário *{input_login_nome.value or 'Paciente'}*.\n*Motivo(s):* {detalhes}"
                enviar_telegram_alerta(msg_telegram, telegram_chat_id_salvo)

        else:
            txt_status.value = f"Status: {status_padrao}"
            txt_status.color = ft.Colors.GREEN_400
            em_alerta_anterior = False

        page.update()

    def disparar_panico_manual(e):
        """Dispara um alerta imediato no Telegram ao clicar no botão do Admin."""
        msg_emergencia = f"🚨 *PÂNICO (TESTE ADMIN):* Alerta manual disparado por *{input_login_nome.value}*."
        enviar_telegram_alerta(msg_emergencia, telegram_chat_id_salvo)
        
        txt_status.value = "Status: ALERTA DE TESTE ENVIADO AO TELEGRAM!"
        txt_status.color = ft.Colors.RED_400
        page.update()

    # Botão de pânico exclusivo do Admin
    btn_panico_admin = ft.FilledButton(
        text="🚨 TESTAR ALERTA NO TELEGRAM",
        on_click=disparar_panico_manual,
        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_800, color=ft.Colors.WHITE),
        width=400
    )

    # Função para salvar a alteração do Chat ID diretamente no painel Admin
    def salvar_config_telegram(e):
        nonlocal telegram_chat_id_salvo
        novo_id = input_admin_chat_id.value.strip()
        telegram_chat_id_salvo = novo_id
        salvar_chat_id(novo_id)
        txt_feedback_save.value = "Configuração salva com sucesso!"
        page.update()

    input_admin_chat_id = ft.TextField(
        label="Chat ID do Telegram (Configuração Admin)", 
        value=telegram_chat_id_salvo,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.WHITE24
    )
    
    btn_salvar_chat_id = ft.OutlinedButton(
        text="Salvar Chat ID",
        on_click=salvar_config_telegram,
        style=ft.ButtonStyle(color=ft.Colors.BLUE_400)
    )

    txt_feedback_save = ft.Text("", color=ft.Colors.GREEN_400, size=12)

    # Simulador manual de sensores
    input_bpm = ft.TextField(label="BPM (Normal: 60-100)", value=bpm, on_change=verificar_sinais)
    input_oxigenio = ft.TextField(label="O2 % (Normal: >=95)", value=oxigenio, on_change=verificar_sinais)
    input_temperatura = ft.TextField(label="Temp °C (Normal: 35.0-37.5)", value=temperatura, on_change=verificar_sinais)

    container_inputs = ft.Column(
        visible=False,
        controls=[
            ft.Text("Simulador de Sensores", size=12, color=ft.Colors.WHITE38),
            input_bpm,
            input_oxigenio,
            input_temperatura
        ]
    )

    def alternar_visibilidade_inputs(e):
        container_inputs.visible = not container_inputs.visible
        btn_toggle_inputs.text = "Ocultar modo manual" if container_inputs.visible else "⚙ Ajuste Manual de Sensores"
        page.update()

    btn_toggle_inputs = ft.TextButton(
        text="⚙ Ajuste Manual de Sensores",
        on_click=alternar_visibilidade_inputs,
        style=ft.ButtonStyle(color=ft.Colors.WHITE38)
    )

    # Painel completo do Admin
    container_admin = ft.Container(
        visible=False,
        content=ft.Column(
            controls=[
                ft.Divider(color=ft.Colors.WHITE24),
                ft.Text("PAINEL DO ADMINISTRADOR", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                btn_panico_admin,
                ft.Container(height=5),
                input_admin_chat_id,
                btn_salvar_chat_id,
                txt_feedback_save,
                ft.Divider(color=ft.Colors.WHITE10),
                btn_toggle_inputs,
                container_inputs
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center
    )

    rodando_simulacao = False

    def simular_variacao_continua():
        nonlocal rodando_simulacao
        while rodando_simulacao:
            time.sleep(3)
            if not container_inputs.visible:
                try:
                    cur_bpm = int(input_bpm.value)
                    cur_o2 = int(input_oxigenio.value)
                    cur_temp = float(input_temperatura.value.replace(",", "."))

                    novo_bpm = max(55, min(105, cur_bpm + random.choice([-2, -1, 0, 1, 2])))
                    novo_o2 = max(93, min(100, cur_o2 + random.choice([-1, 0, 0, 1])))
                    nova_temp = round(max(35.5, min(37.8, cur_temp + random.choice([-0.1, 0.0, 0.1]))), 1)

                    input_bpm.value = str(novo_bpm)
                    input_oxigenio.value = str(novo_o2)
                    input_temperatura.value = str(nova_temp).replace(".", ",")

                    verificar_sinais()
                except ValueError:
                    pass

    def logout(e):
        nonlocal rodando_simulacao, em_alerta_anterior
        rodando_simulacao = False
        em_alerta_anterior = False

        input_login_nome.value = ""
        input_login_senha.value = ""
        chk_termos.value = False
        txt_erro_login.value = ""
        txt_feedback_save.value = ""

        resetar_botoes_sintomas()
        novo_bpm, novo_o2, nova_temp = gerar_sinais_saudaveis()
        input_bpm.value = novo_bpm
        input_oxigenio.value = novo_o2
        input_temperatura.value = nova_temp

        container_inputs.visible = False
        btn_toggle_inputs.text = "⚙ Ajuste Manual de Sensores"
        container_admin.visible = False

        page.controls.clear()
        page.add(login_view)
        page.update()

    btn_logout = ft.TextButton(
        text="Sair",
        on_click=logout,
        style=ft.ButtonStyle(color=ft.Colors.WHITE38)
    )

    main_view = ft.Column(
        controls=[
            btn_logout,
            txt_nome,
            txt_subtitulo,
            ft.Divider(color=ft.Colors.WHITE24),
            txt_status,
            txt_bpm,
            txt_oxigenio,
            txt_temperatura,
            ft.Divider(color=ft.Colors.WHITE24),
            ft.Text("Sintomas atuais:", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row(
                wrap=True,
                spacing=8,
                run_spacing=8,
                controls=botoes_sintomas
            ),
            container_admin
        ]
    )

    def ir_para_termos(e):
        page.controls.clear()
        page.add(termos_view)
        page.update()

    def voltar_para_login(e):
        page.controls.clear()
        page.add(login_view)
        page.update()

    termos_view = ft.Column(
        controls=[
            ft.Container(height=20),
            ft.Text("Termos de Uso", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Divider(color=ft.Colors.WHITE24),
            ft.Text(texto_termos_completo, size=14, color=ft.Colors.WHITE70),
            ft.Container(height=20),
            ft.FilledButton(
                text="Voltar ao Login",
                on_click=voltar_para_login,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
                width=400
            )
        ]
    )

    input_login_nome = ft.TextField(
        label="Nome ou Usuário", 
        color=ft.Colors.WHITE,
        border_color=ft.Colors.WHITE24
    )
    input_login_senha = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True,
        color=ft.Colors.WHITE,
        border_color=ft.Colors.WHITE24
    )
    
    chk_termos = ft.Checkbox(value=False)
    
    row_termos = ft.Row(
        controls=[
            chk_termos,
            ft.Text("Concordo com os", size=12, color=ft.Colors.WHITE70),
            ft.TextButton(
                text="Termos de uso",
                on_click=ir_para_termos,
                style=ft.ButtonStyle(color=ft.Colors.BLUE_400, padding=0)
            )
        ],
        spacing=0
    )

    txt_erro_login = ft.Text("", color=ft.Colors.RED_400, size=12)

    def realizar_login(e):
        nonlocal rodando_simulacao

        if not chk_termos.value:
            txt_erro_login.value = "Você precisa aceitar os termos de uso para continuar."
            page.update()
            return

        txt_erro_login.value = ""
        nome_digitado = input_login_nome.value.strip()
        senha_digitada = input_login_senha.value.strip()

        # Verifica se é admin
        is_admin = (nome_digitado == "admin" and senha_digitada == "admin")
        container_admin.visible = is_admin

        # Atualiza o campo com o ID salvo atual
        input_admin_chat_id.value = telegram_chat_id_salvo

        exibicao_nome = nome_digitado if nome_digitado else "Usuário"
        txt_nome.value = f"Olá, {exibicao_nome}"

        verificar_sinais()

        page.controls.clear()
        page.add(main_view)
        page.update()

        if not rodando_simulacao:
            rodando_simulacao = True
            threading.Thread(target=simular_variacao_continua, daemon=True).start()

    btn_entrar = ft.FilledButton(
        text="Entrar",
        on_click=realizar_login,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE
        ),
        width=400
    )

    login_view = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.Container(height=20),
            ft.Text("Vital", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Text("Acesse sua conta para continuar", size=14, color=ft.Colors.WHITE54),
            ft.Container(height=10),
            input_login_nome,
            input_login_senha,
            row_termos,
            txt_erro_login,
            ft.Container(height=5),
            btn_entrar
        ]
    )

    page.add(login_view)

ft.app(target=main)
