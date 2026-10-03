import random
import time
import threading
import flet as ft

def main(page: ft.Page):

    page.window.width = 400
    page.window.height = 700
    page.title = "Vital"
    page.bgcolor = "#0B191E"
    page.scroll = ft.ScrollMode.AUTO

    
    texto_checkbox = "Concordo estar usando um Aplicativo em fases de teste e que os dados apresentados não substituem avaliação médica."

    status_padrao = "Tudo parece bem"

def logout(page: ft.Page):
    page.controls.clear()

    # Função para sortear valores iniciais saudáveis
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

    btn_dor_cabeca = criar_botao_sintoma("Dor de cabeça", grave=False)
    btn_cansaco = criar_botao_sintoma("Cansaço", grave=False)
    btn_falta_ar = criar_botao_sintoma("Falta de ar", grave=True)
    btn_palpitacoes = criar_botao_sintoma("Palpitações", grave=True)

    def verificar_sinais(e=None):
        txt_bpm.value = f"Frequência cardíaca: {input_bpm.value} bpm"
        txt_oxigenio.value = f"Saturação de O2: {input_oxigenio.value}%"
        txt_temperatura.value = f"Temperatura: {input_temperatura.value} °C"

        motivos = []

        if btn_falta_ar.selected:
            motivos.append("Falta de ar")
        if btn_palpitacoes.selected:
            motivos.append("Palpitações")

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
        else:
            txt_status.value = f"Status: {status_padrao}"
            txt_status.color = ft.Colors.GREEN_400

        page.update()

    input_bpm = ft.TextField(label="BPM (Normal: 60-100)", value=bpm, on_change=verificar_sinais)
    input_oxigenio = ft.TextField(label="O2 % (Normal: >=95)", value=oxigenio, on_change=verificar_sinais)
    input_temperatura = ft.TextField(label="Temp °C (Normal: 35.0-37.5)", value=temperatura, on_change=verificar_sinais)

    container_inputs = ft.Column(
        visible=False,
        controls=[
            ft.Text("Simulador de Sensores (Ajuste Manual)", size=12, color=ft.Colors.WHITE38),
            input_bpm,
            input_oxigenio,
            input_temperatura
        ]
    )

    def alternar_visibilidade_inputs(e):
        container_inputs.visible = not container_inputs.visible
        btn_toggle_inputs.text = "Ocultar modo manual" if container_inputs.visible else "⚙ Configuração manual"
        page.update()

    btn_toggle_inputs = ft.TextButton(
        text="⚙ Configuração manual",
        on_click=alternar_visibilidade_inputs,
        style=ft.ButtonStyle(color=ft.Colors.WHITE38)
    )

    
    rodando_simulacao = True

    def simular_variacao_continua():
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

    thread_simulacao = threading.Thread(target=simular_variacao_continua, daemon=True)

    # ------------------ CONSTRUÇÃO DAS TELAS ------------------

    
    main_view = ft.Column(
        controls=[
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
                controls=[
                    btn_dor_cabeca,
                    btn_cansaco,
                    btn_falta_ar,
                    btn_palpitacoes,
                ]
            ),
            ft.Divider(color=ft.Colors.WHITE10),
            ft.Container(
                content=ft.Column(
                    controls=[
                        btn_toggle_inputs,
                        container_inputs
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center
            )
        ]
    )

    
    input_login_nome = ft.TextField(
        label="Nome ou Usuário", 
        value="Nome",
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
    chk_termos = ft.Checkbox(
        label=texto_checkbox, 
        value=False,
        label_style=ft.TextStyle(color=ft.Colors.WHITE70, size=12)
    )

    def realizar_login(e):
        nome_digitado = input_login_nome.value.strip() or "Usuário"
        txt_nome.value = f"Olá, {nome_digitado}"
        
        
        page.controls.clear()
        page.add(main_view)
        page.update()

        
        if not thread_simulacao.is_alive():
            thread_simulacao.start()

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
        spacing=15,
        controls=[
            ft.Container(height=40),
            ft.Text("Vital", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Text("Acesse sua conta para continuar", size=14, color=ft.Colors.WHITE54),
            ft.Container(height=20),
            input_login_nome,
            input_login_senha,
            chk_termos,
            ft.Container(height=10),
            btn_entrar
        ]
    )

    # Inicializa o app na tela de login
    page.add(login_view)

ft.app(target=main)
