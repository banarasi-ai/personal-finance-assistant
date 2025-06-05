
import gradio as gr
from gradio import Blocks, Textbox, Button, Markdown, Chatbot
from dotenv import load_dotenv
import os
import requests
from http import HTTPStatus


from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from data_model.product_model import ProductPrice, ProductPriceBase
from data_model.transaction_model import Transaction, TransactionBase
import json
import os

# Load environment variables from .env file
load_dotenv()

PRODUCT_PRICE_API_SERVER_URL = os.getenv("PRODUCT_PRICE_API_SERVER_URL", "http://localhost:8000/product_prices/")
EXPENSE_TRANSACTION_API_SERVER_URL = os.getenv("EXPENSE_TRANSACTION_API_SERVER_URL", "http://localhost:8000/transactions/")

def store_product_price_service(product_search_date, product_name, product_price, product_search_url, product_search_vendor, product_additional_info):
    """This function is a placeholder for storing product price information.
    It can be implemented to save the data to a database or any other storage system.
    """
    # Here you can implement the logic to store the product price information
    print(f"Storing product price: {product_search_date}, {product_name}, {product_price}, {product_search_url}, {product_search_vendor}, {product_additional_info}")
    response = requests.post(
        PRODUCT_PRICE_API_SERVER_URL,
        json={
            "product_search_date": product_search_date,
            "product_name": product_name,
            "product_price": product_price,
            "product_search_url": product_search_url,
            "product_search_vendor": product_search_vendor,
            "product_additional_info": product_additional_info
        }
    )
    if response.status_code == 202:
        response_message = "Product price stored successfully."
    else:
        response_message = f"Failed to store product price: {response.status_code}, {response.text}"
    return {
        "response_message": response_message
    }

def store_expense_transaction_service(transaction_date, amount, vendor_name, category, transaction_additional_info):
    """This function is a placeholder for storing product price information.
    It can be implemented to save the data to a database or any other storage system.
    """
    # Here you can implement the logic to store the product price information
    print(f"Storing expense transaction: {transaction_date}, {amount}, {vendor_name}, {category}, {transaction_additional_info}")
    response = requests.post(
        EXPENSE_TRANSACTION_API_SERVER_URL,
        json={
            "transaction_date": transaction_date,
            "amount": amount,
            "vendor_name": vendor_name,
            "category": category,
            "transaction_additional_info": transaction_additional_info
        }
    )
    
    if response.status_code == HTTPStatus.ACCEPTED:
        response_message = "Expense transaction stored successfully."
    else:
        response_message = f"Failed to store expense transaction: {response.status_code}, {response.text}"
    return {
        "response_message": response_message
    }
    
    
search = TavilySearchResults(max_results=5)

# model = ChatAnthropic(model_name="claude-3-sonnet-20240229")
model = ChatOpenAI(model_name="gpt-4.1-mini")
# model = ChatOllama(model="deepseek-r1:8b", temperature=0.1, max_tokens=10000) #this gave error below:
#ollama._types.ResponseError: registry.ollama.ai/library/deepseek-r1:8b does not support tools (status code: 400)

# model = ChatOllama(model="gemma3:4b", temperature=0.1, max_tokens=10000)#this gave error below:
#ollama._types.ResponseError: registry.ollama.ai/library/gemma3:4b does not support tools (status code: 400)

#https://github.com/ollama/ollama/issues/6704
# model = ChatOllama(model="hf.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF:latest", temperature=0.1, max_tokens=10000)


def agent_call(user_query:str):
    """This function initializes a web search agent using LangChain and Ollama.
    It sets up the agent with a memory saver and a search tool, allowing it to respond to user queries about product prices or expenses.
    """
    
    # Create the agent
    memory = MemorySaver()

    tools = [search, store_product_price_service, store_expense_transaction_service]
    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    # Use the agent
    config = {"configurable": {"thread_id": "main_agent_thread_1"}}

    # Uncomment the following lines to stream the agent's response
    # for step in agent_executor.stream(
    #     {"messages": [HumanMessage(content="what is the price of Google Pixel 8a?")]},
    #     config,
    #     stream_mode="values",
    # ):
    #     step["messages"][-1].pretty_print()
    #sample user query: what is the price of Google Pixel 8a? Give me the response in JSON format with keys: 'price', 'currency', 'url, 'source'
    system_message = f"""You are a personal finance assistant. You provide assistance in only 2 types of user requests:
    1) tracking product prices
    2) tracking expenses.
    For any user query on product prices, you will follow the below steps:
    Step 1) search for product prices in all popular online stores and return all the findings with following keys as a list: 
    'product_search_date', 'product_name', 'product_price', 'product_search_url', 'product_search_vendor', 'product_additional_info'.
    Even if the user asks for 'price', search 'all the prices' available online and return them as a list in the response.
    If the information is not available, return the same format with null values.
    Ensure the data type of each key is as per the {ProductPriceBase.model_fields}.
    Use current system date and time as the 'product_search_date'.
    Step 2) From the list of prices for a product from Step 1, store the product price information using the function store_product_price_service. 
    For each of the price information, ensure the data type of each parameter you pass to the function is as per the {ProductPriceBase.model_fields}.
    
    For any user query on expenses, you will follow the below steps:
    Store the expense transaction using the function store_expense_transaction_service.
    Ensure the data type of each parameter you pass to the function is as per the {TransactionBase.model_fields}.
    If the user does not provide transaction_date, use the current system date and time as the 'transaction_date'.
    If the user does not provide vendor_name, use 'unknown' as the 'vendor_name'.
    
    For any other type of user query, you will respond with a message saying "I can only help you with product prices and expenses tracking. Please ask me about product prices or expenses.".
    """
    query = {"messages": [SystemMessage(content=system_message), HumanMessage(content=f"{user_query}")]}
    response = agent_executor.invoke(query, config)
    print(f"Response:\n{response}")
    return response["messages"][-1].content


start_window = gr.Interface(fn=agent_call,
    inputs=[Textbox(label="User Query", placeholder="Ask about product prices or expenses...",)],
    #,audio := gr.Audio(sources="microphone", type="filepath", label="Speak your query")
    outputs="text",
    title="Personal Finance Assistant",
    description="Ask the agent about product prices or expenses to track.",
)


if __name__ == "__main__":
    start_window.launch(server_name="0.0.0.0", server_port=7860, mcp_server=True)

    # sample stand alone usage:
    # llm_response = agent_call("what is the price of Google Pixel 8a?")
    # print(f"LLM Response: {llm_response}")
    # llm_response = agent_call("Track my expense today. I spent 125$ for category Food at Buthi Foods. The lunch was delicious.")
    # print(f"LLM Response: {llm_response}")