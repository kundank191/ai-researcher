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
from dotenv import load_dotenv

import requests
import streamlit as st
from typing import Type

# intialize the environment variables
load_dotenv()

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

class ScrapeWebsiteInput(BaseModel):
    """Inputs for scrape_website"""
    objective : str = Field(description = "The objective and task that users give to the agent")
    url : str = Field(description = "The URL of the website to be scraped")

class ScrapeWebsiteTool(BaseModel):
    """This tool will run the scrape website and return the results"""

    name : str = "scrape_website"
    description : str = "useful when you need to get the data from a website url; passing both the url and the objective to the function; Donot Make up any url; Donot make up any url"
    args_schema: Type[BaseModel] = ScrapeWebsiteInput

    def _run(self, objective : str, url : str):
        return scrape_website(objective, url)

    def _arun(sel, url: str):
        raise NotImplementedError("Not Implemented yet")
    
# Create a Langchain Agents with the tools above
tools = [
    Tool(
        name = "Search",
        func = search,
        description = "useful for when you need to answer questions about current events, data. You should ask targeted questions"
    ),
    ScrapeWebsiteTool()
]

system_message = SystemMessage(
    content = """ You are a world class researcher, who can do detailed research on any topic and produce facts based results;
    you donot make things up, you will try as hard as possible to gather facts and data to back up the research

    Please make sure you complete the objective with the following rules
    1/ You should do enough research to gather as much information as possible about the objective
    2/ If there are url of the relevant links and articles, you will scrape it to gather more information
    3/ After scraping and search, you should think "is there any new things I should search or scrape based on the data I collected to increase research quality?" if the answer is yes, continue; But dont do this more than 3 iterations
    4/ You should not make things up, you should only write facts and data that you have gathered
    5/ In the final outpul, you should include all the reference data and links to back up your research; You should include all references
    6/ In the final outpul, you should include all the reference data and links to back up your research; You should include all references

    """
)

agent_kwargs = {
    "extra_prompt_messages" : [MessagesPlaceholder(variable_name = "memory")],
    "system_message" : system_message
}

llm = ChatOpenAI(
    temperature = 0,
    model = "gpt-3.5-turbo-16k-0613"
)

memory = ConversationSummaryBufferMemory(
    memory_key = "memory",
    return_messages = True,
    llm = llm,
    max_token_limit = 1000
)

agent = initialize_agent(
    tools,
    llm,
    agent = AgentType.OPENAI_FUNCTIONS,
    verbose = True,
    agent_kwargs = agent_kwargs,
    memory = memory
)

# def User streamlit to create a web app
def main():

    st.set_page_config(
        page_title = "AI Researcher",
        page_icon = ":bird:"
    )

    st.header("AI Researcher :bird:")

    query = st.text_input("Research Goal")

    if query:
        st.write("Doing research for ", query)
        result = agent({"input" : query})
        st.info(result['output'])

if __name__ == '__main__':
    main()