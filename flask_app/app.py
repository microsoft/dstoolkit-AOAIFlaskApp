from flask import Flask, flash, request, render_template, send_file
import openai
import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import os, uuid
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import json
from io import StringIO
import sys
base_path = sys.path[0]
from pandas import ExcelWriter
from flask_socketio import SocketIO
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering import models as qna

app = Flask(__name__)
socketio = SocketIO(app)

### KEYVAULT CODE
# keyVaultName = os.environ['KEYVAULT_NAME']
# KVUri = f"https://{keyVaultName}.vault.azure.net"
#
# default_credential = DefaultAzureCredential()
# credential = DefaultAzureCredential()
# client = SecretClient(vault_url=KVUri, credential=credential)
#
# aoai_api_key_secret = "AOAI-API-KEY"
# aoai_api_base_secret = "AOAI-API-BASE"
#
# aoai_api_key = client.get_secret(aoai_api_key_secret)
# aoai_api_base = client.get_secret(aoai_api_base_secret)
#
# openai.api_key = aoai_api_key
# openai.api_base = aoai_api_base
### KEYVAULT CODE

### CHATGPT CODE
#
# kb_endpoint = os.environ['kb_endpoint']
# kb_key = os.environ['kb_key']
# kb_project = os.environ["kb_project"]
#
# def open_ai_US():
#    openai.api_key = os.environ['api_key_us']
#    openai.api_base = os.environ['api_base_us']
#    openai.api_type = "azure"
#    openai.api_version = "2022-12-01"
#
### CHATGPT CODE

def open_ai_EUR():
    openai.api_key = os.environ['api_key']
    openai.api_base = os.environ['api_base']
    openai.api_type = "azure"
    openai.api_version = "2022-12-01"

text_deployment = "test"
codex_deployment = "test-codex"
embeddings_deployment = "test-embeddings"
doc_search_deployment = "test-doc-search"
query_search_deployment = "test-query-search"
# chatgpt_deployment = "chatgpt"

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/text', methods=['GET', 'POST'])
def text():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("text.html", input_base="Conor ranked the highest in his class out of 140 students. He achieved two academic scholarships. He is captain of the school's rugby team, leading them to three championship finals throughout his four years as captain. He is an active member of the school community, participating in fundraisers and extra-curriculars. He would be an asset to your alumni.")

    if request.method == "POST":
        prompt = request.form["input"]
        response = openai_text_summarisation(prompt)

        return render_template("text.html", input_base = prompt, fooResponse=response)

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("classify.html", input_base="Hello, one of the keys on my laptop keyboard broke recently and I'll need a replacement")

    if request.method == "POST":
        inquiry = request.form["text_input"]
        categories = request.form["input"]
        response = openai_text_classification(inquiry, categories)

        return render_template("classify.html", input_base = inquiry, fooResponse=response)

@app.route('/sql', methods=['GET', 'POST'])
def sql():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("sql.html", input_base="Employee(id, name, department_id)&#13;&#10;Department(id, name, address)&#13;&#10;Salary_Payments(id, employee_id, amount, date)&#13;&#10;A query to list the names of the departments which employed more than 10 employees in the last 3 months")

    if request.method == "POST":
        prompt = request.form["input"]
        response = openai_codex_sql(prompt)

        return render_template("sql.html", input_base = prompt, fooResponse=response)
    
@app.route('/python', methods=['GET', 'POST'])
def python():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("python.html", python_input="write python to read in 'data.csv' and create a bar chart using yaxis 'values' and xaxis 'categories' then train a KNN classifier using sklearn library with label as 'categories' and features as 'values' and predict the label of the new data point")
    
    if request.method == "POST":
        prompt = request.form["input"]
        response = openai_codex_py(prompt)

        return render_template("python.html", fooResponse=response, python_input=prompt)

