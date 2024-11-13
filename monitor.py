import time
import requests
import logging
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageFont

# Definindo variáveis globais
DELAY_TIME = 20
PROGRESS_PERCENTAGE = -1
ESTIMATIVA = -1
GCODE_NAME = "N/A"
TEMPO_TOTAL = -1
STOP_GET_NAME = False

# Configuração do logger para depuração
logging.basicConfig(
    filename="widget_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = "http://192.168.31.92:4409/printer/objects/query?print_stats&virtual_sdcard=filename,print_duration,progress"


def main():
    stop_requested = False  # Variável para controlar o loop

    def get_metadata():
        global TEMPO_TOTAL
        try:
            response = requests.get(f"http://192.168.31.92:4409/server/files/metadata?filename={GCODE_NAME}")
            response.raise_for_status()
            data = response.json()
            TEMPO_TOTAL = data.get("result", {}).get("estimated_time", 0)
            logging.info(f"Nome do arquivo: {GCODE_NAME} tempo estimado {TEMPO_TOTAL}")
        except requests.RequestException as e:
            logging.error(f"Erro ao fazer a requisição para a API: {e}")

    def process_response(data):
        global GCODE_NAME, TEMPO_TOTAL, PROGRESS_PERCENTAGE, ESTIMATIVA
        print_stats = data.get("result", {}).get("status", {}).get("print_stats", {})
        virtual_sdcard = data.get("result", {}).get("status", {}).get("virtual_sdcard", {})

        GCODE_NAME = print_stats.get("filename", "N/A")
        print_duration = print_stats.get("print_duration", 0)
        PROGRESS_PERCENTAGE = int(virtual_sdcard.get("progress", 0) * 100)

        if TEMPO_TOTAL == -1 and GCODE_NAME != "N/A":
            get_metadata()
        else:
            ESTIMATIVA = TEMPO_TOTAL - print_duration
            logging.info(f"Tempo Restante: {ESTIMATIVA // 60 // 60}h e {(ESTIMATIVA // 60) % 60}min , estimativa = {ESTIMATIVA}")

    def update_icon(icon):
        # Cria um novo ícone com o valor da porcentagem no centro
        progress_image = Image.new("RGB", (64, 64), "white")
        draw = ImageDraw.Draw(progress_image)

        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except IOError:
            font = ImageFont.load_default()

        text = "OK" if PROGRESS_PERCENTAGE == 100 else ("EPT" if PROGRESS_PERCENTAGE == 0 else f"{PROGRESS_PERCENTAGE}")
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_x = (64 - (text_bbox[2] - text_bbox[0])) // 2
        text_y = (64 - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), text, fill="black", font=font)

        # Atualiza o ícone, o menu e o título com o novo progresso
        icon.icon = progress_image
        icon.menu = Menu(
            MenuItem(f"Progresso: {PROGRESS_PERCENTAGE}%", None, enabled=False),
            MenuItem(f"Tempo Restante: {ESTIMATIVA // 60 // 60}h e {(ESTIMATIVA // 60) % 60}min", None, enabled=False),
            MenuItem("Sair", lambda icon, item: stop_icon(icon))
        )
        icon.title = f"Progresso: {PROGRESS_PERCENTAGE}% finaliza: {time.strftime('%d/%m %H:%M', time.localtime(time.time() + ESTIMATIVA))}"

    def stop_icon(icon):
        nonlocal stop_requested
        stop_requested = True
        icon.stop()
        logging.info("Ícone da impressora encerrado.")

    # Configura o ícone inicial com 0% de progresso
    icon = Icon("Printer Progress")
    icon.icon = Image.new("RGB", (64, 64), "white")  # Ícone inicial em branco
    icon.menu = Menu(
        MenuItem("Progresso: 0%", None, enabled=False),
        MenuItem("Sair", lambda icon, item: stop_icon(icon))
    )
    icon.title = "Progresso: 0%"  # Define o texto inicial do tooltip

    icon.run_detached()  # Inicia o ícone em segundo plano
    logging.info("Ícone da impressora iniciado na bandeja do sistema.")

    while not stop_requested:
        logging.info("Início da atualização de status de impressão.")
        try:
            # Faz a requisição para obter o progresso da API
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            process_response(data)
            update_icon(icon)
            logging.info(f"Ícone atualizado com progresso de {PROGRESS_PERCENTAGE}%")
        except requests.RequestException as e:
            logging.error(f"Erro ao fazer a requisição para a API: {e}")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")

        time.sleep(DELAY_TIME)  # Aguarda antes da próxima atualização
        logging.info("Aguardando próxima atualização...")

if __name__ == "__main__":
    main()
