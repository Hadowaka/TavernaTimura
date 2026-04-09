 
import os
import json

page=input("Введите название папки:")
if(os.path.exists(page)):
    print("Ошибка, такая страница уже существует!T")
else:
    os.mkdir(page)

os.chdir(page)

data = {
    "pageId": "timur",
    "title": "TIMUR: Легенда Таверны",
    "rating": {
        "score": 4.6,
        "metacritic": "88/100"
    },
    "screenshots": [
        {"id": 1, "url": "image1.jpg", "alt": "Битва с драконом"},
        {"id": 2, "url": "image2.jpg", "alt": "Таверна"}
    ]
}
page_json = page + ".json"
with open(page_json, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)