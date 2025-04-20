import requests
import telebot
from random_func import update_recipe_of_the_day, get_recipe_of_the_day
from favorites import add_to_favorites, get_favorites, create_favorite_button, remove_from_favorites
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot('8086994241:AAHUUxXKfpGGGUEYXPmKVenIrdZWiqs8z9M')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "<b>Hello!👋</b>\n"
                                      "Type /help to see what I can do", parse_mode="HTML")


@bot.message_handler(commands=['search'])
def search_processing(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Name', callback_data='name'),
               InlineKeyboardButton('Category', callback_data='category'),
               InlineKeyboardButton('Country', callback_data='country'),
               InlineKeyboardButton('Ingredient', callback_data='ingredient'))
    bot.send_message(message.chat.id, 'Search by:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['name', 'category', 'country', 'ingredient'])
def search(call):
    if call.data == 'name':
        bot.send_message(call.message.chat.id, 'Enter the name of the food:')
        bot.register_next_step_handler(call.message, search_by_name)


def search_by_name(message):
    server = 'https://www.themealdb.com/api/json/v1/1/search.php?s='
    print(message.text)


def search_by_category(message):
    server = 'https://www.themealdb.com/api/json/v1/1/filter.php?c='


def search_by_country(message):
    server = 'https://www.themealdb.com/api/json/v1/1/filter.php?a=Canadian'


def search_by_ingredient(message):
    pass


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "💥 Here's what I can do:\n• Find recipes by criteria\n"
                                      "(ingredients, diet, country) (/search)\n"
                                      "• Suggest a random recipe of the day (/recipe_of_the_day)\n"
                                      "• Show your favorite dishes (/favorites)\n"
                                      "• Open your recipe history (/history)\n\n"
                                      "<b>Enjoy cooking with ease! ⭐️</b>", parse_mode="HTML")


def send_recipe(chat_id, recipe, show_favorite_button=False):
    ingredients_text = "\n".join([f"• {ing}" for ing in recipe.get("ingredients", [])])

    if "image_bytes" in recipe and recipe["image_bytes"]:
        recipe["image_bytes"].seek(0)
        if show_favorite_button:
            markup = create_favorite_button()
            bot.send_photo(
                chat_id,
                recipe["image_bytes"],
                caption=f"<b>{recipe['name']}</b>\n\n<u>Ingredients:</u>\n{ingredients_text}",
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            bot.send_photo(
                chat_id,
                recipe["image_bytes"],
                caption=f"<b>{recipe['name']}</b>\n\n<u>Ingredients:</u>\n{ingredients_text}",
                parse_mode="HTML"
            )
    else:
        bot.send_message(
            chat_id,
            f"<b>{recipe['name']}</b>\n\n<u>Ingredients:</u>\n{ingredients_text}",
            parse_mode="HTML"
        )

    instructions = recipe.get('instructions', 'No instructions available')
    chunk_size = 4000
    for i in range(0, len(instructions), chunk_size):
        chunk = instructions[i:i + chunk_size]
        if i == 0:
            bot.send_message(chat_id, f"<u>Recipe:</u>\n{chunk}", parse_mode="HTML")
        else:
            bot.send_message(chat_id, chunk, parse_mode="HTML")


@bot.message_handler(commands=['recipe_of_the_day'])
def random_recipe(message):
    update_recipe_of_the_day()
    recipe = get_recipe_of_the_day()

    if recipe:
        send_recipe(message.chat.id, recipe, show_favorite_button=True)
    else:
        bot.send_message(message.chat.id, "Recipe of the day not found. Please try again later.")


@bot.message_handler(commands=['favorites'])
def show_favorites(message):
    favorites = get_favorites(message.from_user.id)

    if not favorites:
        bot.send_message(message.chat.id, "Your favorites list is empty.")
        return

    markup = InlineKeyboardMarkup()
    for recipe in favorites:
        markup.add(InlineKeyboardButton(recipe['name'], callback_data=f"show_recipe:{recipe['name']}"))

    instruction = (
        "⭐ <b>Your favorite recipes:</b>\n\n"
        "To delete a recipe, send:\n"
        "<code>Delete Recipe_Name</code>\n\n"
    )
    bot.send_message(message.chat.id, instruction, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "add_to_favorites":
        recipe = get_recipe_of_the_day()
        if recipe:
            add_to_favorites(call.from_user.id, recipe)
            bot.answer_callback_query(call.id, "Recipe added to favorites!")
        else:
            bot.answer_callback_query(call.id, "Error adding to favorites")

    elif call.data.startswith("show_recipe:"):
        recipe_name = call.data.split(":")[1]
        favorites = get_favorites(call.from_user.id)
        recipe = next((r for r in favorites if r['name'] == recipe_name), None)

        if recipe:
            send_recipe(call.message.chat.id, recipe)
        else:
            bot.send_message(call.message.chat.id, "Recipe not found")


@bot.message_handler(func=lambda message: message.text.lower().startswith('delete '))
def handle_delete_favorite(message):
    user_id = message.from_user.id
    recipe_name = message.text[7:].strip()

    favorites = get_favorites(user_id)
    recipe_exists = any(r['name'].lower() == recipe_name.lower() for r in favorites)

    if recipe_exists:
        remove_from_favorites(user_id, recipe_name)
        bot.send_message(message.chat.id, f"✅ Recipe '{recipe_name}' has been removed from favorites!")
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Recipe '{recipe_name}' not found in your favorites.\n\nUse /favorites to see your list.",
            parse_mode="HTML"
        )


bot.polling(none_stop=True)
