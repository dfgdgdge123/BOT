import telebot
import os
import requests
from random_func import update_recipe_of_the_day, get_recipe_of_the_day
from PIL import Image
from translator import translate
from io import BytesIO

API_TOKEN = '8086994241:AAHUUxXKfpGGGUEYXPmKVenIrdZWiqs8z9M'
IMAGE_FOLDER = "images"
server = 'https://www.themealdb.com/api/json/v1/1/search.php'

bot = telebot.TeleBot(API_TOKEN)
remove = telebot.types.ReplyKeyboardRemove()

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
    bot.send_message(message.chat.id, 'Введите название блюда.')
    bot.register_next_step_handler(message, search_by_name)


def search_by_name(message):
    response = requests.get(server + '?s=' + message.text).json()
    if response['meals']:
        names = [meal['strMeal'] for meal in response['meals']]
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        buttons = [telebot.types.KeyboardButton(text) for text in names]
        markup.add(*buttons)
        bot.send_message(message.chat.id, 'Вот, что удалось найти:', reply_markup=markup)
        bot.register_next_step_handler(message, show_info)
    else:
        bot.send_message(message.chat.id, 'Ничего не найдено.', reply_markup=remove)


@bot.message_handler()
def a(message):
    bot.send_message(message.chat.id, 'Неизвестная команда.', reply_markup=remove)


@bot.message_handler()
def show_info(message):
    response = requests.get(server + '?s=' + message.text).json()
    if response['meals']:
        meal = response['meals'][0]
        response = requests.get(meal['strMealThumb'])
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        name = meal['strMeal']
        country = meal['strArea']
        instructions = meal['strInstructions']
        categ = meal['strCategory']
        ingredients = [meal['strIngredient' + str(i)] for i in range(1, 21) if meal['strIngredient' + str(i)]]
        measure_ingredients = '\n'.join(
            [f"• {meal['strMeasure' + str(i + 1)]} {ingredients[i]}" for i in range(len(ingredients))])

        caption = f"{name}\n\nКатегория: {categ}\nСтрана: {country}\n\nИнгридиенты:\n{measure_ingredients}"
        bot.send_photo(message.chat.id, image, caption=caption, parse_mode="HTML", reply_markup=remove)
        bot.send_message(message.chat.id, f'Приготовление:\n{instructions}')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка.')


bot.polling(none_stop=True)
