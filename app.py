import os
import logging
import json
from bs4 import BeautifulSoup
import requests

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

        return text
    else:
        logging.info(f"Http request failed with status code : {response.status_code}, details : {response.text}")

scrape_website(
    objective = "Get Detailed Information", 
    url = "https://medium.com/@aaabulkhair/so-which-ml-algorithm-to-use-d2484239f448"
)
