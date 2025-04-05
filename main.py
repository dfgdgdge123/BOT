import telebot
from random_func import update_recipe_of_the_day, get_recipe_of_the_day

bot = telebot.TeleBot('8086994241:AAHUUxXKfpGGGUEYXPmKVenIrdZWiqs8z9M')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "<b>Hello!👋</b>\n"
                                      "Type /help to see what I can do", parse_mode="HTML")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "💥 Here's what I can do:\n• Find recipes by criteria\n"
                                      "(ingredients, diet, country) (/search)\n"
                                      "• Suggest a random recipe of the day (/recipe_of_the_day)\n"
                                      "• Show your favorite dishes (/favorites)\n"
                                      "• Open your recipe history (/history)\n\n"
                                      "<b>Enjoy cooking with ease! ⭐️</b>", parse_mode="HTML")


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
                caption=f"<b>{recipe['name']}</b>\n\n<u>Ingredients:</u>\n{ingredients_text}",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"<b>{recipe['name']}</b>\n\n<u>Ingredients:</u>\n{ingredients_text}",
                parse_mode="HTML"
            )

        instructions = recipe.get('instructions', 'No instructions available')
        chunk_size = 4000
        for i in range(0, len(instructions), chunk_size):
            chunk = instructions[i:i + chunk_size]
            if i == 0:
                bot.send_message(message.chat.id, f"<u>Recipe:</u>\n{chunk}", parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, chunk, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Recipe of the day not found. Please try again later.")


@bot.message_handler(commands=['search'])
def search(message):
    bot.send_message(message.chat.id, "Search functionality will be implemented soon")


bot.polling(none_stop=True)