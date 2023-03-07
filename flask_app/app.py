from flask import Flask, flash, request, render_template
import openai
import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)
# openai.api_key = os.environ['OPENAI_APIKEY']
openai.api_key = ""
openai.api_base = ""
openai.api_type = ""
openai.api_version = ""

text_deployment = "test"
codex_deployment = "test-codex"
embeddings_deployment = "test-embeddings"
doc_search_deployment = "test-doc-search"
query_search_deployment = "test-query-search"

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/text', methods=['GET', 'POST'])
def text():
    if request.method == "GET":
        return render_template("text.html")

    if request.method == "POST":
        prompt = request.form["input"]
        response = openai_text_summarisation(prompt)

        return render_template("text.html", fooResponse=response)

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == "GET":
        return render_template("classify.html")

    if request.method == "POST":
        inquiry = request.form["text_input"]
        categories = request.form["input"]
        response = openai_text_classification(inquiry, categories)

        return render_template("classify.html", fooResponse=response)

@app.route('/sql', methods=['GET', 'POST'])
def sql():
    if request.method == "GET":
        return render_template("sql.html")

    if request.method == "POST":
        prompt = request.form["input"]
        response = openai_codex(prompt)

        return render_template("sql.html", fooResponse=response)

@app.route('/embed', methods=['GET', 'POST'])
def embed():
    if request.method == "GET":
        return render_template("embed.html")

    if request.method == "POST":
        user_input1 = request.form["text1"]
        user_input2 = request.form["text2"]
        response = openai_embeddings(user_input1,user_input2)

        return render_template("embed.html", fooResponse=response)
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "GET":
        return render_template("search.html")

    if request.method == "POST":
        user_input = request.form["input"]
        response = openai_text_search(user_input)

        return render_template("search.html", fooResponse=response)
    
@app.route('/oneshot', methods=['GET', 'POST'])
def oneshot():
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

    return response.choices[0].text

def openai_codex(user_input):

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
    for l in response.choices[0].text.splitlines():
        text_reponse += l
        text_reponse += "\n"

    return "SELECT " + text_reponse

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

    df = pd.read_csv("flask_app/data/reviews_embedded.csv")
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

    return response.choices[0].text

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

    return "Companies:"+ response.choices[0].text

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

    return "Companies:"+ response.choices[0].text

if __name__ == '__main__':
    app.run()