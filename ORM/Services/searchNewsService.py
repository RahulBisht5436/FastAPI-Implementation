
from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from Services.modelsServices import NewsArticle
from langchain_core.prompts import PromptTemplate
import dotenv

dotenv.load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = PromptTemplate(
    template="""
    You are a helpful assistant that can search for news articles.
    You will be given a news_query and you need to search for news articles that match the news_query.
    You need to return the news articles in a list of dictionaries.
    Each dictionary should contain the title, url, and summary of the news article.
    """,
    input_variables=["news_query"]
)


structured_llm = llm.with_structured_output(NewsArticle)

chain = prompt | structured_llm 

def search_news(news_query: str):
    response = chain.invoke({"news_query": news_query})
    return response.model_dump_json()

if __name__ == "__main__":
    print(search_news("What is the latest news about the stock market?"))
    