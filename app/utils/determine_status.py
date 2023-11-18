import pandas as pd
import asyncio

import sys
sys.path.append('.')
from config import CSV_PATH

async def determine_verdict(words):
    df = pd.read_csv(CSV_PATH)
    
    relevant_words = [word.lower() for word in words if len(word) > 3]
    statuses = []
    words_with_status = {}

    async def get_status(word, df):
        interested_statuses = ['харам', 'машбух', 'макрух']
        unique_statuses = set()

        for _, row in df.iterrows():
            if isinstance(row[0], str) and isinstance(row[1], str):
                if word in row[0].lower():
                    for status in interested_statuses:
                        if status.lower() in row[1].lower():
                            unique_statuses.add(status)

        return list(unique_statuses) if unique_statuses else None

    async def process_word(word):
        words_split = word.split("-")
        for split_word in words_split:
            split_word = split_word.strip()
            status_list = await get_status(split_word, df)
            print(status_list, '\n')
            if status_list:
                for status in status_list:
                    statuses.append(status)
                    words_with_status[split_word] = status

    await asyncio.gather(*(process_word(word) for word in relevant_words))

    verdicts_order = ['харам', 'макрух', 'машбух', 'халяль']
    for verdict in verdicts_order:
        if verdict in statuses:
            final_verdict = verdict
            break
    else:
        final_verdict = 'халяль'

    print(words_with_status)
    return [final_verdict, words_with_status]

async def main():
    words = ['баранина', 'e120', 'свинина']
    result = await determine_verdict(words)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())