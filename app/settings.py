import telebot
import os
from apscheduler.schedulers.background import BackgroundScheduler


DB_PATH = 'data/database.db'
BOT_TOKEN = os.getenv('BOT_API_TOKEN')
GEO_TOKEN = os.getenv('GEO_API_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_API_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
sched = BackgroundScheduler()
