import openai
import pandas as pd
import re
from transformers import GPT2TokenizerFast
from openai.embeddings_utils import get_embedding

openai.api_key = ""
openai.api_base = ""
openai.api_type = ""
openai.api_version = ""

doc_search_deployment = "test-doc-search"

df = pd.read_csv("flask_app/data/fine_food_reviews_1k.csv")

def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()
    
    return s

df_reviews = df[['Summary', 'Text']]
df_reviews['Text'] = df_reviews["Text"].apply(lambda x : normalize_text(x))

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
df_reviews['n_tokens'] = df_reviews["Text"].apply(lambda x: len(tokenizer.encode(x)))
df_reviews = df_reviews[df_reviews.n_tokens<2000]

df_reviews['curie_search'] = df_reviews["Text"].apply(lambda x: get_embedding(x, engine=doc_search_deployment))

df_reviews.to_csv("flask_app/data/reviews_embedded.csv")