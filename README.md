# 🚂 IRCTC Chatbot

A conversational AI assistant powered by RAG (Retrieval-Augmented Generation) to help users understand Indian Railways policies, ticket booking procedures, cancellation rules, and refund policies.

## 🌟 Features

- **Interactive Chat Interface**: Beautiful, responsive chat UI with gradient backgrounds
- **Quick Questions**: Pre-defined common questions for instant answers
- **Real-time Responses**: Fast document retrieval and AI-powered responses
- **Policy Coverage**: Comprehensive coverage of IRCTC policies including:
  - Ticket booking procedures
  - Cancellation and refund rules
  - Baggage allowance guidelines
  - Senior citizen concessions
  - Passenger rights and services

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **Backend**: LangChain for document processing and RAG
- **Vector Database**: FAISS for efficient similarity search
- **Embeddings**: HuggingFace sentence transformers
- **LLM**: OpenAI-compatible API (OpenRouter)
- **Document Processing**: Unstructured for PDF parsing

## 🏃‍♂️ Running the Application

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | OpenRouter/OpenAI API key | Required |
| `BASE_URL` | API base URL | `https://openrouter.ai/api/v1` |
| `MODEL_NAME` | LLM model name | `meta-llama/llama-3.1-8b-instruct:free` |
| `EMBEDDING_MODEL` | HuggingFace embedding model | `sentence-transformers/all-MiniLM-L6-v2` |

### Document Processing

- **Chunk Size**: 800 characters
- **Chunk Overlap**: 100 characters
- **Similarity Search**: Top 8 relevant chunks
- **Supported Formats**: PDF

## 📝 Usage Examples

### Sample Questions:
- "What are the cancellation charges for AC 2-tier tickets?"
- "How can I get a refund for my cancelled ticket?"
- "What is the baggage allowance for passengers?"
- "How do I book tickets online?"
- "What are the senior citizen concession rules?"


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.