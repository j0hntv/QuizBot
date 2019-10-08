# QuizBot

Бот для проведения викторин в Telegram и Вконтакте.
- Пример бота для [Вконтакте](https://vk.com/xkcd_comics_fun)
- Пример бота для [Telegram](https://t.me/DevmanBot_bot)

## Установка
```
git clone https://github.com/j0hntv/QuizBot.git
```
- Распаковать архив `quiz-questions.zip` в `quiz-questions`
- Необходимые библиотеки:
```
pip3 install -r requirements.txt
```

## Переменные окружения
На машине должны быть доступны следующие переменные окружения:
```
TELEGRAM_BOT_TOKEN=<...>
VK_TOKEN=<...>
REDIS_HOST=<...>
REDIS_PORT=<...>
REDIS_PASSWORD=<...>
```

## Запуск
- Телеграм-бот:
```
python3 telegrambot.py
```
- VK-бот:
```
python3 vkbot.py
```

Сделано в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/modules/)