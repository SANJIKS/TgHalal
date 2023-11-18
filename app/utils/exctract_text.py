import io, os
from google.cloud import vision
from config import GOOGLE_CREDENTIALS

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS
client = vision.ImageAnnotatorClient()


def image_to_text(file_name: str):
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        image_text = texts[0].description
        image_text = image_text.strip()
        print(image_text)
        return image_text
    else:
        return False