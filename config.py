# тут будут находится все чувствительные и не публичные данные, по крайней мере пока ты не разберёшься, что такое .env
from dotenv import load_dotenv
import os

load_dotenv() # Загружает переменные окружения из .env

TOKEN = os.getenv('TELEGRAM_TOKEN') #bot token from BotFather
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')