@app.route('/embed', methods=['GET', 'POST'])
def embed():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("embed.html", input_base1 = "Vehicle", input_base2 = "Automobile")

    if request.method == "POST":
        user_input1 = request.form["text1"]
        user_input2 = request.form["text2"]
        response = openai_embeddings(user_input1,user_input2)

        return render_template("embed.html", input_base1 = user_input1, input_base2 = user_input2, fooResponse=response)
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("search.html", input_base="whole wheat pasta")

    if request.method == "POST":
        user_input = request.form["input"]
        response = openai_text_search(user_input)

        return render_template("search.html", input_base=user_input, fooResponse=response)
    
@app.route('/oneshot', methods=['GET', 'POST'])
def oneshot():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("oneshot.html")

    if request.method == "POST":
        user_input = request.form["input"]
        user_input = user_input.replace("\r\n\r\n", "\n\n")
        if 'submit-button1' in request.form:
            response = openai_zero_shot(user_input)
        if 'submit-button2' in request.form:
            response = openai_one_shot(user_input)
        return render_template("oneshot.html", fooResponse=response)
    
@app.route('/synthetic_data', methods=['GET', 'POST'])
def synthetic_data():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("synthetic_data.html", input_base ="Create fake data with 30 rows in csv format with following rules: first and last name seperated by a space, age between 18-100, tax_number which is unique 5 digit number, gender (male, female), uk street number and name, uk post code. First row is the field names: name, age, tax_id, gender, street_name, post_code. No spaces between the rows.")

    if request.method == "POST":
        user_input = request.form["input"]
        user_input = user_input.replace("\r\n\r\n", "\n\n")
        if 'submit-button1' in request.form:
            response = openai_syn_data(user_input)
            if 'download_tick' in request.form:
                dataframe = pd.read_csv(StringIO(response), sep=',')
                dataframe.to_csv(base_path + "/return_data/GeneratedDataDownload.csv", index=False)
                return render_template("synthetic_data.html", download_link_text = "Download Here.", input_base = user_input, fooResponse=response)
        return render_template("synthetic_data.html", input_base = user_input, fooResponse=response)
    
@app.route('/call_centre', methods=['GET', 'POST'])
def call_centre():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("call_centre.html")

    if request.method == "POST":

        functionality = request.form['group1']
        response = transcript_analytics(functionality)

        return render_template("call_centre.html", fooResponse=response)

@app.route('/download_generated_data', methods=['GET', 'POST'])
def download_generated_data():
    open_ai_EUR()
    return send_file(base_path + "/return_data/GeneratedDataDownload.csv", as_attachment=True)

@app.route('/download_transcript',methods=['GET','POST'])
def download_transcript():
    open_ai_EUR()
    return send_file(base_path + "/return_data/transcript.txt", as_attachment=True)

@app.route('/user_stories', methods=['GET', 'POST'])
def user_stories():
    open_ai_EUR()
    if request.method == "GET":
        return render_template("user_stories.html")

    if request.method == "POST":
        user_stories="\n\n# Start of user stories\nAs an Account Holder I want to withdraw cash from an ATM So that I can get money when the bank is closed \nScenario 1: Account has sufficient funds Given the account balance is $100 And the card is valid And the machine contains enough money When the Account Holder requests $20 Then the ATM should dispense $20 And the account balance should be $80 And the card should be returned \nScenario 2: Account has insufficient funds Given the account balance is $10 And the card is valid And the machine contains enough money When the Account Holder requests $20 Then the ATM should not dispense any money And the ATM should say there are insufficient funds And the account balance should be $20 And the card should be returned \nScenario 3: Card has been disabled Given the card is disabled When the Account Holder requests $20 Then the ATM should retain the card And the ATM should say the card has been retained \nScenario 4: The ATM has insufficient funds\n# End of user stories"
        functionality = request.form['group1']
        if functionality == "Technical IT requirements":
            response = openai_tech_req(user_stories)
            return render_template("user_stories.html", fooResponse=response[0], t=response[1], str=response[2])
                
        if functionality == "Data Attributes":
            response = openai_data_attr(user_stories)
            return render_template("user_stories.html", t=response[0], str=response[1])
    
