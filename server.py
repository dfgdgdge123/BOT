import requests
import telebot
import os
from history import add_dish, show_dishes, clear
from random_func import update_recipe_of_the_day, get_recipe_of_the_day, process_image
from favorites import add_to_favorites, get_favorites, create_favorite_button, remove_from_favorites, check_recipe_in_db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove

token = os.environ.get("token")
bot = telebot.TeleBot(token)
remove = ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])  # стартовая команда
def start(message):
    bot.send_message(message.chat.id, "<b>Hello!👋</b>\n"
                                      "Type /help to see what I can do", parse_mode="HTML", reply_markup=remove)


@bot.message_handler(commands=['search'])  # команда поиска блюд
def search_processing(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton('Name', callback_data='name'),
               InlineKeyboardButton('Category', callback_data='category'),
               InlineKeyboardButton('Country', callback_data='country'),
               InlineKeyboardButton('Ingredient', callback_data='ingredient'))
    bot.send_message(message.chat.id, '🔎 Search by:', reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data in ['name', 'category', 'country', 'ingredient'])  # выбор способа поиска
def search(call):
    if call.data == 'name':
        bot.send_message(call.message.chat.id, '💬 Enter the name of the food:', reply_markup=remove)
        bot.register_next_step_handler(call.message, search_by_name)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == 'category':
        search_by_category(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == 'country':
        search_by_country(call.message)
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == 'ingredient':
        bot.send_message(call.message.chat.id, '💬 Enter the name of the ingredient:', reply_markup=remove)
        bot.register_next_step_handler(call.message, search_by_ingredient)
        bot.delete_message(call.message.chat.id, call.message.message_id)


def search_by_name(message):  # поиск по названию
    if not command_handler(message):
        server = 'https://www.themealdb.com/api/json/v1/1/search.php?s='
        response = requests.get(server + message.text).json()

        if response['meals'] and response['meals'] != 'no data found':
            keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            names = []

            for meal in response['meals']:
                name = KeyboardButton(text=meal['strMeal'])
                keyboard.add(name)
                names.append(meal['strMeal'])

            bot.send_message(message.chat.id, '🔎 This is what I managed to find:', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_name, names)
        else:
            bot.send_message(message.chat.id, '❌ Nothing found. Try again.')
            bot.register_next_step_handler(message, search_by_name)


def preparing_recipe(meal=None, recipe_id=None):
    if recipe_id:
        server = 'https://www.themealdb.com/api/json/v1/1/lookup.php?i='
        meal = requests.get(server + str(recipe_id)).json()['meals'][0]
    img_data = requests.get(meal['strMealThumb']).content
    image = process_image(img_data)
    ingredients = []

    for i in range(1, 21):
        ingredient = meal.get(f'strIngredient{i}', '')
        measure = meal.get(f'strMeasure{i}', '')
        if ingredient:
            ingredients.append(f"{measure.strip()} {ingredient.strip()}".strip())

    recipe = {
        "id": meal['idMeal'],
        "name": meal['strMeal'],
        "image_bytes": image,
        "instructions": meal['strInstructions'],
        "ingredients": [ing for ing in ingredients if ing]}
    return recipe


def get_name(message, names=None, recipe_id=None):  # получение конкретного блюда
    if recipe_id:
        server = 'https://www.themealdb.com/api/json/v1/1/lookup.php?i='
        meal = requests.get(server + str(recipe_id)).json()['meals'][0]
        recipe = preparing_recipe(meal)
        send_recipe(message.chat.id, recipe)

    elif not command_handler(message):
        if message.text in names:
            server = 'https://www.themealdb.com/api/json/v1/1/search.php?s='
            meal = requests.get(server + message.text).json()['meals'][0]
            recipe = preparing_recipe(meal)
            send_recipe(message.chat.id, recipe)
        else:
            bot.send_message(message.chat.id, '🗒 Please select a dish from the list.')
            bot.register_next_step_handler(message, get_name, names)


def search_by_category(message):  # поиск по категории
    server = 'https://www.themealdb.com/api/json/v1/1/list.php?c=list'
    response = requests.get(server).json()
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    for category in response['meals']:
        button = KeyboardButton(category['strCategory'])
        keyboard.add(button)

    bot.send_message(message.chat.id, "🗒 Choose the category of the food:", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_category)


def get_category(message):  # получение конкретной категории
    if not command_handler(message):
        server = 'https://www.themealdb.com/api/json/v1/1/filter.php?c='
        response = requests.get(server + message.text).json()

        if response['meals'] and response['meals'] != 'no data found':
            keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            names = []

            for meal in response['meals']:
                name = KeyboardButton(text=meal['strMeal'])
                keyboard.add(name)
                names.append(meal['strMeal'])

            bot.send_message(message.chat.id, '🔎 This is what I managed to find:', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_name, names)
        else:
            bot.send_message(message.chat.id, "🗒 Please select a category from the list.")
            bot.register_next_step_handler(message, get_category)


def search_by_country(message):  # поиск по стране
    server = 'https://www.themealdb.com/api/json/v1/1/list.php?a=list'
    response = requests.get(server).json()
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    for category in response['meals']:
        button = KeyboardButton(category['strArea'])
        keyboard.add(button)

    bot.send_message(message.chat.id, "🗒 Choose the country of the food:", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_country)


def get_country(message):  # получение конкретной страны
    if not command_handler(message):
        server = 'https://www.themealdb.com/api/json/v1/1/filter.php?a='
        response = requests.get(server + message.text).json()

        if response['meals'] and response['meals'] != 'no data found':
            keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            names = []

            for meal in response['meals']:
                name = KeyboardButton(text=meal['strMeal'])
                keyboard.add(name)
                names.append(meal['strMeal'])

            bot.send_message(message.chat.id, '🔎 This is what I managed to find:', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_name, names)
        else:
            bot.send_message(message.chat.id, "🗒 Please select a country from the list.")
            bot.register_next_step_handler(message, get_country)


def search_by_ingredient(message):  # поиск по ингредиенту
    if not command_handler(message):
        server = 'https://www.themealdb.com/api/json/v1/1/filter.php?i='
        response = requests.get(server + message.text).json()

        if response['meals'] and response['meals'] != 'no data found':
            keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            names = []

            for meal in response['meals']:
                name = KeyboardButton(text=meal['strMeal'])
                keyboard.add(name)
                names.append(meal['strMeal'])

            bot.send_message(message.chat.id, '🔎 This is what I managed to find:', reply_markup=keyboard)
            bot.register_next_step_handler(message, get_name, names)
        else:
            bot.send_message(message.chat.id, '❌ Nothing found. Try again.')
            bot.register_next_step_handler(message, search_by_ingredient)


@bot.message_handler(commands=['help'])  # вызов справочника команд
def help(message):
    bot.send_message(message.chat.id, "💥 Here's what I can do:\n• Find recipes by criteria\n"
                                      "(ingredients, diet, country) (/search)\n"
                                      "• Suggest a random recipe of the day (/recipe_of_the_day)\n"
                                      "• Show your favorite dishes (/favorites)\n"
                                      "• Open your recipe history (/history)\n\n"
                                      "<b>Enjoy cooking with ease! ⭐️</b>", parse_mode="HTML", reply_markup=remove)


def send_recipe(chat_id, recipe):  # отправка рецепта пользователю
    add_dish(chat_id, recipe['id'], recipe['name'])
    ingredients_text = "\n".join([f"• {ing}" for ing in recipe.get("ingredients", [])])

    if "image_bytes" in recipe and recipe["image_bytes"]:
        recipe["image_bytes"].seek(0)
        if not check_recipe_in_db(chat_id, recipe['id']):
            markup = create_favorite_button(recipe['id'])
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
                parse_mode="HTML", reply_markup=remove
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


@bot.message_handler(commands=['recipe_of_the_day'])  # команда рецепта дня
def random_recipe(message):
    update_recipe_of_the_day()
    recipe = get_recipe_of_the_day()

    if recipe:
        send_recipe(message.chat.id, recipe)
    else:
        bot.send_message(message.chat.id, "❌ Recipe of the day not found. Please try again later.")


@bot.message_handler(commands=['favorites'])  # список понравившихся блюд
def show_favorites(message):
    favorites = get_favorites(message.from_user.id)

    if not favorites:
        bot.send_message(message.chat.id, "Your favorites list is empty.")
        return

    instruction = (
        "⭐ <b>Your favorite recipes:</b>\n\n"
        "To delete a recipe, send:\n"
        "<code>Delete Recipe_Name</code>\n\n"
    )
    markup = InlineKeyboardMarkup()
    last_send = True

    for i, recipe in enumerate(favorites):
        markup.add(InlineKeyboardButton(recipe[1], callback_data=f"show_recipe:{recipe[0]}"))
        if (i + 1) % 100 == 0:
            bot.send_message(message.chat.id, instruction, reply_markup=markup, parse_mode="HTML")
            instruction = '.'
            markup = InlineKeyboardMarkup()
            last_send = False
        else:
            last_send = True
    if last_send:
        bot.send_message(message.chat.id, instruction, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['history'])  # историю просмотренных блюд
def show_history(message):
    history_list = show_dishes(message.chat.id)

    if not history_list:
        bot.send_message(message.chat.id, "Your history is empty.")
        return

    instruction = (
        "⭐ <b>Your history of recipes:</b>\n\n"
        "To clear history, send:\n"
        "/clear_history\n\n"
    )
    markup = InlineKeyboardMarkup()
    last_send = True

    for i, recipe in enumerate(history_list):
        markup.add(InlineKeyboardButton(recipe[1], callback_data=f"show_recipe_from_history:{recipe[0]}"))
        if (i + 1) % 100 == 0:
            bot.send_message(message.chat.id, instruction, reply_markup=markup, parse_mode="HTML")
            instruction = '.'
            markup = InlineKeyboardMarkup()
            last_send = False
        else:
            last_send = True
    if last_send:
        bot.send_message(message.chat.id, instruction, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['clear_history'])
def clear_history(message):
    clear(message.chat.id)
    bot.send_message(message.chat.id, '✅ History successfully cleared.', reply_markup=remove)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith("add_to_favorites"):
        server = 'https://www.themealdb.com/api/json/v1/1/lookup.php?i='
        meal = requests.get(server + str(call.data.split(':')[1])).json()['meals'][0]
        recipe = preparing_recipe(meal)
        if not check_recipe_in_db(call.message.chat.id, recipe['id']):
            add_to_favorites(call.from_user.id, recipe['id'], recipe['name'])
            bot.answer_callback_query(call.id, "Recipe added to favorites!")
        else:
            bot.answer_callback_query(call.id, "Error adding to favorites")

    elif call.data.startswith("show_recipe:"):
        recipe_name = call.data.split(":")[1]
        favorites = get_favorites(call.from_user.id)
        id_and_name = next((r for r in favorites if r[1] == recipe_name), None)
        recipe = preparing_recipe(recipe_id=id_and_name[0])

        if recipe:
            send_recipe(call.message.chat.id, recipe)
        else:
            bot.send_message(call.message.chat.id, "Recipe not found")
    elif call.data.startswith("show_recipe_from_history:"):
        recipe_id = call.data.split(":")[1]
        get_name(call.message, recipe_id=recipe_id)


@bot.message_handler(func=lambda message: message.text.lower().startswith('delete '))
def handle_delete_favorite(message):
    user_id = message.from_user.id
    recipe_name = message.text[7:].strip()

    favorites = get_favorites(user_id)
    recipe_exists = any(r[1] == recipe_name for r in favorites)

    if recipe_exists:
        remove_from_favorites(user_id, recipe_name)
        bot.send_message(message.chat.id, f"✅ Recipe '{recipe_name}' has been removed from favorites!")
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Recipe '{recipe_name}' not found in your favorites.\n\nUse /favorites to see your list.",
            parse_mode="HTML"
        )


def command_handler(message):
    commands = {
        '/start': start,
        '/help': help,
        '/search': search_processing,
        '/recipe_of_the_day': random_recipe,
        '/favorites': show_favorites
    }
    if message.text in commands:
        commands[message.text](message)
        return True


def job():
    requests.get('https://glitch.com/edit/#!/screeching-shadow-celery?path=images%2Fcarbonara.jpg%3A1%3A0')


if __name__ == '__main__':
    bot.polling(none_stop=True)
    schedule.every(2).minutes.do(job)

    while True:
        schedule.run_pending()
