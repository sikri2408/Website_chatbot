<h1>Websites_chatbot</h1>

<h2>Table of Contents</h2>
<ul>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#api-hosting">API Hosting</a></li>
</ul>

<h2 id="overview">Overview</h2>
<p>Websites_chatbot is a Retrieval-Augmented Generation (RAG) system that answers questions using content from specified websites. It retrieves, stores, and generates responses from trusted sources, with a REST API, citation mechanism, and a basic authentication and Streamlit based UI for secure, user-friendly access.</p>

<h2 id="getting-started">Getting Started</h2>
<p>To set up and run this project, follow these steps:</p>
<ol>
    <li>Clone this repository.</li>
    <li>Set up a virtual environment with Python 3.12.7.</li>
    <li>Install dependencies from <code>requirements.txt</code>.</li>
    <li>Configure environment variables in the <code>.env</code> file.</li>
</ol>

<h2 id="installation">Installation</h2>

<h3>Step 1: Clone the Repository</h3>
<pre><code>git clone https://github.com/sikri2408/Website_chatbot.git;
cd Website_chatbot;
</code></pre>

<h3>Step 2: Set Up a Virtual Environment</h3>
<p>It is recommended to use a Conda environment. Follow these steps to create and activate the environment:</p>
<pre><code>conda create -n &lt;env-name&gt; python=3.12.7
conda activate &lt;env-name&gt;
</code></pre>

<h3>Step 3: Install Requirements</h3>
<p>Install the necessary packages from <code>requirements.txt</code>:</p>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>Step 4: Configure Environment Variables</h3>
<p>Replace <code>OPEN_AI_KEY</code> in the <code>.env</code> file with your actual OpenAI API key.</p>


<h2 id="usage">Usage</h2>
<h3>Python Code Example</h3>

<pre><code>import requests
from config import API_CLIENT_ID, API_KEY

API_URL = "https://mko0y480af.execute-api.ap-south-1.amazonaws.com/Dev/api/v1/"
headers = {"X-Client-ID": API_CLIENT_ID, "X-API-Key": API_KEY}

## CHAT
endpoint = "chat"
chat_history = [{"content": "What would you like to know?", "role": "assistant"}]
chat_input = {'query': "What is Term-based retrieval?", "chat_history": chat_history}

response = requests.post(API_URL + endpoint, json=chat_input, headers=headers)
print(response.json())

## INDEX
new_url = "https://huyenchip.com/2024/07/25/genai-platform.html"
endpoint = 'index'
response = requests.post(url=API_URL + endpoint, json={'url': new_url, 'force_update': False}, headers=headers)
print(response.json())

## STATS
endpoint = "stats"
response = requests.get(API_URL + endpoint, headers=headers)
print(response.json())
</code></pre>

</body>
</html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project README</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1 { color: #333; }
        pre { background-color: #f4f4f4; padding: 15px; border-radius: 5px; border: 1px solid #ddd; }
        code { font-family: Consolas, "Courier New", monospace; }
    </style>
</head>
<body>

<h3>CURL Commands Example</h3>

<pre><code># CHAT Endpoint
curl -X POST "https://mko0y480af.execute-api.ap-south-1.amazonaws.com/Dev/api/v1/chat" \
     -H "Content-Type: application/json" \
     -H "X-Client-ID: YOUR_API_CLIENT_ID" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{
           "query": "What is Term-based retrieval?",
           "chat_history": [{"content": "What would you like to know?", "role": "assistant"}]
         }'

# INDEX Endpoint
curl -X POST "https://mko0y480af.execute-api.ap-south-1.amazonaws.com/Dev/api/v1/index" \
     -H "Content-Type: application/json" \
     -H "X-Client-ID: YOUR_API_CLIENT_ID" \
     -H "X-API-Key: YOUR_API_KEY" \
     -d '{
           "url": "https://huyenchip.com/2024/07/25/genai-platform.html",
           "force_update": false
         }'

# STATS Endpoint
curl -X GET "https://mko0y480af.execute-api.ap-south-1.amazonaws.com/Dev/api/v1/stats" \
     -H "X-Client-ID: YOUR_API_CLIENT_ID" \
     -H "X-API-Key: YOUR_API_KEY"
</code></pre>

</body>
</html>

Here's the HTML code to add to your Readme.md file:

<h2>API Hosting</h2>

<h3>1. Local Machine</h3>
<p>To run the RAG API locally, use the following command with Uvicorn:</p>
<pre><code>uvicorn main:app --host 0.0.0.0 --port 8080</code></pre>
<p>Once running, the API will be accessible locally. The Streamlit interface can also be accessed at:</p>
<pre><code>streamlit run streamlit_ui.py</code></pre>

<h3>2. Cloud Deployment</h3>
<p>The API is also hosted on AWS for easy access without local setup:</p>
<p>API URL: <a href="https://mko0y480af.execute-api.ap-south-1.amazonaws.com/Dev/api/v1/">https://mko0y480af.execute-api.ap-south-1.amazonaws.com/Dev/api/v1/</a></p>
<p>Streamlit UI: <a href="http://13.233.253.251:8501/">http://13.233.253.251:8501/</a></p>
<p>This setup provides flexibility to run and access the API locally or from the cloud, depending on your development and production needs.</p>
