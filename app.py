from flask import Flask, render_template, request
from src.medical_chatbot.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.medical_chatbot.prompt import *
import os

# ✅ NEW IMPORTS FOR MEMORY
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory.chat_message_histories import ChatMessageHistory

app = Flask(__name__)

load_dotenv()

# API KEYS
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Embeddings + Vector Store
embeddings = download_embeddings()

index_name = "medical-chatbot"

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

# Retriever
retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# LLM
chatModel = ChatOpenAI(model="gpt-4o")

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# Chains
question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# =========================
# 🧠 MEMORY SETUP
# =========================

store = {}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]

    # ✅ CALL MEMORY-ENABLED CHAIN
    response = conversational_rag_chain.invoke(
        {"input": msg},
        config={"configurable": {"session_id": "user1"}}  # change later for real users
    )

    return str(response["answer"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)