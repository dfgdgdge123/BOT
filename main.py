import telebot
import os
from random_func import update_recipe_of_the_day, get_recipe_of_the_day
from PIL import Image
from translator import translate

bot = telebot.TeleBot('8086994241:AAG8NYaP-2dxDJMyKFnqutIMCs-nUIxaLys')

IMAGE_FOLDER = "images"
server = 'www.themealdb.com/api/json/v1/1/'

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
    bot.send_message(message.chat.id, "<b>Привет!</b> Я бот FridgeChef. 👋\n"
                                      "Пиши команду /help чтобы узнать, что я умею", parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "💥 Итак, я могу:\n• Найти рецепты по ингредиентам.\n"
                                      "• Подобрать блюда под вашу диету (кето, веган, ПП и другие).\n"
                                      "• Предложить случайный рецепт дня. (/recipe_of_the_day)\n\n"
                                      "<b>Готовьте с удовольствием и без лишних хлопот! ⭐️</b>", parse_mode="HTML")




@bot.message_handler(commands=['recipe_of_the_day'])
def random_recipe(message):
    update_recipe_of_the_day()
    recipe_of_the_day = get_recipe_of_the_day()

    if recipe_of_the_day:
        image_path = os.path.join(IMAGE_FOLDER, recipe_of_the_day["image"])

        if os.path.exists(image_path):
            image_path = resize_image(image_path)

            name = recipe_of_the_day['name']
            instructions = recipe_of_the_day['instructions']

            caption = f"<b>{name}</b>\n\n{instructions}"

            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "Изображение рецепта не найдено.")
    else:
        bot.send_message(message.chat.id, "Рецепт дня не найден. Попробуйте позже.")
@bot.message_handler(commands=['search'])
def search(message):
    bot.send_message(message.chat.id, translate(message.text, 'en'))


bot.polling(none_stop=True)
