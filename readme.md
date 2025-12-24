### Researcher Agent

The agent is capable of generating detailed, factual, and unbiased research reports, with customizable options to focus on specific resources, outlines, and insights. Drawing inspiration from recent Plan-and-Solve and RAG papers.

This agent utilizes all the components of RAG, such as embeddings, chunking, retrieving, some post-processings, and async calls to LLM provider. It stores embeddings in memory, eliminating the need for vector database. It is able to search the internet, or different types of files provided, and curates research report based on the provided context.

Here's a sample demo, where agent searches the internet and curates a detailed report with references.



https://github.com/user-attachments/assets/14c590b8-3468-48c8-84dc-b27ef58e3161


This code contains backend code + researcher agent code. Researcher agent code can be found in the `/researcher/core` directory.

## How to run

### Install the dependency

```bash
pip install -r requirements.txt
```

### Run the FastAPI server

```bash
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

or you can use docker

```bash
docker-compose up --build
```
