import shelve
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Хранилище для избранных рецептов
FAVORITES_DB = 'favorites.db'


def add_to_favorites(user_id, recipe):
    with shelve.open(FAVORITES_DB) as db:
        if str(user_id) not in db:
            db[str(user_id)] = []

        # Проверяем нет ли уже этого рецепта в избранном
        if not any(r['name'] == recipe['name'] for r in db[str(user_id)]):
            db[str(user_id)] = db[str(user_id)] + [recipe]


def get_favorites(user_id):
    with shelve.open(FAVORITES_DB) as db:
        return db.get(str(user_id), [])


def remove_from_favorites(user_id, recipe_name):
    with shelve.open(FAVORITES_DB) as db:
        if str(user_id) in db:
            db[str(user_id)] = [r for r in db[str(user_id)] if r['name'] != recipe_name]


def create_favorite_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⭐ Add to favorites", callback_data="add_to_favorites"))
    return markup