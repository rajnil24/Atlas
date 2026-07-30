import requests
from pydantic import BaseModel
from backend.tools.base_tools import BaseTool, ToolResult
from backend.config import OPEN_WEATHER_API_KEY


class WeatherInput(BaseModel):
    city: str


class WeatherTool(BaseTool):

    tool_name = "weather"
    tool_description = (
        "Input Schema: <city : string > . Returns current weather , temperature,humidity,wind_speed,time_zone,visibility for a city"   
    )
    input_schema = WeatherInput

    def run(
        self,
        input_data: WeatherInput
    ) -> ToolResult:

        city = input_data.city
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPEN_WEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params
        )

        if response.status_code != 200:
            return ToolResult(
                success=False,
                error=response.text
            )

        data = response.json()

        weather = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "time_zone": data["timezone"],
            "visibility": data["visibility"]
        }

        return ToolResult(
            success=True,
            output=weather
        )