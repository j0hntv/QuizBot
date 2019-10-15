import os
import logging
import redis
import textwrap
import random
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, Filters, ConversationHandler, RegexHandler
from questions import get_questions


logger = logging.getLogger('QUIZ-Telegram')


def start(bot, update):
    user = update.message.from_user.first_name
    user_id = update.message.from_user.id

    update.message.reply_text(text=f"Привет, {user}! Поиграем?", reply_markup=START_REPLY_MARKUP)

    db.hset(user_id, 'number_of_questions_asked', 0)
    db.hset(user_id, 'number_of_right_answers', 0)
    db.hset(user_id, 'answer', '')

    return PLAY


def handle_new_question_request(bot, update):
    user_id = update.message.from_user.id

    question, answer = random.choice(questions)

    update.message.reply_text(question, reply_markup=ANSWER_REPLY_MARKUP)
    logger.info(f'<Вопрос> {question} <Ответ> {answer}')

    db.hset(user_id, 'answer', answer)
    db.hincrby(user_id, 'number_of_questions_asked', 1)

    return ANSWER


def handle_solution_attempt(bot, update):
    user_id = update.message.from_user.id
    correct_answer = db.hget(user_id, 'answer').lower().strip('."')
    user_answer = update.message.text.lower()

    if not user_answer == correct_answer:
        update.message.reply_text('Неправильно.', reply_markup=ANSWER_REPLY_MARKUP)

        return ANSWER

    message = textwrap.dedent('''\
        Правильно.
        Чтобы продолжить - нажми на Новый вопрос.''')

    update.message.reply_text(text=message, reply_markup=PLAY_REPLY_MARKUP)
    db.hincrby(user_id, 'number_of_right_answers', 1)

    return PLAY


def handle_count(bot, update):
    user_id = update.message.from_user.id

    number_of_questions_asked = db.hget(user_id, 'number_of_questions_asked')
    number_of_right_answers = db.hget(user_id, 'number_of_right_answers')

    message = textwrap.dedent(f'''\
        Задано вопросов: {number_of_questions_asked}
        Правильных ответов: {number_of_right_answers}''')

    update.message.reply_text(text=message)


def handle_give_up(bot, update):
    user_id = update.message.from_user.id
    answer = db.hget(user_id, 'answer')

    message = textwrap.dedent(f'''\
        Правильный ответ: {answer}
        Чтобы продолжить - нажми на Новый вопрос.''')

    update.message.reply_text(text=message, reply_markup=PLAY_REPLY_MARKUP)

    return PLAY


def cancel(bot, update):
    user = update.message.from_user.first_name

    message = textwrap.dedent(f'''\
        Удачи, {user}!
        Чтобы начать сначала, нажми /start''')

    update.message.reply_text(text=message, reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END


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

    START_KEYBOARD = [['Новый вопрос']]
    ANSWER_KEYBOARD = [['Сдаться', 'Мой счет']]
    PLAY_KEYBOARD = [['Новый вопрос', 'Мой счет']]

    START_REPLY_MARKUP = ReplyKeyboardMarkup(START_KEYBOARD, resize_keyboard=True)
    ANSWER_REPLY_MARKUP = ReplyKeyboardMarkup(ANSWER_KEYBOARD, resize_keyboard=True)
    PLAY_REPLY_MARKUP = ReplyKeyboardMarkup(PLAY_KEYBOARD, resize_keyboard=True)

    PLAY, ANSWER = range(2)

    handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PLAY: [RegexHandler('Новый вопрос', handle_new_question_request),
                    RegexHandler('Мой счет', handle_count)],

            ANSWER: [RegexHandler('Мой счет', handle_count),
                    RegexHandler('Сдаться', handle_give_up),
                    RegexHandler('.{1,}', handle_solution_attempt)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    try:
        db = redis.Redis(REDIS_HOST, REDIS_PORT,
            password=REDIS_PASSWORD, decode_responses=True)

        db.get('None')
        logger.info('Redis connected.')

    except redis.exceptions.RedisError as error:
        logger.error(f'Redis: {error}')


    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()