def openai_text_summarisation(user_input):

    response = openai.Completion.create(
        engine=text_deployment,
        prompt="Summarize this into a reference letter:\n\n" + user_input,
        temperature=1,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].text.lstrip()

def openai_codex_sql(user_input):

    response = openai.Completion.create(
        engine=codex_deployment,
        prompt="Postgres SQL tables, with their properties:\n"+user_input+"\nSELECT",
        temperature=0,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["#", ";"]
    )

    text_reponse = ""
    for l in response.choices[0].text.lstrip().splitlines():
        text_reponse += l
        text_reponse += "\n"

    return "SELECT " + text_reponse

def openai_codex_py(user_input):

    response = openai.Completion.create(
        engine=codex_deployment,
        prompt="'" + user_input.replace('"', "'") + "'",
        temperature=0,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["#", ";"]
    )
    
    text_reponse = ""
    for l in response.choices[0].text.lstrip().splitlines():
        text_reponse += l
        text_reponse += "\n"

    x = text_reponse.split("''",1)[-1]
    return x.lstrip()

def openai_embeddings(user_input1, user_input2):

    user_input1 = user_input1.replace("\n", " ")
    user_input2 = user_input2.replace("\n", " ")

    embedding1 = openai.Embedding.create(
        engine=embeddings_deployment, 
        input=[user_input1])["data"][0]["embedding"]

    embedding2 = openai.Embedding.create(
        engine=embeddings_deployment, 
        input=[user_input2])["data"][0]["embedding"]

    response = cosine_similarity(embedding1, embedding2)
    
    return "Cosine similarity score: " + str(response)

def openai_text_search(user_input):

    input_embedding = get_embedding(user_input, engine=query_search_deployment)

    df = pd.read_csv("/flask_app/data/reviews_embedded.csv")
    df["curie_search"] = df.curie_search.apply(eval).apply(np.array)

    df["similarities"] = df.curie_search.apply(lambda x: cosine_similarity(x, input_embedding))

    res = (
        df.sort_values("similarities", ascending=False)
        .head(3)
    )

    response = ""
    i = 1
    for r in res["Text"].values:
        response += str(i)+".\n"
        response += r
        response += "\n\n"
        i+=1
                
    return response

def openai_text_classification(categories, inquiry):

    response = openai.Completion.create(
        engine=text_deployment,
        prompt = "Classify the following inquiry into one of the following categories: ["+ categories +"]\n\ninquiry: " + inquiry + ":\n\nClassified category:",
        temperature=0,
        max_tokens=6,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )

    return response.choices[0].text.lstrip()

def openai_zero_shot(user_input):

    response = openai.Completion.create(
        engine=text_deployment,
        prompt="From the text below, extract the following entities in the following format:\nCompanies: <comma-separated list of companies mentioned>\nPeople & titles: <comma-separated list of people mentioned (with their titles or roles appended in parentheses)>\n\nText:\n\"\"\"\n"+user_input+"\n\"\"\"\nCompanies:",
        temperature=1,
        max_tokens=1252,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###", "\"\"\""]
    )

    return "Companies: "+ response.choices[0].text.lstrip()

