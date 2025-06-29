import requests
import json
from pprint import pprint

from requests import Response


class DogImage:
    DOG_URL = "https://dog.ceo/api"
    YDX_UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    YDX_FOLDER_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, breed, ydx_token):
        self.breed = breed
        self.ydx_token = ydx_token
        self.results = []

    def sub_breeds(self):
        """Поиск подпород"""
        url = f"{self.DOG_URL}/breed/{self.breed}/list"
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            print(f"Ошибка при получении подпород: {response.status_code}")
        return data.get("message")

    def image_urls(self):
        """Получение URL для породы и всех подпород"""
        image_urls_list = []
        sub_breeds = self.sub_breeds()
        if sub_breeds:
            for sub_breed in sub_breeds:
                url = f"{self.DOG_URL}/breed/{self.breed}/{sub_breed}/images/random"
                response = requests.get(url)
                data = response.json()
                if response.status_code != 200:
                    print(f"Ошибка загрузки картинки для {sub_breed}")
                else:
                    image_urls_list.append(data["message"])
        else:
            url = f"{self.DOG_URL}/breed/{self.breed}/images/random"
            response = requests.get(url)
            data = response.json()
            if response.status_code != 200:
                print(f"Ошибка загрузки картинки для породы")
            else:
                image_urls_list.append(data["message"])
        return image_urls_list

    def create_ydx_folder(self):
        """Создание папки в Я.диске"""
        headers = {
            "Authorization": f"OAuth {self.ydx_token}",
            "Content-Type": "application/json"
        }
        params = {
            "path": f"/{self.breed}",
            "overwrite": "true"
        }

        response = requests.put(self.YDX_FOLDER_URL, headers=headers, params=params)

        if response.status_code == 201:
            print(f"Папка {self.breed} создана")
            return True
        elif response.status_code == 409:
            print(f"Папка {self.breed} уже существует")
            return True
        else:
            print(f"Ошибка при создании папки: {response.status_code} - {response.text}")
            return False

    def upload_images_to_ydx(self, im_url):
        """Загрузка в Я.диск изображений"""
        file_name = im_url.split("/")[-1]
        save_name = f"{self.breed}_{file_name}"

        # запрос url для загрузки
        headers = {
            "Authorization": f"OAuth {self.ydx_token}"
        }
        params = {
            "path": f"/{self.breed}/{save_name}",
            "url": im_url
        }
        response = requests.post(self.YDX_UPLOAD_URL, headers=headers, params=params)

        # сохраняем информацию о файле
        file_info = {
            "file_name": save_name,
            "status": "uploaded"
        }
        self.results.append(file_info)
        return file_info

    def save_result_json(self):
        """Сохраняем результат в формате json"""
        file = f"{self.breed}_results.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False)

        print("Успех")

    def start(self):
        """Основной метод"""
        # создаем папку
        if not self.create_ydx_folder():
            return print("Оштбка создания папки на Я.диске")

        # получаем url
        im_urls = self.image_urls()
        if not im_urls:
            return print("Ошибка в получении URL изображений")

        # загружаем url
        for url in im_urls:
            self.upload_images_to_ydx(url)

        # сохраняем результаты
        self.save_result_json()
        print("загружено в json")


if __name__ == '__main__':
    ydx_token = "y0__xCf1JaNCBjx0jgg9JGY1xMwnoe7oQiP0mZWah5_aI3ZaR7yclOJ1c57yw"
    breed = "spaniel"
    run = DogImage(breed, ydx_token)
    run.start()
