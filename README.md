# Install python 3.12
brew install python@3.12       

# Setup virtual environment
python3 -m venv .venv                                                                                        
source .venv/bin/activate

# Install packages
pip install unique_sdk
pip install flask
pip install requests
pip install python-dotenv

# Save requirements
pip freeze > requirements.txt

-------------------------------

## ngrok
# ngrok install
brew install ngrok

# ngrok authentification
ngrok config add-authtoken XXXXXXXXX

# get ngrok forwarding http address (new address when ngrok is restartet)
ngrok http --domain fabian-unique.ngrok.dev 5001

-------------------------------

## app file
create an app.py file in the project folder

-------------------------------

## Flask
# create flask env file with app location
file: .flaskenv
content: FLASK_APP=sdk_demo_project/app.py

# run flask app (with port 5001 & debugger active)
flask run --port 5001 --debug

-------------------------------


## Question
# General
- Module selection extracts also language. Where can I get this parameter? Also in event?

# Modules
- Are multi chat interactions possible? E.g. one information is missing and modules asks for this. Staying within the module for multiple interactions


# Feedback
- API call for hybrid search returns raw sources. maybe we need once a simplified version that returns merged sources 

# Streaming
- How is streaming possible?

# Search
There are currently 3 search types:
- VECTOR: vector search
- COMBINED: vector search combined with fulltext search
- FULLTEXT: Currently, there is no API allowing to the only the fulltext search results --> has to be done

# Chat completion
- model names are our own unique convention (e.g. AZURE_GPT_4_0613). Should we use OpenAI naming? Or add the naming convention to the documentation

# References
- post processing of [source1] --> <sup1>
- where are we doing this? Relevant for displaying sources
- How to append/display references?


# Things to discuss
- Is a webhock listening to all chat messages from all assistants? Or can we limit it to one/several assistants? Is this handled with the APP-ID? If not, this might be a potential data breach. I can see what other departments are asking.