def openai_one_shot(user_input):

    response = openai.Completion.create(
        engine=text_deployment,
        prompt="###\nIn March 1981, United States v. AT&T came to trial under Assistant Attorney General William Baxter. AT&T chairman Charles L.Brown thought the company would be gutted. He realized that AT&T would lose and, in December 1981, resumed negotiations with the Justice Department. Reaching an agreement less than a month later, Brown agreed to divestiture-the best and only realistic alternative. AT&T's decision allowed it to retain its research and manufacturing arms. The decree, titled the Modification of Final Judgement, was an adjustment of the Consent Decree of 14 January 1956. Judge Harold H. Greene was given the authority over the modified decree....\n\nIn 1982, the U.S. government announced that AT&T would cease to exist as a monopolistic entity. On 1 January 1984, it was split into seven smaller regional companies, Bell South, Bell Atlantic, NYNEX, American Information Technologies, Southwestern Bell, US West, and Pacific Telesis, to handle regional phone services in the U.S. AT&T retains control of its long distance services, but was no longer protected from competition.\n\nCompanies: AT&T, Bell South, Bell Atlantic, NYNEX, American Information Technologies, Southwestern Bell, US West, Pacific Telesis\nPeople & titles: William Baxter (Assistant Attorney General), Charles L. Brown (AT&T chairman), Harold H. Greene (Judge)\n###\nFrom the text below, extract the following entities in the following format:\nCompanies: <comma-separated list of companies mentioned>\nPeople & titles: <comma-separated list of people mentioned (with their titles or roles appended in parentheses)>\n\nText:\n\"\"\"\n"+user_input+"\n\"\"\"\nCompanies:",
        temperature=1,
        max_tokens=1252,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###", "\"\"\""]
    )

    return "Companies: "+ response.choices[0].text.lstrip()

def openai_syn_data(user_input):

    response = openai.Completion.create(
        engine=text_deployment,
        prompt=user_input,
        temperature=1,
        max_tokens=2500,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###", "\"\"\""]
        )
    
    return response.choices[0].text.lstrip()

def prompt_response(prompt):
    response = openai.Completion.create(
        engine=text_deployment,
        prompt = prompt,
        temperature=0,
        max_tokens=2988,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )
    return response

def transcript_analytics(functionality):
    with open(base_path + '/return_data/transcript.txt', 'r') as file:
            data = file.read()
    start_string = "\n\n# Start of transcript"
    end_string = "\n# End of transcript"

    prompt = "Below is the transcript of a conversation between a customer and a customer service call agent. "

    content = start_string + data + end_string

    if functionality == "Convert to standard English":
        prompt = prompt + "Correct this to standard English:"
    elif functionality == "Extract Keywords":
        prompt = prompt + "Extract keywords from this transcript:"
    elif functionality == "Extract Customer Information":
        prompt = prompt + "Extract customer information from this transcript:"
    elif functionality == "Sentiment Analysis":
        prompt = prompt + "Perform aspect based sentiment analysis on the transcript.\n - Provide overall sentiment score between 0 to 5 for the conversation\n- Provide a sentiment polarity score between 0 to 5 for each aspect\n- Summarize the sentiment for each aspect"
    elif functionality == "Summarize Conversation":
        prompt = prompt + "Summarize this conversation:"
    elif functionality == "Order Info":
        prompt = prompt + "Extract order information from this transcript:"
    elif functionality == "Customer Interaction Improvements":
        prompt = prompt + "Determine how this customer interaction could be improved."
    elif functionality == "Process Improvements":
        prompt = prompt + "Determine some improvements to the company's policies and processes that could be made to improve customer experience."
    elif functionality == "Customer Intent":
        prompt = prompt + "Provide the intent of the customer in this interaction."
    elif functionality == "Classify Customer Enquiry":
        prompt = prompt + "Classify this customer interaction into one of the following categories:\nDelivery, Returns & Refunds, Order Issues, Product & Stock, Payments, Technical"
    elif functionality == "Convert to 3rd Person":
        prompt = prompt + "Convert this conversation from first-person to third person."

    response = openai.Completion.create(
        engine=text_deployment,
        prompt = prompt + content,
        temperature=0.2,
        max_tokens=2804,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )
    response = response.choices[0].text.lstrip()

    if functionality == "Classify Customer Enquiry":
        response = "Categories: [Delivery, Returns & Refunds, Order Issues, Product & Stock, Payments, Technical]\n\n" + response

    return response

