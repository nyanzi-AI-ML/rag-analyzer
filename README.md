# RAG for Effective Information Retrieval (10-K Report Analysis)

An advanced Retrieval-Augmented Generation (RAG) system built to automate the extraction, summarization, and analysis of annual 10-K reports for major cloud and AI service providers.

---

## 🏢 Business Use Case & Problem Statement

* **Company Background:** A financial technology firm specializing in advanced analytics and insights for investment management and financial planning.
* **The Challenge:** Analysts manage extensive collections of 10-K reports detailing financial performance, risk factors, market trends, and strategic initiatives. Extracting precise information manually is time-consuming and creates a bottleneck for delivering timely client recommendations.
* **The Solution:** Implementation of an automated RAG-based system to drastically enhance the speed and accuracy of investment insights across five major platforms: **Amazon AWS, Google Cloud, Microsoft Azure, Meta AI, and IBM Watson**.

---

## 🚀 Project Objectives

* **Automated Information Extraction:** Streamline the analysis of key 10-K report metrics.
* **Comparative Platform Research:** Evaluate major tech giants on AI acquisitions, R&D capital allocation, ethical AI initiatives, and competitive differentiation.
* **Systematic LLM Evaluation:** Utilize an LLM-as-a-Judge framework to rigorously measure response faithfulness and answer relevance against source chunks.
* **Productivity Enhancement:** Empower financial analysts with a rapid query tool for timely client recommendations.
* **Cloud Deployment:** Deploy an interactive web application on Hugging Face Spaces with automated evaluation and request logging.

---

## 🛠️ Tech Stack Dependencies 
* **Language:** Python 
* **Frameworks:** LangChain, LangChain Community
* **Vector Database:** ChromaDB
* **Embeddings Model:** Hugging Face Sentence Transformers (thenlper/gte-large)   
* **Large Language Model:** OpenAI GPT-4 (used for response generation and LLM-as-a-judge evaluation)   
* **PDF Processing:** PyPDF / PyPDFDirectoryLoader   
* **Interface & Logging:** Gradio, Hugging Face Hub (CommitScheduler)   

---

## 🏛️ System Runtime Architecture (app.py)
This diagram represents the runtime execution flow encapsulated within app.py

```mermaid
graph TD
    subgraph App["app.py (Hugging Face Spaces Runtime)"]
        UI["Gradio User Interface"]
        VS[("ChromaDB Vector Store")]
        LLM["OpenAI GPT-4"]
        LOGGER["CommitScheduler Log Manager"]

        UI -->|"1. User Query & Filters"| VS
        VS -->|"2. Retrieved Context Chunks (k=5)"| LLM
        LLM -->|"3. Grounded Answer"| UI
        UI -->|"4. Async Request Logging"| LOGGER
    end

    LOGGER -->|"Persists qna_logs.json"| HF[("Hugging Face Datasets")]

```
---
## ⚙️ Project Pipeline & Deployment Workflow
This diagram represents the notebook build environment where data ingestion, vector creation, RAG building and LLM-as-a-Judge evaluation happen prior to deployment.
```mermaid
graph LR
    A["Import Libraries"] --> B["Chunk Data"]
    B --> C["Create VectorDb"]
    C --> D["Build RAG"]
    D --> E{"Evaluate"}
    E --> F["App.py"]
    G["Gradio"] --> F

    A --> H["Requirements"]
    C --> I["Persisted VectorDB"]
    
    H --> J["HuggingFace Spaces"]
    I --> J
    F --> J
```
---
## 🧠 The cental role of `app.py`
In the rag-analyzer architecture, `app.py` is the production backbone of the project. While the Jupyter notebook (financial_rag_analysis.ipynb) handles heavy-lifting data ingestion and evaluation offline, `app.py` assumes total runtime responsibility once deployed to Hugging Face Spaces:

1. **Interactive Runtime Orchestration:** Initializes and hosts the Gradio web interface, capturing user queries and financial metadata filters in real-time.
2. **Semantic Retrieval & Generation Loop:** Connects directly to the persisted ChromaDB vector store to execute similarity searches ($k=5$) and feeds the retrieved context chunks into the OpenAI GPT-4 pipeline for grounded, context-aware financial answers.
3. **Production Observability & Logging:** Integrates the `CommitScheduler` utility to asynchronously capture and commit every interaction (user queries, model responses, and session metadata) into an audit trail (qna_logs.json) stored on Hugging Face Datasets.
4. **Self-Contained Deployment Artifact:** Serves as the immutable entrypoint that Hugging Face Spaces automatically detects, executes, and builds using the companion requirements.txt environment.

---

## 🎬 Installation & Local Setup

To run this project locally or within a notebook environment, install the required packages:

