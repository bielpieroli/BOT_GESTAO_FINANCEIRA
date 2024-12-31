from src.telegram_bot import TelegramBot
from src.drive_bot import driveBot

# bot = TelegramBot()
# bot.start()

driveBot = driveBot()
print(driveBot.get_data())