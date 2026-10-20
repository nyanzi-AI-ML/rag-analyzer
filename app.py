## Setup
# Import the necessary Libraries
import os
import uuid
import json

import gradio as gr

from openai import OpenAI

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

from huggingface_hub import CommitScheduler
from pathlib import Path
import threading  # Use threading for locking

import pandas as pd

# Initialise the client
client = OpenAI(
    #organization=['org-9ygUzkyPJVjPXLT8SJPZ5Gpr'],
    #project=['proj_nNIeI2uc25FgwwriShmOt5qi'],
    api_key=os.environ['openAI']
    )




# Define the embedding model and the vectorstore
embedding_model = SentenceTransformerEmbeddings(model_name='thenlper/gte-large')

#Create a Colelction Name
cloud_collection = 'cloud_providers_annual_reports_2023'

#DB location
persisted_vectordb_location = './cloud_db'

# Load the persisted vectorDB
vectorstore_persisted = Chroma(
    collection_name=cloud_collection,
    embedding_function=embedding_model,
    persist_directory=persisted_vectordb_location,
)


# Prepare the retriever
retriever = vectorstore_persisted.as_retriever(
    search_type='similarity',
    search_kwargs={'k': 5}
)
#


# Prepare the logging functionality
log_file = Path("logs/") / f"data_{uuid.uuid4()}.json"
log_folder = log_file.parent

scheduler = CommitScheduler(
    repo_id="logs_nyanzi_reports_qna",
    repo_type="dataset",
    folder_path=log_folder,
    path_in_repo="data",
    every=2
)



qna_system_message = """
You are an assistant to a financial services firm who answers user queries on annual reports.
User input will have the context required by you to answer user questions.
This context will begin with the token: ###Context.
The context contains references to specific portions of a document relevant to the user query.

User questions will begin with the token: ###Question.

Please answer only using the context provided in the input. Do not mention anything about the context in your final answer.

If the answer is not found in the context, respond "I don't know".




"""




# Define the user message template
qna_user_message_template = """
###Context
{context}
###Question
{question}
"""

# Define the predict function that runs when 'Submit' is clicked or when a API request is made
def predict(user_question,company):

    filter = "dataset/"+company+"-10-k-2023.pdf"
    relevant_document_chunks = vectorstore_persisted.similarity_search(user_question, k=5, filter={"source":filter})

    # Create context_for_query
    context_list = [d.page_content + "\n page: " + str(d.metadata['page']) + "\n\n " for d in relevant_document_chunks]
    context_for_query = ". ".join(context_list)

    # Create messages
    messages = [
        {"role": "system", "content": qna_system_message},
        {"role": "user", "content": qna_user_message_template.format(
            context=context_for_query, 
            question=user_question
            )
        }
    ]

    # Get response from the LLM
    try:
        response = client.chat.completions.create(
            model='gpt-4',
            messages=messages,
            temperature=0
        )

        prediction = response.choices[0].message.content.strip()

    except Exception as e:
        prediction = f'Sorry, I encountered the following error: \n {e}'


    # While the prediction is made, log both the inputs and outputs to a local log file
    # While writing to the log file, ensure that the commit scheduler is locked to avoid parallel
    # access

    with scheduler.lock:
        with log_file.open("a") as f:
            f.write(json.dumps(
                {
                    'user_input': user_question,
                    'company': company,
                    'retrieved_context': context_for_query,
                    'model_response': prediction
                }
            ))
            f.write("\n")

    return prediction

# Set-up the Gradio UI
# Add text box and radio button to the interface
# The radio button is used to select the company 10k report in which the context needs to be retrieved.

textbox = gr.Textbox(placeholder="Enter your query here", label = 'User Question', lines=6)
company_name = gr.Radio(["aws", "google", "IBM", "Meta", "msft"], label="Company")

# Create the interface
# For the inputs parameter of Interface provide [textbox,company]

demo = gr.Interface(
    fn=predict,
    inputs=[textbox, company_name],
    outputs="text",
    title="Financial Report Analysis System",
    description="This web API presents an interface to ask questions on 5 cloud service providers' 2023 financial reports",
)


demo.queue()
demo.launch(share=False)