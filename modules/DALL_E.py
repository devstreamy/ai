import openai, os, requests
from utils.logs import logSystem, stopColor, logError
from modules.other import show_current_datetime
from addon.checkbox import getConfigInfo
openai.api_key = getConfigInfo('main', 'openai_apikey')

def generate_image(prompt):
    try:
        if not os.path.exists("images"):
            os.makedirs("images")

        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        image_name = os.path.basename(image_url)
        image_data = requests.get(image_url).content
        save_path = os.path.join("images", image_name)
        with open(save_path, 'wb') as f:
            f.write(image_data)
        print(logSystem + f"сгенерированный URL изображения: {image_url}" + stopColor + show_current_datetime())
        print(logSystem + f"сгенерированное изображение сохранено: {save_path}" + stopColor + show_current_datetime())
    except Exception as e:
        print(logError + f"произошла ошибка при генерации изображения: {str(e)}" + stopColor + show_current_datetime())