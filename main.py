import telebot
import os
from random_func import update_recipe_of_the_day, get_recipe_of_the_day
from PIL import Image

bot = telebot.TeleBot('8086994241:AAG8NYaP-2dxDJMyKFnqutIMCs-nUIxaLys', parse_mode="MarkdownV2")

IMAGE_FOLDER = "images"


def escape_markdown(text):
    escape_chars = '_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def resize_image(image_path):
    with Image.open(image_path) as img:
        if img.format not in ['JPEG', 'JPG']:
            image_path = image_path.rsplit('.', 1)[0] + '.jpg'
            img = img.convert('RGB')

        if img.width < 320 or img.height < 320:
            new_size = (max(320, img.width), max(320, img.height))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        img.save(image_path, 'JPEG')

    return image_path


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот FridgeChef. Используй /random, чтобы получить рецепт дня.")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Доступные команды:\n/random - получить рецепт дня.")


@bot.message_handler(commands=['random'])
def random_recipe(message):
    update_recipe_of_the_day()
    recipe_of_the_day = get_recipe_of_the_day()

    if recipe_of_the_day:
        image_path = os.path.join(IMAGE_FOLDER, recipe_of_the_day["image"])

        if os.path.exists(image_path):
            image_path = resize_image(image_path)

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
