import threading
import time
import flet as ft
import serial  # pip install pyserial

# Configure a porta serial e a velocidade (baudrate) de acordo com seu microcontrolador (Arduino, ESP32, etc.)
PORTA_SERIAL = "COM14"  # No Linux/Mac use algo como '/dev/ttyUSB0' ou '/dev/ttyACM0'
BAUDRATE = 9600


def main(page: ft.Page):
    page.window.width = 400
    page.window.height = 700
    page.title = "Vital"
    page.bgcolor = "#0B191E"
    page.scroll = ft.ScrollMode.AUTO

    nome = "Mundo!"
    status_padrao = "Tudo parece bem"
    bpm = "71"
    oxigenio = "98"
    temperatura = "36,6"

    txt_nome = ft.Text(
        f"Olá, {nome}", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE
    )
    txt_subtitulo = ft.Text(
        "Veja como seu corpo está hoje.", size=14, color=ft.Colors.WHITE54
    )

    txt_status = ft.Text(
        f"Status: {status_padrao}",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_400,
    )

    txt_bpm = ft.Text(f"Frequência cardíaca: {bpm} bpm", color=ft.Colors.WHITE)
    txt_oxigenio = ft.Text(
        f"Saturação de O2: {oxigenio}%", color=ft.Colors.WHITE
    )
    txt_temperatura = ft.Text(
        f"Temperatura: {temperatura} °C", color=ft.Colors.WHITE
    )

    def toggle_sintoma(e):
        btn = e.control
        btn.selected = not btn.selected

        if btn.selected:
            btn.style = ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_700 if btn.grave else ft.Colors.BLUE_700,
                side=ft.BorderSide(
                    1, ft.Colors.RED_400 if btn.grave else ft.Colors.BLUE_400
                ),
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
            on_click=toggle_sintoma,
        )
        btn.selected = False
        btn.grave = grave
        return btn

    btn_dor_cabeca = criar_botao_sintoma("Dor de cabeça", grave=False)
    btn_cansaco = criar_botao_sintoma("Cansaço", grave=False)
    btn_falta_ar = criar_botao_sintoma("Falta de ar", grave=True)
    btn_palpitacoes = criar_botao_sintoma("Palpitações", grave=True)

    def verificar_sinais(e=None):
        txt_nome.value = f"Olá, {nome}"
        txt_bpm.value = f"Frequência cardíaca: {input_bpm.value} bpm"
        txt_oxigenio.value = f"Saturação de O2: {input_oxigenio.value}%"
        txt_temperatura.value = f"Temperatura: {input_temperatura.value} °C"

        alerta = False

        if btn_falta_ar.selected or btn_palpitacoes.selected:
            alerta = True

        # Checagem dos sinais vitais
        try:
            val_bpm = float(input_bpm.value.replace(",", "."))
            val_o2 = float(input_oxigenio.value.replace(",", "."))
            val_temp = float(input_temperatura.value.replace(",", "."))

            if (
                val_bpm < 60
                or val_bpm > 100
                or val_o2 < 95
                or val_temp < 35.0
                or val_temp > 37.5
            ):
                alerta = True

        except ValueError:
            pass

        if alerta:
            txt_status.value = "Status: ALERTA! CHAME UM MÉDICO!"
            txt_status.color = ft.Colors.RED_400
        else:
            txt_status.value = f"Status: {status_padrao}"
            txt_status.color = ft.Colors.GREEN_400

        page.update()

    input_bpm = ft.TextField(
        label="BPM (Normal: 60-100)", value=bpm, on_change=verificar_sinais
    )
    input_oxigenio = ft.TextField(
        label="O2 % (Normal: >=95)", value=oxigenio, on_change=verificar_sinais
    )
    input_temperatura = ft.TextField(
        label="Temp °C (Normal: 35.0-37.5)",
        value=temperatura,
        on_change=verificar_sinais,
    )

    page.add(
        txt_nome,
        txt_subtitulo,
        ft.Divider(color=ft.Colors.WHITE24),
        txt_status,
        txt_bpm,
        txt_oxigenio,
        txt_temperatura,
        ft.Divider(color=ft.Colors.WHITE24),
        ft.Text(
            "Sintomas atuais:",
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
        ft.Row(
            wrap=True,
            spacing=8,
            run_spacing=8,
            controls=[
                btn_dor_cabeca,
                btn_cansaco,
                btn_falta_ar,
                btn_palpitacoes,
            ],
        ),
        ft.Divider(color=ft.Colors.WHITE24),
        ft.Text(
            "Leitura do Sensor (Serial)",
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE70,
        ),
        input_bpm,
        input_oxigenio,
        input_temperatura,
    )

    # --- LEITURA DA PORTA SERIAL EM SEGUNDO PLANO ---
    def ler_serial():
        try:
            ser = serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=1)
            time.sleep(2)  # Tempo para inicializar a conexão serial

            while True:
                if ser.in_waiting > 0:
                    # Lê a linha enviada pelo microcontrolador (ex: "75,98\n")
                    linha = ser.readline().decode("utf-8").strip()

                    # Espera que o sensor envie os dados separados por vírgula
                    dados = linha.split(",")

                    if len(dados) == 2:
                        bpm_sensor, oxigenio_sensor = dados[0], dados[1]

                        # Atualiza os valores dos TextFields no Flet
                        input_bpm.value = bpm_sensor
                        input_oxigenio.value = oxigenio_sensor

                        # Recalcula os status e atualiza a interface
                        verificar_sinais()

        except serial.SerialException as err:
            print(f"Erro na conexão Serial: {err}")
        except Exception as e:
            print(f"Erro inesperado na leitura: {e}")

    # Inicia a thread paralela para não congelar a interface visual
    thread_serial = threading.Thread(target=ler_serial, daemon=True)
    thread_serial.start()


ft.app(target=main)
