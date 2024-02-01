class Config:
    def __init__(self):

        self.retriever = "Weaviate"
        self.search_engine = "duckduckgo"
        self.llm = "gpt-3.5-turbo-1106"
        self.max_search_query = 3
        self.max_search_results_per_query = 3 
        self.max_chunks_per_query = 3 
        self.total_words = 2000
        self.temperature = 0.2
        self.chunk_size = 1000
        self.chunk_overlap = 100
        
        

