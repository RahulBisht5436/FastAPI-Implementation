from pydantic import BaseModel
from typing import List


class WeatherForecast(BaseModel):
    weather: str
    temperature: float
    humidity: float

    wind_speed: float
    wind_direction: str

    wind_gust: float
    wind_gust_direction: str


class GetWeatherOutput(BaseModel):
    city: str

    # Current weather
    current_weather: WeatherForecast

    # Future weather
    future_weather: List[WeatherForecast]