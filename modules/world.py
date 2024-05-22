import requests
from modules.speach import speach
from utils.logs import stopColor, logError, logNews
from modules.other import (saveTextfile, 
                           show_current_datetime)
def get_weather(cities):
    try:
        api_key = "db986886bc22744d4dbb14d5af5308f3"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        weather_data = []
        
        for city in cities:
            complete_url = f"{base_url}appid={api_key}&q={city}&units=metric&lang=ru"
            response = requests.get(complete_url)
            data = response.json()
            
            if data["cod"] == 200:
                city_name = data.get("name", "Unknown city") 
                temp = data.get("main", {}).get("temp", "No temperature data")
                description = data.get("weather", [{}])[0].get("description", "No description")
                weather_data.append(f"погода: {temp}, {description} Город: {city_name}")
            else:
                error_message = data.get("message", "No error message")
                weather_data.append((city, f"Error: {error_message}"))
        
        return weather_data
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в получении информации о погоде :: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в получении информации о погоде :: {e}"+stopColor+show_current_datetime())

def getNews():
    try:
        api_key = 'dd6d5795210b4b2abe3f66dbc5c77369'
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'country': 'ru',
            'apiKey': api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            news = response.json()['articles']
            for articles in news:
                saveTextfile('logs.txt', articles['title']+show_current_datetime(), True)
                print(logNews+articles['title']+stopColor+show_current_datetime())
                speach(articles['title'])
                break
        else:
            return logError+"ошибка: Не удалось получить новости"+stopColor+show_current_datetime()()
    except Exception as e:
        saveTextfile('logs.txt',f"ошибка в получении последних новостей :: {e}"+show_current_datetime(), True)
        print(logError+ f"ошибка в получении последних новостей :: {e}"+stopColor+show_current_datetime())
