import os
import logging
import redis
import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from random import randrange
from dotenv import load_dotenv
from questions import get_questions


logger = logging.getLogger('QUIZ-VK')


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)

    user_id = event.user_id

    db.hset(user_id, 'total', 0)
    db.hset(user_id, 'count', 0)
    db.hset(user_id, 'answer', '')

    vk_api.messages.send(
        user_id=user_id,
        message='Привет! Поиграем?',
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )

def new_question(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)

    user_id = event.user_id

    question_number = randrange(0, number_of_questions)
    question = questions[question_number][0]
    answer = questions[question_number][1]

    db.hset(user_id, 'answer', answer)
    db.hincrby(user_id, 'total', 1)

    logger.info(f'<Вопрос> {question} <Ответ> {answer}')

    vk_api.messages.send(
        user_id=user_id,
        message=question,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )

def give_up(event, vk_api):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    
    user_id = event.user_id
    answer = db.hget(user_id, 'answer').decode()

    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Правильный ответ: {answer}\nЧтобы продолжить - нажми на Новый вопрос.',
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - [%(levelname)s] <{logger.name}> %(message)s')

    questions = get_questions()
    number_of_questions = len(questions)

    logger.info(f'Всего вопросов: {number_of_questions}')

    VK_TOKEN = os.getenv('VK_TOKEN')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

    try:
        db = redis.Redis(REDIS_HOST, REDIS_PORT, password=REDIS_PASSWORD)
        db.get('None')
        logger.info('Redis connected.')

    except redis.exceptions.RedisError as error:
        logger.error(f'Redis: {error}')

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Начать':
                start(event, vk_api)
            elif event.text == 'Новый вопрос':
                new_question(event, vk_api)
            elif event.text == 'Сдаться':
                give_up(event, vk_api)

