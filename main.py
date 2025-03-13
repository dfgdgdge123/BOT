import telebot
import random
import datetime
import os

bot = telebot.TeleBot('8086994241:AAG8NYaP-2dxDJMyKFnqutIMCs-nUIxaLys', parse_mode="MarkdownV2")  # Включаем MarkdownV2

IMAGE_FOLDER = "images"

recipes = [
    {
        "name": "Паста Карбонара",
        "image": "carbonara.jpg",
        "instructions": "1. Сварите спагетти. 2. Обжарьте бекон. 3. Смешайте яйца с сыром. 4. Соедините всё вместе."
    },
    {
        "name": "Омлет с помидорами",
        "image": "eggs.jpg",
        "instructions": "1. Взбейте яйца. 2. Нарежьте помидоры. 3. Обжарьте всё на сковороде."
    },
    {
        "name": "Салат Цезарь",
        "image": "salad.jpeg",
        "instructions": "1. Нарежьте салат и курицу. 2. Добавьте сухарики и соус. 3. Перемешайте."
    }
]

recipe_of_the_day = None
last_updated = None


def escape_markdown(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def update_recipe_of_the_day():
    global recipe_of_the_day, last_updated
    today = datetime.date.today()
    if last_updated != today:
        recipe_of_the_day = random.choice(recipes)
        last_updated = today


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот FridgeChef. Используй /random, чтобы получить рецепт дня.")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n/random - получить рецепт дня.")


@bot.message_handler(commands=['random'])
def random_recipe(message):
    update_recipe_of_the_day()
    if recipe_of_the_day:
        image_path = os.path.join(IMAGE_FOLDER, recipe_of_the_day["image"])

        if os.path.exists(image_path):
            name = escape_markdown(recipe_of_the_day['name'])
            instructions = escape_markdown(recipe_of_the_day['instructions'])

            caption = f"*{name}*\n\n{instructions}"

            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption)
        else:
            bot.send_message(message.chat.id, "Изображение рецепта не найдено.")
    else:
        bot.send_message(message.chat.id, "Рецепт дня не найден. Попробуйте позже.")


bot.polling(none_stop=True)