def openai_tech_req(user_stories):

    req = openai.Completion.create(
        engine=text_deployment,
        prompt="Describe the technical IT requirements defined in these user stories:"+user_stories,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )

    req = req.choices[0].text.lstrip()

    tech_req_numbered = req.replace("Technical IT Requirements:\n\n", "")
    tech_req_numbered = "\n\n# Start of technical IT requirements\n" + tech_req_numbered + "\n# End of technical IT requirements"

    tech_req = req.splitlines()[2:]
    for i in range(0, len(tech_req)):
        tech_req[i] = tech_req[i].replace(str(i+1)+". ", "")
    
    tech_req_nonnumbered = ""
    for i in tech_req:
        tech_req_nonnumbered += i + "\n"
    tech_req_nonnumbered = "\n\n# Start of technical IT requirements\n" + tech_req_nonnumbered + "# End of technical IT requirements"

    moscow_prompt = "The following user stories have the following technical IT requirements. Perform a MOSCOW assessment on these technical requirements. Populate a table with the results of this MOSCOW assessment, with the requirements as the index and each column being a MOSCOW element." + user_stories + tech_req_nonnumbered
 
    moscow_response = openai.Completion.create(
        engine=text_deployment,
        prompt = moscow_prompt,
        temperature=0,
        max_tokens=2379,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=["#"]
    )

    moscow_table = openai.Completion.create(
        engine=text_deployment,
        prompt = "Convert this table to HMTL with borders around each cell:\n\n" + moscow_response.choices[0].text,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )

    table = moscow_table.choices[0].text.lstrip()


    prioritize_prompt = "The following user stories have the following technical IT requirements. A MOSCOW assessment has been performed on them, the results of which are in the table. List the requirements in order of priority as per the MOSCOW assessment results. Explain the reasoning behind this prioritization." + user_stories + tech_req_nonnumbered + "\n\n#MOSCOW assessment table\n" +  moscow_response.choices[0].text

    rank_list = openai.Completion.create(
        engine=text_deployment,
        prompt = prioritize_prompt,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=['#']
    )
    rank_list = rank_list.choices[0].text.lstrip()

    res = []
    res.append(req)
    res.append(table)
    res.append(rank_list)

    return res

def openai_data_attr(user_stories):

    data_attr = openai.Completion.create(
        engine=text_deployment,
        prompt="Extract all data points required to execute the following user stories.\n\n" + user_stories + "\n\nData Attribute | Description | Data Format",
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )

    data = openai.Completion.create(
        engine=text_deployment,
        prompt = "Extract all data attributes from this table:\n\n" + data_attr.choices[0].text,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )

    data_attributes = data.choices[0].text.strip().splitlines()
    data_attributes = data_attributes[1:]
    for i in range(0, len(data_attributes)):
        data_attributes[i] = data_attributes[i].replace("- ", "")
        data_attributes[i] = data_attributes[i].rstrip()

    data_attributes_str = " "
    for x in data_attributes:
        data_attributes_str = data_attributes_str + "\'" + x + "\',"
    data_attributes_str = data_attributes_str[:-1]

    data_attr_table = openai.Completion.create(
        engine=text_deployment,
        prompt = "Convert this table to HMTL with borders around each cell:\n\n" + data_attr.choices[0].text,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=None
    )

    python_script = openai.Completion.create(
        engine=codex_deployment,
        prompt="# Create a python class called 'ATMDataset' that initializes the following data attributes as variables using regular Python naming conventions in lowercase:" + data_attributes_str + "and returns them all in a string.\n\n",
        temperature=0.2,
        max_tokens=4152,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        best_of=1,
        stop=["#"]
    )

    res = []
    res.append(data_attr_table.choices[0].text.lstrip())
    res.append("\nPython Script:\n\n" + python_script.choices[0].text.lstrip())

    return res

if __name__ == '__main__':
    app.run()