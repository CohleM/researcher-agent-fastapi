from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings



class HybridRetriever:
    def __init__(self, documents, embeddings=OpenAIEmbeddings(model='text-embedding-3-small'), max_results=5):

        self.documents = documents
        self.embeddings = embeddings
        self.max_results = max_results
        self.retriever = self._hybrid_retriever()
        
    def _hybrid_retriever(self):
        
        # initialize the bm25 retriever and faiss retriever
        bm25_retriever = BM25Retriever.from_documents(self.documents)
        bm25_retriever.k = self.max_results

        # embedding = OpenAIEmbeddings()
        faiss_vectorstore = FAISS.from_documents(self.documents, self.embeddings)
        faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": self.max_results })

        #initialize the ensemble retriever
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever], weights=[0.2, 0.8]
        )

        return ensemble_retriever
    
    def get_context(self, query):

        return self.retriever.get_relevant_documents(query)
        


