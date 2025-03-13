import random
import datetime

recipe_of_the_day = None
last_updated = None

recipes = [
    {
        "name": "Паста Карбонара",
        "image": "carbonara.jpg",
        "instructions": "1. Сварите спагетти.\n2. Обжарьте бекон.\n3. Смешайте яйца с сыром.\n4. Соедините всё вместе."
    },
    {
        "name": "Омлет с помидорами",
        "image": "eggs.jpg",
        "instructions": "1. Взбейте яйца.\n2. Нарежьте помидоры.\n3. Обжарьте всё на сковороде."
    },
    {
        "name": "Салат Цезарь",
        "image": "salad.jpeg",
        "instructions": "1. Нарежьте салат и курицу.\n2. Добавьте сухарики и соус.\n3. Перемешайте."
    }
]


def update_recipe_of_the_day():
    global recipe_of_the_day, last_updated
    today = datetime.date.today()
    if last_updated != today:
        recipe_of_the_day = random.choice(recipes)
        last_updated = today


def get_recipe_of_the_day():
    return recipe_of_the_day
