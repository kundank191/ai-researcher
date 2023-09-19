import os
import logging
import json
from bs4 import BeautifulSoup

from langchain import PromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import SystemMessage
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

import requests
import streamlit as st

# Setup logging
log_format = '%(asctime)s - %(levelname)s - %(filename)s: %(message)s'
logging.basicConfig(filename='logs/info.log', level=logging.INFO, format=log_format)

browserless_api_key = os.getenv('BROWSERLESS_API_KEY')
serper_api_key = os.getenv('SERP_API_KEY')

# create a search tool to get results from google
def search(query):

    url = "https://google.serper.dev/search"

    payload = json.dumps({
        'q' : query
    })

    headers = {
        'X-API-KEY' : serper_api_key,
        'Content-Type' : 'application/json'
    }

    response = requests.request(
        "POST", 
        url, 
        headers = headers, 
        data = payload
    )

    logging.info(response.text)

    return response.text

# Scrape website tool
def scrape_website(objective: str, url: str):
    """
        Args
            objective : summarization will be done on the basis of this objective
            url : The url from where the data will be taken
    """
    
    logging.info("Scraping Website ...")

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type' : 'application/json'
    }

    data = {
        "url" : url
    }

    # convert to json
    data_json = json.dumps(data)

    # Send the post request
    post_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
    
    response = requests.post(
        post_url, 
        headers = headers,
        data = data_json
    )

    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        logging.info("Content from website ", text )

        if len(text) > 10000:
            output = summarize(objective, text)
            return output
        else:
            return text
    else:
        logging.info(f"Http request failed with status code : {response.status_code}, details : {response.text}")

# Sumamrize content
def summarize(objective, content):
    llm = ChatOpenAI(temperature = 0, model = "gpt-3.5-turbo-16k-0613")

    text_splitter = RecursiveCharacterTextSplitter(
        separators = ["\n\n", "\n"],
        chunk_size = 10000,
        chunk_overlap = 500
    )

    docs = text_splitter.create_documents([content])

    map_prompt = """
    Write a summary of teh following text for {objective}:
    "{text}"
    SUMMARY:
    """

    map_prompt_template = PromptTemplate(
        template = map_prompt,
        input_variables = ["text","objective"]
    )

    summary_chain = load_summarize_chain(
        llm = llm,
        chain_type = "map_reduce",
        map_prompt = map_prompt_template,
        combine_prompt = map_prompt_template,
        verbose = True
    )

    ouput = summary_chain.run(
        input_documents = docs,
        objective = objective
    )

    return ouput
