import asyncio
from googletrans import Translator


async def translate_text(text, dest):
    async with Translator() as translator:
        result = await translator.translate(text, dest=dest)
        return result


def translate(text, dest):
    return asyncio.run(translate_text(text, dest))
