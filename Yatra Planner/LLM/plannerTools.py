from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from Config.openai_model import openai_model
from Models.plannerModels import GetWeatherOutput


# Prompt template
weather_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a weather information assistant.

        Provide current and future weather information
        for the requested city.

        The response must follow the provided structured
        output schema.
        """
    ),
    (
        "human",
        """
        Get the weather information for {city}.

        Include current weather details:
        - Weather condition
        - Temperature
        - Humidity
        - Wind speed
        - Wind direction
        - Wind gust
        - Wind gust direction

        Also provide future weather predictions including:
        - Weather condition
        - Temperature
        - Humidity
        - Wind speed
        - Wind direction
        - Wind gust
        - Wind gust direction
        """
    ),
])


# Structured LLM
structured_weather_model = openai_model.with_structured_output(
    GetWeatherOutput
)


# Chain
weather_chain = weather_prompt | structured_weather_model


@tool
def get_weather(city: str) -> GetWeatherOutput:
    """
    Get current and future weather details of a city.
    """

    response = weather_chain.invoke({
        "city": city
    })

    return response