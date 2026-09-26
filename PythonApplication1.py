import urllib.request
import urllib.parse
import json

city = input("Şəhərin adını ingiliscə yaz: ")

# Şəhərin koordinatlarını tapır
search_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode({
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json"
})

with urllib.request.urlopen(search_url) as response:
    location_data = json.loads(response.read().decode())

if "results" not in location_data:
    print("Şəhər tapılmadı.")
else:
    location = location_data["results"][0]

    name = location["name"]
    latitude = location["latitude"]
    longitude = location["longitude"]

    # Hava məlumatını alır
    weather_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
        "timezone": "auto"
    })

    with urllib.request.urlopen(weather_url) as response:
        weather_data = json.loads(response.read().decode())

    weather = weather_data["current"]

    print("\n-------------------------")
    print("Şəhər:", name)
    print("Temperatur:", weather["temperature_2m"], "°C")
    print("Hiss olunan:", weather["apparent_temperature"], "°C")
    print("Rütubət:", weather["relative_humidity_2m"], "%")
    print("Külək:", weather["wind_speed_10m"], "km/saat")
    print("-------------------------")
