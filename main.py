import os
from dotenv import load_dotenv
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from unstructured.partition.pdf import partition_pdf
from langchain_core.documents import Document

load_dotenv()

# Environment configs
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')
OPENROUTER_API_KEY = os.getenv('API_KEY')
MODEL = os.getenv('MODEL_NAME')
OPENROUTER_URL = os.getenv('BASE_URL')

# Use relative paths for cloud compatibility
BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "data" / "policies"
INDEX_PATH = BASE_DIR / "data" / "faiss_index"

def extract_documents_from_folder(folder_path):
    all_docs = []

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            elements = partition_pdf(filename=pdf_path, strategy="auto", infer_table_structure=True)
            content = "\n".join(str(e) for e in elements if e.text)
            document = Document(page_content=content, metadata={"source": filename})
            all_docs.append(document)

    return all_docs



def split_documents_to_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_documents(documents)


def create_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={'normalize_embeddings': True},
        model_kwargs={'device': 'cpu'}
    )


def create_or_load_vectorstore():
    embeddings = create_embeddings()
    if os.path.exists(INDEX_PATH):
        print("Loading existing FAISS index...")
        return FAISS.load_local(INDEX_PATH, embeddings=embeddings, allow_dangerous_deserialization=True)
    else:
        print("Creating new FAISS index...")
        raw_docs = extract_documents_from_folder(FILE_PATH)
        split_docs = split_documents_to_chunks(raw_docs)
        vectorstore = FAISS.from_documents(split_docs, embedding=embeddings)
        vectorstore.save_local(INDEX_PATH)
        return vectorstore


def build_prompt(query, context):
    return f"""
        You are an expert IRCTC assistant.

        For refund or cancellation related queries use the rules below, analyze the timing and class of ticket and clearly calculate the refund.
        If percentage and flat fee are both mentioned, choose the greater as per IRCTC policy.

        Format your answer as:
        Refund = [Ticket Price] - [Cancellation Charges] = [Refund Amount]

        If the query is not available in context, answer the question using your best understanding using external knowledge base. If unsure, mention that user should verify on [IRCTC](https://www.irctc.co.in/).

        If you are totally unable to provide answer say:
        "Sorry, visit https://www.irctc.co.in/ or raise a query at https://equery.irctc.co.in/."

        Context:
        {context}

        Question: {query}
        Answer:
        """


def get_answer(query, vectorstore):
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 8})
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = build_prompt(query, context)

    llm = ChatOpenAI(
        api_key=OPENROUTER_API_KEY,
        model_name=MODEL,
        base_url=OPENROUTER_URL,
        temperature=0.3
    )

    response = llm.invoke(prompt)
    return response.content