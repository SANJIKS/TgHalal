# import os
from googletrans import Translator
# from config import GOOGLE_CREDENTIALS

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS

translator = Translator()

def translate(text):
    translation = translator.translate(text, dest='ru')
    if translation and translation.text:
        return translation.text
    else:
        return ""

def translate_to_russian(text):
    translation = translator.translate(text, dest='ru')
    if translation and translation.text:
        return translation.text
    else:
        return ""