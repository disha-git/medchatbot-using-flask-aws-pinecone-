import os
from dotenv import load_dotenv

from src.medical_chatbot.helper import (
    load_pdf_file,
    filter_to_minimal_docs,
    text_split,
    download_embeddings
)

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore


# -------------------- LOAD ENV --------------------
load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


# -------------------- STEP 1: LOAD DATA --------------------
print("📄 Loading PDFs...")
extracted_data = load_pdf_file(data="data/")
print(f"✅ Loaded {len(extracted_data)} documents")


# -------------------- STEP 2: FILTER --------------------
print("🧹 Filtering documents...")
filter_data = filter_to_minimal_docs(extracted_data)


# -------------------- STEP 3: SPLIT --------------------
print("✂️ Splitting into chunks...")
text_chunks = text_split(filter_data)
print(f"✅ Created {len(text_chunks)} chunks")


# -------------------- STEP 4: EMBEDDINGS --------------------
print("🧠 Creating embeddings...")
embeddings = download_embeddings()


# -------------------- STEP 5: PINECONE --------------------
print("🌲 Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medical-chatbot"

# FIXED index check
existing_indexes = [index.name for index in pc.list_indexes()]

if index_name not in existing_indexes:
    print("⚙️ Creating new index...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
else:
    print("ℹ️ Index already exists")


# -------------------- STEP 6: STORE --------------------
print(f"📦 Uploading {len(text_chunks)} chunks to Pinecone... (this may take time ⏳)")

docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    embedding=embeddings,
    index_name=index_name
)

print("✅ SUCCESS: All documents embedded and stored in Pinecone!")