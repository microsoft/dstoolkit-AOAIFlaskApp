# Project

# Introduction 
This repo supplements the Azure OpenAI one-pager by providing code examples of some of the functionalities of OpenAI e.g. text summarisation, NLP to code, text classification, text similarity, document search and more. Coming soon: ChatGPT, and Change Summary use cases.

# Getting Started
1.	create a virtual environment locally
2.  pip install -r .\requirements.txt
3.	replace OpenAI API key with your own (when running locally)

# Build and Test
Run the app.py and load the website in your browser.
There are 10 pages, each has sample input pre-loaded into the input forms. Sample input & corresponding output can be seen in samples.txt.
1.  Call Centre Analytics uses Azure Speech to Text Service and OpenAI's GPT-3 model to perform analytics.
2.  NLP to SQL - uses OpenAI's codex model to transform natural language to an SQL query.
3.  NLP to Python - uses OpenAI's codex model to tranform natural language to Python.
4.  Synthetic Data Generation - Uses GPT-3's ability to follow natural language to create synthetic data.
5.  User Stories - uses OpenAI's GPT-3 model to capture the IT requirements and main data attributes required by a technical system that encapsulates various user scenarios.
6.  Text Generation -  Uses GPT-3's ability to follow natural language to create text.
7.  Classify Text -  GPT-3 classifies text into one of multiple categories provided by the user.
8.  Similarity Embedding - compares two pieces of text by transforming each into an embedding vector & using cosine similarity to generate a similarity score.
9.  Text Search - creates embeddings for a set of Amazon food reviews (already done - just loaded into memory). compares these embeddings to the embedded user input and returns the top 3 reviews most similar to what the user asked.
10. Entity extraction - demonstrating zero-shot vs one-shot learning. An article is input and the names of companies as well as the names of people & their titles are extracted and returned to the user. Results should show improved accuracy with one-shot learning over zero-shot.

Coming soon: ChatGPT, and Change Summary use cases.

# Contribute
Please reach out to clodaghlynch@microsoft.com, or henrytaylor@microsoft.com, for any questions, suggestions, or improvements. Thank you!

# Resources
https://microsofteur-my.sharepoint.com/:o:/g/personal/clodaghlynch_microsoft_com/Eg7NwxxSiBpDmyFOqlNmekIBcO_G6-_kG7SbOV7Y7pJIdg 

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
