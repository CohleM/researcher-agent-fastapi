import os
import json
import requests
import weaviate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WeaviateClient:
    def __init__(self, weaviate_url=None, weaviate_api_key=None, openai_api_key=None):
        # Use environment variables if the values are not provided explicitly
        self.__weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL")
        self.__weaviate_api_key = weaviate_api_key or os.getenv("WEAVIATE_API_KEY")
        self.__openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize Weaviate client
        self.client = weaviate.Client(
            url=self.__weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=self.__weaviate_api_key),
            additional_headers={
                "X-OpenAI-Api-Key": self.__openai_api_key
            }
        )

    def create_collection(self, collection_name, embedding_model):
        
        if embedding_model == 'openai': #uses text-embedding-ada-002 by default
            vectorizer = "text2vec-openai"
            
        class_obj = {
            "class": collection_name,
            "vectorizer":vectorizer ,
            "moduleConfig": {
                
                vectorizer: {}, #class level module configs
            }
        }
        self.client.schema.create_class(class_obj)

        
    
    def embed(self, collection_name, data):
        self.client.batch.configure(batch_size=100)  # Configure batch
        with self.client.batch as batch:  # Initialize a batch process
            for i, d in enumerate(data):  # Batch import data
                print(f"Importing question: {i + 1}")
                
                properties = {
                    "text": d.page_content,
                    "url": d.metadata['url']
                }
                
                batch.add_data_object(
                    data_object=properties,
                    class_name= collection_name
                )
                
                
                
    def semantic_search(self, collection_name, query_text, K=5):

        response = (
            self.client.query
            .get(collection_name, ["text", "url"])
            .with_near_text({"concepts": query_text })
            .with_limit(K)
            .do()
        )

        return response

    def hybrid_search(self, collection_name, query_text, K=5):
        
        response = (
            self.client.query
            .get(collection_name, ["text", "url"])
            .with_hybrid(
                query= query_text
            )
            .with_limit(K)
            .do()
        )
            
        return response


# weaviate_instance = WeaviateClient()


