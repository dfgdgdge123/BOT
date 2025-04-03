import telebot
import os
from random_func import update_recipe_of_the_day, get_recipe_of_the_day
from PIL import Image
from translator import translate

bot = telebot.TeleBot('8086994241:AAHUUxXKfpGGGUEYXPmKVenIrdZWiqs8z9M')

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
    bot.send_message(message.chat.id, "<b>Привет!👋\n"
                                      "Пиши команду /help чтобы узнать, что я умею", parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "💥 Итак, я могу:\n• Найти рецепты по ингредиентам.\n"
                                      "• Подобрать блюда под вашу диету (кето, веган, ПП).\n"
                                      "• Предложить случайный рецепт дня. (/recipe_of_the_day)\n\n"
                                      "<b>Готовьте с удовольствием и без лишних хлопот! ⭐️</b>", parse_mode="HTML")


@bot.message_handler(commands=['recipe_of_the_day'])
def random_recipe(message):
    update_recipe_of_the_day()
    recipe = get_recipe_of_the_day()

    if recipe:
        image_path = recipe["image"]

        if os.path.exists(image_path):
            ingredients_text = "\n".join([f"• {ing}" for ing in recipe.get("ingredients", [])])

            with open(image_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=f"<b>{recipe['name']}</b>\n\n<u>Ингредиенты:</u>\n{ingredients_text}",
                    parse_mode="HTML"
                )

            bot.send_message(
                message.chat.id,
                f"<u>Рецепт:</u>\n{recipe['instructions']}",
                parse_mode="HTML"
            )
        else:
            ingredients_text = "\n".join([f"• {ing}" for ing in recipe.get("ingredients", [])])
            bot.send_message(
                message.chat.id,
                f"<b>{recipe['name']}</b>\n\n<u>Ингредиенты:</u>\n{ingredients_text}\n\n"
                f"<u>Рецепт:</u>\n{recipe['instructions']}",
                parse_mode="HTML"
            )
    else:
        bot.send_message(message.chat.id, "Рецепт дня не найден. Попробуйте позже.")


@bot.message_handler(commands=['search'])
def search(message):
    bot.send_message(message.chat.id, translate(message.text, 'en'))


bot.polling(none_stop=True)