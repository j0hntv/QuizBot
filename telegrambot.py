import os
import telegram
import logging
import redis
from random import randrange
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from questions import get_questions


logger = logging.getLogger('QUIZ-Telegram')


def start(bot, update):
    keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(text="Привет! Поиграем?", reply_markup=reply_markup)


def button(bot, update):
    if update.message.text == 'Новый вопрос':
        question_number = randrange(0, number_of_questions)

        question = questions[question_number][0]
        answer = questions[question_number][1]

        update.message.reply_text(question)

        update.message.reply_text(f'Ответ: {answer}')
        db.set(update.message.chat_id, question)


    elif update.message.text == 'Мой счет':
        update.message.reply_text('Твой счет: ')
        
    elif update.message.text == 'Сдаться':
        update.message.reply_text('Правильный ответ: ')

    
if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - [%(levelname)s] <{logger.name}> %(message)s')

    questions = get_questions()
    number_of_questions = len(questions)

    logger.info(f'Всего вопросов: {number_of_questions}')

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

    db = redis.Redis(REDIS_HOST, REDIS_PORT, password=REDIS_PASSWORD)
    logger.info('Redis connected.')

    updater = Updater(TELEGRAM_BOT_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(MessageHandler(Filters.text, button))

    updater.start_polling()
    updater.idle()