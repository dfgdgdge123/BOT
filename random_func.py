import random
import datetime
import requests
from PIL import Image
import os
import io
from googletrans import Translator
from deep_translator import GoogleTranslator
from functools import lru_cache

recipe_of_the_day = None
last_updated = None
translator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.ru'
])

UNIT_TRANSLATIONS = {
    'cup': 'стакан',
    'tablespoon': 'столовая ложка',
    'teaspoon': 'чайная ложка',
    'ounce': 'унция',
    'pound': 'фунт',
    'gram': 'грамм',
    'kilogram': 'килограмм',
    'milliliter': 'миллилитр',
    'liter': 'литр',
    'pinch': 'щепотка',
    'clove': 'зубчик',
    'slice': 'ломтик',
    'piece': 'штука',
    'can': 'банка'
}

@lru_cache(maxsize=1000)
def translate_to_russian(text):
    if not text or not isinstance(text, str):
        return text

    try:
        for eng_unit, ru_unit in UNIT_TRANSLATIONS.items():
            text = text.replace(eng_unit, ru_unit)

        return GoogleTranslator(source='auto', target='ru').translate(text)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text


def translate_to_russian(text):
    if not text or not isinstance(text, str):
        return text

    try:
        return GoogleTranslator(source='auto', target='ru').translate(text)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text


# Локальные рецепты на случай если API временно не работает
local_recipes = [
    {
        "name": "Паста Карбонара",
        "image": os.path.abspath(os.path.join("images", "carbonara.jpg")),
        "instructions": "Рецепт классической карбонары (на 4 порции):\n\n"
                        "1. Сварите спагетти в подсоленной воде с оливковым маслом до состояния 'аль денте'.\n"
                        "2. Нарежьте бекон тонкими полосками, чеснок измельчите.\n"
                        "3. Обжарьте бекон с чесноком на сковороде до румяности.\n"
                        "4. Натрите сыр, добавьте горячую воду от спагетти, взбейте желтки и смешайте с сыром.\n"
                        "5. Слейте воду со спагетти, добавьте к ним сырно-яичную смесь и бекон.\n"
                        "6. Перемешайте, приправьте солью и перцем. Подавайте горячим."
                        ,
        "ingredients": ["спагетти", "бекон", "яйца", "сыр"]
    },
]


def download_and_save_image(url, meal_id):
    try:
        # Создаем папку images если ее нет
        os.makedirs("images", exist_ok=True)

        response = requests.get(url)
        if response.status_code == 200:
            image_path = os.path.abspath(os.path.join("images", f"{meal_id}.jpg"))

            with open(image_path, 'wb') as f:
                f.write(response.content)

            with Image.open(image_path) as img:
                img = img.convert('RGB')
                if img.width < 320 or img.height < 320:
                    new_size = (max(320, img.width), max(320, img.height))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=85)

            return image_path
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")
    return None


def get_random_recipe_from_api():
    try:
        response = requests.get('https://www.themealdb.com/api/json/v1/1/random.php')
        if response.status_code == 200:
            meal = response.json()['meals'][0]

            image_path = download_and_save_image(meal['strMealThumb'], meal['idMeal'])
            if not image_path:
                return None

            name = translate_to_russian(meal['strMeal'])

            ingredients = []
            for i in range(1, 21):
                ingredient = meal.get(f'strIngredient{i}')
                measure = meal.get(f'strMeasure{i}')
                if ingredient and ingredient.strip():
                    translated_measure = translate_to_russian(measure) if measure else ""
                    translated_ing = translate_to_russian(ingredient)
                    ingredients.append(f"{translated_measure} {translated_ing}".strip())

            instructions = translate_to_russian(meal['strInstructions'])

            return {
                "name": name,
                "image": image_path,
                "instructions": instructions,
                "ingredients": ingredients
            }
    except Exception as e:
        print(f"Ошибка API: {e}")
    return None


def update_recipe_of_the_day():
    global recipe_of_the_day, last_updated
    today = datetime.date.today()
    if last_updated != today:
        api_recipe = get_random_recipe_from_api()
        recipe_of_the_day = api_recipe if api_recipe else random.choice(local_recipes)
        last_updated = today


def get_recipe_of_the_day():
    return recipe_of_the_day