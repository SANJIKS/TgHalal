import re
# import openai
import aiohttp
import sys
sys.path.append('.')

from config import OPENAI_KEY


async def gpt_clear(english_words):
    chat_history = [
        {"role": "system", "content": "Вы - Пользователь"},
        {"role": "user", "content": f"Текст состава продукта: {english_words}\n" \
             "Очистите текст от лишних слов и верните все пищевые ингредиенты в нижнем регистре, переведенные на русский, приведенные к единому числу, в формате 'код-наименование' (если есть код), и не должно быть просто 'кислота', обязательно писать полностью к примеру 'уксусная кислота', но игнорируй приставки по типу 'в/с', но не укорачивай добавки по типу 'желатин из свиной кожи' - такие сразу переписывай например на 'свинина', и впринципе добавки которые сделаны из животных, сразу приравнивай к животным. Запомни, добавка состоит всегда только из одного слова или кода.Если в тексте нет ингредиентов, ваш ответ будет 'False'. Вот пример твоего ответа: 'E120-кармин, соль, сахар, яблочная кислота'."}]

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4-1106-preview",
                "messages": chat_history,
                "temperature": 0.2
            },
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}"
            }
        ) as response:
            response.raise_for_status()
            data = await response.json()

    generated_text = data["choices"][0]["message"]["content"]

    if 'False' in generated_text:
        return False

    components = generated_text.split(',')
    cleaned_components = [component.strip('\'"') for component in components]
    formatted_components = ', '.join(cleaned_components)
    return formatted_components


async def gpt_response_halal():
    gpt_prompt = [
        {"role": "system", "content": "Вы эксперт и знаете многое об Исламе."},
        {"role": "user", "content": "Объясни про Халал продукты, что их разрешено есть. Кратко. Не выдумывай ничего. Максимум 30 символов."}
    ]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4-1106-preview",
                "messages": gpt_prompt,
                "temperature": 0.4
            },
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}"
            }
        ) as response:
            response.raise_for_status()
            data = await response.json()

    return data["choices"][0]["message"]["content"]


async def main():
    english_words = "морковь, соль, вода холодильник, свинина, кармин"
    cleaned_components = await gpt_clear(english_words)
    print("Очищенные компоненты:", cleaned_components)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())