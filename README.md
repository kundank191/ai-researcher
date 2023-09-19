# AI-researcher
Enter a Reasearch goal and it will return content with references. This tool is different because it doent makes up URLs or content, it is based on facts and well referenced information. The content is hence authentic and credible.

Try the Tool Here : https://kundan-ai-researcher.streamlit.app/
If you want to learn in detail how the code works then checkout this video : https://www.youtube.com/watch?v=ogQUlS7CkYA&pp=ygUIYWkgamFzb24%3D

# Here are the steps explaining how it works:

1. The AI starts with a google search and filter outs all the relevant results.
2. The AI scrapes all the relevant information from the websites
3. If the AI finds a relevant link inside the website then it will scrape that too
4. After the scraping is complete the AI will ask itself wheter the reaseach work is sufficient or not?
5. If not suffiecient then it will again start from step 1 based on past experience, exploring new links.

# Here are some images of the project

## Main Interface

<img src="https://github.com/kundank191/ai-researcher/assets/26672993/4f424ea1-8505-4f26-b909-ab44c12138a4" width="700" height="550"/>

## Example Query

### Result

<img src="https://github.com/kundank191/ai-researcher/assets/26672993/a17f59ce-f8b5-4f5b-8560-19b744e6a7ca" width="700" height="550"/>

### References in the example

<img src="https://github.com/kundank191/ai-researcher/assets/26672993/81239347-d47e-4ddd-949b-19219d90e9d4" width="700" height="550"/>


## Tech Used in The Project

* langchain : https://www.langchain.com/
* OpenAI API : https://openai.com/blog/openai-api
* serp : https://serper.dev/
* browserless : https://www.browserless.io/

## Setting up the project

* python 3.11.5
* setup .env file
    * OPENAI_API_KEY : https://openai.com/blog/openai-api
    * SERP_API_KEY : https://serper.dev/
    * BROWSERLESS_API_KEY : https://www.browserless.io/
* pip install -r requirements.txt
* streamlit run app.py

## References
* This project was possible due to this youtube video : https://www.youtube.com/watch?v=ogQUlS7CkYA&pp=ygUIYWkgamFzb24%3D
