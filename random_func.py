# random_func.py
import random
import datetime
import requests
from PIL import Image
import io
from deep_translator import GoogleTranslator
import re

recipe_of_the_day = None
last_updated = None

UNIT_TRANSLATIONS = {
    'cup': 'стакан',
    'tablespoon': 'столовая ложка',
    'teaspoon': 'чайная ложка',
    'ounce': 'унция',
    'pound': 'фунт',
    'gram': 'грамм',
    'G': 'грамм',
    'g': 'грамм',
    'kilogram': 'килограмм',
    'milliliter': 'миллилитр',
    'liter': 'литр',
    'pinch': 'щепотка',
    'clove': 'зубчик',
    'slice': 'ломтик',
    'piece': 'штука',
    'can': 'банка'
}


def translate_to_russian(text):
    if not text or not isinstance(text, str):
        return text

    if any('\u0400' <= c <= '\u04FF' for c in text):
        return text

    try:
        for eng_unit, ru_unit in UNIT_TRANSLATIONS.items():
            text = re.sub(rf'\b{eng_unit}\b', ru_unit, text, flags=re.IGNORECASE)

        sentences = re.split(r'(?<=[.!?])\s+', text)
        translated_sentences = []

        for sentence in sentences:
            if len(sentence) < 3:
                translated_sentences.append(sentence)
                continue

            try:
                translated = GoogleTranslator(source='auto', target='ru').translate(sentence)
                if translated and translated != sentence:
                    translated_sentences.append(translated)
                else:
                    translated_sentences.append(sentence)
            except Exception:
                translated_sentences.append(sentence)

        return ' '.join(translated_sentences)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text


local_recipes = [
    {
        "name": "Паста Карбонара",
        "image_bytes": None,
        "instructions": "Рецепт классической карбонары (на 4 порции):\n\n"
                        "1. Сварите спагетти в подсоленной воде с оливковым маслом до состояния 'аль денте'.\n"
                        "2. Нарежьте бекон тонкими полосками, чеснок измельчите.\n"
                        "3. Обжарьте бекон с чесноком на сковороде до румяности.\n"
                        "4. Натрите сыр, добавьте горячую воду от спагетти, взбейте желтки и смешайте с сыром.\n"
                        "5. Слейте воду со спагетти, добавьте к ним сырно-яичную смесь и бекон.\n"
                        "6. Перемешайте, приправьте солью и перцем. Подавайте горячим.",
        "ingredients": ["спагетти - 400 г", "бекон - 150 г", "яйца - 4 шт", "сыр Пармезан - 50 г"]
    },
]


def process_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')

        if img.width > 1024 or img.height > 1024:
            img.thumbnail((1024, 1024))

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return output
    except Exception:
        return None


def get_random_recipe_from_api():
    try:
        response = requests.get('https://www.themealdb.com/api/json/v1/1/random.php', timeout=10)
        response.raise_for_status()
        meal = response.json()['meals'][0]

        image_response = requests.get(meal['strMealThumb'], timeout=10)
        image_response.raise_for_status()
        image_bytes = process_image(image_response.content)

        name = meal['strMeal']
        if not any('\u0400' <= c <= '\u04FF' for c in name):  # Если нет кириллицы
            name = translate_to_russian(name)

        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}', '').strip()
            measure = meal.get(f'strMeasure{i}', '').strip()

            if ingredient:
                ing_str = f"{measure} {ingredient}".strip()
                if not any('\u0400' <= c <= '\u04FF' for c in ing_str):
                    ing_str = translate_to_russian(ing_str)
                ingredients.append(ing_str)

        instructions = meal['strInstructions']
        if not any('\u0400' <= c <= '\u04FF' for c in instructions):
            instructions = translate_to_russian(instructions)

        return {
            "name": name,
            "image_bytes": image_bytes,
            "instructions": instructions,
            "ingredients": [ing for ing in ingredients if ing]  # Удаляем пустые
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