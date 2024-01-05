
from langchain.text_splitter import RecursiveCharacterTextSplitter

from researcher.scraping.scrape import Scraper


class Chunking:
    
    def __init__(self, size, chunk_overlap):
        self.size = size
        self.chunk_overlap = chunk_overlap
    
    def run(self, content, metadatas):
        
        splitter = RecursiveCharacterTextSplitter(chunk_size = self.size, chunk_overlap = self.chunk_overlap)
        text = splitter.create_documents([content], metadatas = [metadatas])
        
        return text
        
        
