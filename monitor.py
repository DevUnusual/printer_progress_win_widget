import time
import requests
import logging
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageFont

delayTime = 20
estimativa = -1
progress_percentage = -1

# Configuração do logger para depuração
logging.basicConfig(
    filename="widget_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    # URL da API para obter o progresso porta 4409, nao sei se funciona no fluid, possivelmente sim
    API_URL = "http://192.168.31.92:4409/printer/objects/query?virtual_sdcard=progress"
    API_TIMEOBJ = "http://192.168.31.92:4409/printer/objects/query?print_stats=print_duration"
    stop_requested = False  # Variável para controlar o loop

    def estimativa_tempo():
        global estimativa
        global progress
        try:
            #time.sleep(5)
            # Faz a requisição para obter o progresso da API
            logging.info("Realizando requisição para a API.")
            response = requests.get(API_TIMEOBJ)
            response.close()
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Resposta da API: {data}")

            # Extrai o valor de progresso da resposta
            timing = data.get("result", {}).get("status", {}).get("print_stats", {}).get("print_duration", 0)
            estimativa = timing/progress_percentage
            logging.info(f"Tempo Restante: {estimativa}min")
        except requests.RequestException as e:
            logging.error(f"Erro ao fazer a requisição para a API: {e}")

    # Define a função para encerrar o loop
    def stop_icon(icon, item):
        nonlocal stop_requested
        stop_requested = True
        icon.stop()
        logging.info("Ícone da impressora encerrado.")

    # Configura o ícone inicial com 0% de progresso
    icon = Icon("Printer Progress")
    icon.icon = Image.new("RGB", (64, 64), "white")  # Ícone inicial em branco
    icon.menu = Menu(
        MenuItem("Progresso: 0%", None, enabled=False),
        MenuItem("Sair", stop_icon)
    )
    icon.title = "Progresso: 0%"  # Define o texto inicial do tooltip

    icon.run_detached()  # Inicia o ícone em segundo plano
    logging.info("Ícone da impressora iniciado na bandeja do sistema.")

    while not stop_requested:
        global progress_percentage
        logging.info("Início da atualização de status de impressão.")
        try:
            # Faz a requisição para obter o progresso da API
            logging.info("Realizando requisição para a API.")
            response = requests.get(API_URL)
            response.close()
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Resposta da API: {data}")

            # Extrai o valor de progresso da resposta
            progress = data.get("result", {}).get("status", {}).get("virtual_sdcard", {}).get("progress", 0)
            progress_percentage = int(progress * 100)
            logging.info(f"Progresso obtido: {progress_percentage}%")

            # Cria um novo ícone com o valor da porcentagem no centro
            progress_image = Image.new("RGB", (64, 64), "white")  # Fundo branco
            draw = ImageDraw.Draw(progress_image)
            
            try:
                font = ImageFont.truetype("arial.ttf", 48)  # Tamanho da fonte aumentado para 48
            except IOError:
                font = ImageFont.load_default()

            # Desenha o texto de progresso centralizado
            if progress_percentage == 100:
              text = "OK"
              delayTime = 300
            elif progress_percentage == 0:
              text = "EPT"
              delayTime = 300
            else:
              text = f"{progress_percentage}"
              delayTime = 20
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (64 - text_width) // 2
            text_y = (64 - text_height) // 2
            draw.text((text_x, text_y), text, fill="black", font=font)

            # Atualiza o ícone, o menu e o título com o novo progresso
            icon.icon = progress_image
            icon.menu = Menu(
                MenuItem(f"Progresso: {progress_percentage}%", None, enabled=False),
                MenuItem(f"Tempo Restante: {estimativa//60}h e {estimativa%60 : .0f}min", estimativa_tempo() , enabled=False),
                MenuItem("Sair", stop_icon)
            )
            icon.title = f"Progresso: {progress_percentage}% estimativa: {time.strftime("%d/%m %H:%M",time.localtime(time.time() + estimativa*60))}"  # Atualiza o tooltip com o progresso atual
            logging.info(f"Ícone atualizado com progresso de {progress_percentage}%")
            
        except requests.RequestException as e:
            logging.error(f"Erro ao fazer a requisição para a API: {e}")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")

        time.sleep(delayTime)  # Aguarda 10 segundos antes da próxima atualização
        logging.info("Aguardando próxima atualização...")

if __name__ == "__main__":
    main()
