from dotenv import load_dotenv
import os
import requests
import json

# DETALHES IMPORTANTES:
# Crie um .env no diretório GESTOR_FINANCEIRO/ com uma variável API_KEY_TELEGRAM, obtida ao criar o BOT do TELEGRAM

load_dotenv()

class TelegramBot:
    def __init__(self):
        TOKEN = os.getenv("API_KEY_TELEGRAM")
        if not TOKEN:
            raise ValueError("API_KEY_TELEGRAM não foi encontrado. Verifique o arquivo .env")

        self.url = f"https://api.telegram.org/bot{TOKEN}/"

    def start(self):
        update_id = None
        while True:
            update = self.get_message(update_id)
            # print(update)  # Debug
            new_message = update['result']
            if new_message:
                for message in new_message:
                    try:
                        update_id = message['update_id']
                        chat_id = message['message']['from']['id']
                        text = message['message']['text']
                        answer_bot = self.create_answer(text)
                        self.send_answer(chat_id, answer_bot)
                    except Exception as e:
                        print(f"Erro ao processar mensagem: {e}")  # Debug

    def get_message(self, update_id):
        request = f"{self.url}getUpdates?timeout=1000"
        if update_id:
            request = f"{self.url}getUpdates?timeout=1000&offset={update_id + 1}"
        answer = requests.get(request)
        return json.loads(answer.content)
    
    def create_answer(self, text):
        if text in ["Oi", "Olá", "E aí?", "Tudo bem?"]:
            return "Olá, tudo bem?"
        else:
            return "Não entendi"
    
    def send_answer(self, chat_id, answer):
        link_to_send = f"{self.url}sendMessage?chat_id={chat_id}&text={answer}"
        # print(f"Enviando para: {link_to_send}")  # Debug
        response = requests.get(link_to_send)
        # print(response.json())  # Debug
        return
