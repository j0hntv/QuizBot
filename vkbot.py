import os
import logging
import redis
import textwrap
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from random import choice
from dotenv import load_dotenv
from questions import get_questions


logger = logging.getLogger('QUIZ-VK')


def start(event, vk_api):
    user_id = event.user_id

    db.hset(user_id, 'number_of_questions_asked', 0)
    db.hset(user_id, 'number_of_right_answers', 0)
    db.hset(user_id, 'answer', '')

    vk_api.messages.send(
        user_id=user_id,
        message='Привет! Поиграем?',
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )

def handle_new_question_request(event, vk_api):
    user_id = event.user_id

    question, answer = choice(questions)

    db.hset(user_id, 'answer', answer)
    db.hincrby(user_id, 'number_of_questions_asked', 1)

    logger.info(f'<Вопрос> {question} <Ответ> {answer}')

    vk_api.messages.send(
        user_id=user_id,
        message=question,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )


def handle_solution_attempt(event, vk_api):

    user_id = event.user_id
    correct_answer = db.hget(user_id, 'answer').decode().lower().strip('."')
    user_answer = event.text.strip(' ."').lower()

    if not user_answer == correct_answer:
        vk_api.messages.send(
            user_id=user_id,
            message='Неправильный ответ или неверная команда.',
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id()
        )
        return

    message = textwrap.dedent('''\
        Правильно.
        Чтобы продолжить - нажми на Новый вопрос.''')

    vk_api.messages.send(
        user_id=user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=get_random_id()
    )
    db.hincrby(user_id, 'number_of_right_answers', 1)


def handle_give_up(event, vk_api):
    user_id = event.user_id
    answer = db.hget(user_id, 'answer').decode()

    if answer:

        message = textwrap.dedent(f'''\
            Правильный ответ: {answer}
            Чтобы продолжить - нажми на Новый вопрос.''')

        vk_api.messages.send(
            user_id=event.user_id,
            message=message,
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id()
        )
        
    db.hset(user_id, 'answer', '')


def handle_count(event, vk_api):
    user_id = event.user_id
    number_of_questions_asked = db.hget(user_id, 'number_of_questions_asked').decode()
    number_of_right_answers = db.hget(user_id, 'number_of_right_answers').decode()

    message = textwrap.dedent(f'''\
        Задано вопросов: {number_of_questions_asked}
        Правильных ответов: {number_of_right_answers}''')

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
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

    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)

    longpoll = VkLongPoll(vk_session)


    for event in longpoll.listen():
        if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
            continue

        if event.text == 'Начать':
            logger.info(event.text)
            start(event, vk_api)
        elif event.text == 'Новый вопрос':
            logger.info(event.text)
            handle_new_question_request(event, vk_api)
        elif event.text == 'Сдаться':
            logger.info(event.text)
            handle_give_up(event, vk_api)
        elif event.text == 'Мой счет':
            logger.info(event.text)
            handle_count(event, vk_api)
        else:
            logger.info(event.text)
            handle_solution_attempt(event, vk_api)

