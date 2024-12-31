import telebot
from dotenv import load_dotenv
import os
import pandas as pd
from src.drive_bot import driveBot
from tabulate import tabulate  # Biblioteca para melhorar a formatação das tabelas

# Carrega as variáveis do ambiente
load_dotenv()

class TelegramBot:
    def __init__(self):
        TOKEN = os.getenv("API_KEY_TELEGRAM")
        if not TOKEN:
            raise ValueError("API_KEY_TELEGRAM não foi encontrado. Verifique o arquivo .env")

        self.bot = telebot.TeleBot(TOKEN)
        self.drive_bot = driveBot()  # Instância para interagir com a planilha

        # Configura handlers
        self.setup_handlers()

    def setup_handlers(self):
        bot = self.bot

        @bot.message_handler(commands=["start", "help"])
        def send_welcome(message):
            bot.reply_to(
                message,
                "Olá! Sou seu bot de gestão financeira.\n"
                "Comandos disponíveis:\n"
                "/ver_dados - Exibir dados da planilha\n"
                "/adicionar_dado - Adicionar novo dado\n"
                "/remover_dado - Remover um dado\n"
                "/atualizar_dado - Atualizar um dado existente"
            )

        @bot.message_handler(commands=["ver_dados"])
        def view_data(message):
            try:
                df = self.drive_bot.get_data()

                # Verifica se os dados são grandes demais
                if len(df.to_string()) > 4096:  # Limite de caracteres para mensagens de texto
                    # Se os dados forem grandes, envia como arquivo CSV
                    self.send_file(message, df)
                else:
                    # Se os dados forem pequenos, exibe com formatação
                    response = self.format_table(df)  # Formata os dados
                    bot.reply_to(message, f"Dados atuais na planilha:\n\n{response}")
            except Exception as e:
                bot.reply_to(message, f"Erro ao acessar dados: {str(e)}")

        @bot.message_handler(commands=["adicionar_dado"])
        def add_data(message):
            bot.reply_to(
                message,
                "Por favor, envie os dados no formato:\n\n"
                "`coluna1, coluna2, coluna3`\n\n"
                "Substitua pelos valores desejados.",
                parse_mode="Markdown"
            )

            @bot.message_handler(func=lambda msg: True)
            def handle_new_data(msg):
                try:
                    # Supondo que os dados sejam enviados no formato: "valor1, valor2, valor3"
                    new_data = msg.text.split(",")
                    if len(new_data) != len(self.drive_bot.get_data().columns):
                        bot.reply_to(msg, "Número de colunas inválido. Tente novamente.")
                        return
                    
                    self.drive_bot.add_row(new_data)  # Adiciona os dados na planilha
                    bot.reply_to(msg, "Dado adicionado com sucesso!")
                except Exception as e:
                    bot.reply_to(msg, f"Erro ao adicionar dado: {str(e)}")

    def format_table(self, df):
        """ Formata os dados para uma visualização mais bonita com o tabulate """
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)

    def send_file(self, message, df):
        """ Envia os dados como arquivo CSV """
        # Salva os dados em um arquivo CSV
        file_path = "dados.csv"
        df.to_csv(file_path, index=False)
        
        # Envia o arquivo para o usuário
        with open(file_path, "rb") as file:
            self.bot.send_document(message.chat.id, file)
    
    def start(self):
        print("Bot está ativo!")
        self.bot.polling()  # Inicia o polling do bot
