import random
import datetime
import requests
from PIL import Image
import io

recipe_of_the_day = None
last_updated = None

local_recipes = [
    {
        "name": "Pasta Carbonara",
        "image_bytes": None,
        "instructions": "Classic carbonara recipe (for 4 servings):\n\n"
                        "1. Cook spaghetti in salted water with olive oil until al dente.\n"
                        "2. Cut bacon into thin strips, chop garlic.\n"
                        "3. Fry bacon with garlic in a pan until golden brown.\n"
                        "4. Grate cheese, add hot water from spaghetti, beat egg yolks and mix with cheese.\n"
                        "5. Drain spaghetti, add cheese-egg mixture and bacon.\n"
                        "6. Mix well, season with salt and pepper. Serve hot.",
        "ingredients": ["spaghetti - 400g", "bacon - 150g", "eggs - 4", "Parmesan cheese - 50g"]
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

        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}', '').strip()
            measure = meal.get(f'strMeasure{i}', '').strip()
            if ingredient:
                ingredients.append(f"{measure} {ingredient}".strip())

        return {
            "id": meal['idMeal'],  # Добавляем ID рецепта
            "name": meal['strMeal'],
            "image_bytes": image_bytes,
            "instructions": meal['strInstructions'],
            "ingredients": [ing for ing in ingredients if ing]
        }
    except Exception as e:
        print(f"API error: {e}")
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
