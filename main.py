import telebot
import os
from random_func import update_recipe_of_the_day, get_recipe_of_the_day
from PIL import Image
from translator import translate

bot = telebot.TeleBot('8086994241:AAHUUxXKfpGGGUEYXPmKVenIrdZWiqs8z9M')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "<b>Привет!👋</b>\n"
                                      "Пиши команду /help чтобы узнать, что я умею", parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "💥 Итак, я могу:\n• Найти рецепты по заданным критериям.\n"
                                      "(игнредиенты, диета, страна) (/search)\n"
                                      "• Предложить случайный рецепт дня. (/recipe_of_the_day)\n"
                                      "• Показать список понравившихся вам блюд. (/favorites)\n"
                                      "• Открыть список просмотренных рецептов. (/history)\n\n"
                                      "<b>Готовьте с удовольствием и без лишних хлопот! ⭐️</b>", parse_mode="HTML")


@bot.message_handler(commands=['recipe_of_the_day'])
def random_recipe(message):
    update_recipe_of_the_day()
    recipe = get_recipe_of_the_day()

    if recipe:
        ingredients_text = "\n".join([f"• {ing}" for ing in recipe.get("ingredients", [])])

        if "image_bytes" in recipe:
            recipe["image_bytes"].seek(0)
            bot.send_photo(
                message.chat.id,
                recipe["image_bytes"],
                caption=f"<b>{recipe['name']}</b>\n\n<u>Ингредиенты:</u>\n{ingredients_text}",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"<b>{recipe['name']}</b>\n\n<u>Ингредиенты:</u>\n{ingredients_text}",
                parse_mode="HTML"
            )

        instructions = recipe.get('instructions', 'Инструкции отсутствуют')
        chunk_size = 4000
        for i in range(0, len(instructions), chunk_size):
            chunk = instructions[i:i + chunk_size]
            if i == 0:
                bot.send_message(message.chat.id, f"<u>Рецепт:</u>\n{chunk}", parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, chunk, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Рецепт дня не найден. Попробуйте позже.")


@bot.message_handler(commands=['search'])
def search(message):
    bot.send_message(message.chat.id, translate(message.text, 'en'))


bot.polling(none_stop=True)