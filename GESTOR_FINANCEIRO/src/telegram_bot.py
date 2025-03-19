import telebot
from dotenv import load_dotenv
import os
import pandas as pd
from src.drive_bot import driveBot
from tabulate import tabulate  

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
                if df.empty:
                    bot.reply_to(message, "A planilha está vazia.")
                    return
                print(df)
                # Formata a tabela em partes
                table_parts = self.format_table(df)
                print(table_parts)
                for part in table_parts:
                    bot.send_message(message.chat.id, f"{part}", parse_mode="Markdown")
            except Exception as e:
                bot.reply_to(message, f"Erro ao acessar dados: {str(e)}")

        @bot.message_handler(commands=["adicionar_dado"])
        def add_data(message):
            bot.reply_to(
                message,
                "Por favor, envie os dados no formato:\n\n"
                "`TIPO, DATA, VALOR, ORIGEM`\n\n"
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

        @bot.message_handler(commands=["remover_dado"])
        def remove_data(message):
            try:
                df = self.drive_bot.get_data()
                if df.empty:
                    bot.reply_to(message, "A planilha está vazia, não há dados para remover.")
                    return

                # Envia os dados com índices para o usuário
                formatted_table = tabulate(df.reset_index(), headers='keys', tablefmt='grid', showindex=True)
                bot.reply_to(
                    message,
                    f"Dados atuais na planilha:\n\n{formatted_table}\n\n"
                    "Envie o número da linha que deseja remover."
                )

                @bot.message_handler(func=lambda msg: True)
                def handle_remove_index(msg):
                    try:
                        index_to_remove = int(msg.text.strip())  # Lê o índice do usuário
                        if index_to_remove < 0 or index_to_remove >= len(df):
                            bot.reply_to(msg, "Índice inválido. Tente novamente.")
                            return

                        # Remove a linha correspondente
                        self.drive_bot.delete_row(index_to_remove+1)
                        bot.reply_to(msg, "Linha removida com sucesso!")
                    except ValueError:
                        bot.reply_to(msg, "Por favor, envie um número válido.")
                    except Exception as e:
                        bot.reply_to(msg, f"Erro ao remover dado: {str(e)}")

            except Exception as e:
                bot.reply_to(message, f"Erro ao acessar dados: {str(e)}")
        
        @bot.message_handler(commands=["atualizar_dado"])
        def update_data(message):
            try:
                df = self.drive_bot.get_data()
                # Exibe a tabela com índices reiniciados para facilitar a identificação da linha
                response = self.format_table(df.reset_index())
                bot.reply_to(
                    message,
                    f"Dados atuais na planilha:\n\n{response}\n\n"
                    "Envie o índice da linha que deseja atualizar."
                )

                @bot.message_handler(func=lambda msg: True)
                def handle_index(msg):
                    try:
                        # Recebe o índice do usuário
                        user_index = int(msg.text)

                        # Verifica se o índice é válido
                        if user_index < 0 or user_index >= len(df):
                            bot.reply_to(msg, "Índice inválido. Tente novamente.")
                            return

                        # Armazena a linha selecionada para edição
                        selected_row = df.iloc[user_index].to_dict()
                        fields = "\n".join([f"{key}: {value}" for key, value in selected_row.items()])
                        bot.reply_to(
                            msg,
                            f"Você selecionou a linha:\n\n{fields}\n\n"
                            "Envie os novos valores no formato:\n"
                            "`campo1=valor1, campo2=valor2`\n\n"
                            "Somente os campos que deseja alterar precisam ser enviados.",
                            parse_mode="Markdown"
                        )

                        @bot.message_handler(func=lambda m: True)
                        def handle_update(m):
                            try:
                                # Recebe os valores a serem atualizados
                                updates = dict(
                                    item.split("=") for item in m.text.split(",") if "=" in item
                                )
                                updates = {k.strip(): v.strip() for k, v in updates.items()}

                                # Valida os campos informados
                                invalid_fields = [field for field in updates if field not in df.columns]
                                if invalid_fields:
                                    bot.reply_to(m, f"Campos inválidos: {', '.join(invalid_fields)}. Tente novamente.")
                                    return

                                # Atualiza os campos na linha selecionada
                                for field, value in updates.items():
                                    df.at[user_index, field] = value

                                # Atualiza a planilha
                                self.drive_bot.update_data(df)
                                bot.reply_to(m, "Linha atualizada com sucesso!")
                            except Exception as e:
                                bot.reply_to(m, f"Erro ao atualizar dado: {str(e)}")
                    except ValueError:
                        bot.reply_to(msg, "Por favor, envie um índice numérico válido.")
                    except Exception as e:
                        bot.reply_to(msg, f"Erro ao processar índice: {str(e)}")
            except Exception as e:
                bot.reply_to(message, f"Erro ao acessar dados: {str(e)}")


    def format_table(self, df):
        # Define o limite de caracteres para cada coluna
        column_limits = {
            'T': 2,
            'DATA': 6,
            'VALOR': 6,
            'ORIGEM': 15
        }

        # Ajusta o limite para cada coluna
        truncated_df = df.copy()

        for col in df.columns:
            limit = column_limits.get(col, 20)  # Limite padrão de 20 se não especificado
            truncated_df[col] = truncated_df[col].apply(
                lambda x: str(x)[:limit] + "..." if len(str(x)) > limit else str(x)
            )

        # Calcular o maior comprimento de cada coluna
        column_widths = {}
        for col in df.columns:
            max_len = max(truncated_df[col].apply(lambda x: len(str(x))))
            column_widths[col] = max(max_len, column_limits.get(col, 20))  # A largura mínima é o limite

        # Formata a tabela como uma string para o Telegram
        formatted_table = ""

        # Adiciona o cabeçalho com largura ajustada
        formatted_table += f"{'T':<{column_widths['T']}}|{' DATA':<{column_widths['DATA']}} |{' VALOR':<{column_widths['VALOR']}}|{' ORIGEM':<{column_widths['ORIGEM']}}\n"

        # Adiciona as linhas da tabela
        for row in truncated_df.itertuples(index=False):
            formatted_table += f"{str(row[0]):<{column_widths['T']}}|{str(row[1]):<{column_widths['DATA']}} |{str(row[2]):<{2*column_widths['VALOR']}}|{str(row[3]):<{column_widths['ORIGEM']}}\n"

        # Divida em partes caso a tabela exceda o limite do Telegram
        parts = [formatted_table[i:i + 4000] for i in range(0, len(formatted_table), 4000)]

        return parts



    def send_file(self, message, df):
        """ Envia os dados como arquivo XSL """
        # Salva os dados em um arquivo 
        file_path = "dados.xsl"
        df.to_xsl(file_path, index=False)
        
        # Envia o arquivo para o usuário
        with open(file_path, "rb") as file:
            self.bot.send_document(message.chat.id, file)
    
    def start(self):
        print("Bot está ativo!")
        self.bot.polling()  