```bash
pip install openai==1.23.2 tiktoken==0.6.0 pypdf==4.0.1 langchain==0.1.1 langchain-community==0.0.13 chromadb==0.4.22 sentence-transformers==2.3.1
```

---
## 🎬 Project Pipeline & Workflow

1. **Data Preparation & Chunking:**
   * Loaded 2023 10-K PDF reports for AWS, Google, IBM, Meta, and Microsoft.
   * Split documents using `RecursiveCharacterTextSplitter.from_tiktoken_encoder` with a `chunk_size` of 512 and `chunk_overlap` of 16 using `cl100k_base` encoding.
2. **Vector Database Creation:**
   * Generated dense embeddings using the `thenlper/gte-large` model.
   * Stored document chunks in a persistent Chroma vector collection named `cloud_providers_annual_reports_2023`.
3. **Retrieval-Augmented Generation (RAG):**
   * Performed metadata-filtered similarity searches (`k=5`) targeting specific company filings.
   * Passed retrieved contexts and page references into custom system and user prompt templates.
   * Queried OpenAI GPT-4 with a temperature of `0` to synthesize precise answers.
4. **LLM Evaluation Framework:**
   * Assessed generation quality using an automated LLM rater (`gpt-4`) scored on a scale of 1 to 5:
     * **Groundedness:** Evaluates whether answers are derived strictly from the provided context without hallucinations.
     * **Relevance:** Measures how effectively the answer addresses the core aspects of the user query.
5. **Web Application & Logging:**
   * Developed an interactive Gradio interface allowing users to select a company and input financial queries.
   * Integrated `CommitScheduler` to log user inputs, retrieved contexts, and model outputs directly to a Hugging Face dataset.

---

## ☁️ Hugging Face Spaces Deployment
The `rag-analyzer` application is designed to run seamlessly on **Hugging Face Spaces** using the **Gradio** SDK.

### Prerequisites
* A [Hugging Face account](https://huggingface.co/join).
* An OpenAI API Key (`OPENAI_API_KEY`).
* A Hugging Face write token (`HF_TOKEN`) for log persistence via `CommitScheduler`.

---

### Step-by-Step Deployment Instructions

#### 1. Create a New Space
1. Navigate to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set the **Space name** (e.g., `rag-analyzer`).
3. Select **Gradio** as the Space SDK.
4. Set the repository visibility (Public or Private).

#### 2. Push Repository Artifacts to the Space
You can push the required deployment files (`app.py`, `requirements.txt`, and the `chroma_db/` persistent directory generated by your notebook) to the Space repository using Git:

```bash
# Add Hugging Face Space as a remote target
git remote add hf [https://huggingface.co/spaces/](https://huggingface.co/spaces/)<your-username>/rag-analyzer

# Push deployment artifacts to the Space
git push hf main
```
### CI/CD Deloyment Workflow
This diagram illustrates an automated CI/CD pipeline for Hugging Face Spaces.
```mermaid
graph LR
    subgraph Repo ["repository"]
        direction TB
        VDB["VectorDB"]
        APP["app.py"]
        REQ["requirements.txt"]
        LLM["LLM on Anyscale"]

        VDB --> APP
        APP --> REQ
        REQ --> LLM
        LLM --> APP
    end

    Repo --> Build["Build<br/>• Docker image created and pushed<br/>• Install requirements"]
    
    subgraph UI ["Gradio UI"]
        Interface["Gradio Web Interface"]
    end

    Build --> Interface
    Interface --> Logs["Logs"]
    Interface --> API["API"]

    subgraph CICD_Note ["CICD"]
        Note["Whenever changes have been made,<br/>a new build happens automatically"]
    end
```

---
## 🌐 Live Application & Datasets

* **Hugging Face Space App:** [Nyanzi Reports QnA Space](https://huggingface.co/spaces/jnyanzi/nyanzi_reports_qna)
* **Logs Dataset:** [Nyanzi Reports QnA Logs Dataset](https://huggingface.co/datasets/jnyanzi/logs_nyanzi_reports_qna)

---

## 📂 Repository Folder Structure

```Plaintext
rag-analyzer/
├── dataset/                # Initial 10-K PDF reports
│   ├── aws-10-k-2023.pdf
│   ├── google-10-k-2023.pdf
│   ├── IBM-10-k-2023.pdf
│   ├── Meta-10-k-2023.pdf
│   └── msft-10-k-2023.pdf
├── notebooks/              # Development notebooks and exports
│   ├── financial_rag_analysis.ipynb
│   └── financial_rag_analysis.html
├── cloud_db/               # Persisted Chroma vector database files
├── logs/                   # Log files generated by CommitScheduler
├── app.py                  # Main Gradio application script
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation & architecture
└── .gitignore              # Files to ignore (venv/, __pycache__, etc.)

```
