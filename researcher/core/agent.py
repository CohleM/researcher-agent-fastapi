import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from researcher.config import Config
from researcher.search.duckduckgo import Duckduckgo
from researcher.utils.functions import *
from researcher.retriever.langchain_hybrid_retriever import HybridRetriever
from researcher.scraping.scrape import Scraper
from researcher.context.chunking import Chunking
import logging
from langsmith.run_helpers import traceable
from researcher.search.custom import get_links_from_queries
from backend.routers.files import get_file_from_r2
import traceback

class Researcher:
    def __init__(self, query, websocket=None, files = None):
        self.query = query
        self.cfg = Config()
        self.agent = None
        self.role = None
        self.websocket = websocket
        self.visited_urls = set()
        self.context = [] 
        self.files = files

    async def run_researcher_agent(self, stop_event):
        """
        Run the researcher
        """

        await stream_output(
            f"📘 Starting research for query: {self.query}", websocket=self.websocket)

        self.agent, self.role = await choose_agent(self.query, self.cfg)
        await stream_output(f"Running {self.agent} ...", websocket=self.websocket)

        # query modification
        sub_queries = await get_sub_queries(self.query, self.role, self.cfg) + [
            self.query
        ]

        # Commenting this for checking
        for each_query in sub_queries:
            print(f"🔍 Searching web with query: {each_query}")
            content = await self.get_content_using_query(each_query) # Getting the content by scraping urls
            web_context = await self.get_similar_context(each_query, content)
            self.context.append(web_context)


        # Check if we have files


        try:
            files_context= []
            if len(self.files)>0:
                print('FILES part executing')
                retirever = await self.process_files() #process_files function returns retriever for all the enabled files.
                for each_query in sub_queries:

                    print('Adding documents for query ', each_query)
                    each_query_context = retirever.get_context(each_query)
                    for each_document in each_query_context:
                        if each_document not in self.context:
                            files_context.append(each_document)
                            self.context.append(each_document)

            print(files_context, 'len', len(files_context))


        except Exception as e:
            traceback.print_exc()
            print('Error', e)
            

        # total_chunks = 0
        # for chunk in self.context:
        #     total_chunks += len(chunk)

        # print(f"Total chunk count {total_chunks}")

        await stream_output("✍🏻 Generating final Report...", websocket=self.websocket)
        result = generate_report(self.context, self.query, self.role, self.cfg, stop_event)

        async for text, finish_reason in result:
            yield text, finish_reason

    async def run_qa_agent(self, stop_event):
        """
        QA agent
        """
        # print("Running QA agent")

        print(f"🔍 Searching web with query: {self.query}")
        await stream_output(
            f"📘 Starting QA for query: {self.query}", websocket=self.websocket)
        content = await self.get_content_using_query(self.query)
        context = await self.get_similar_context(self.query, content)
        self.context.append(context)

        total_chunks = 0
        for chunk in self.context:
            total_chunks += len(chunk)

        print(total_chunks)
        # print(f"Total chunk count {total_chunks}")

        print("Generating Answers...")
        await stream_output(
            f"Generating Answer ...", websocket=self.websocket)
        result = generate_qa(self.context, self.query, self.cfg, stop_event)

        async for text, finish_reason in result:
            yield text, finish_reason

    # Run summarization agent
    async def run_summarization_agent(self, stop_event):
        """
        Summarization agent
        """
        print("Running summarization agent")

        result = generate_summary(self.query, self.cfg, stop_event)

        async for text, finish_reason in result:
            yield text, finish_reason

    # Run summarization agent
    async def run_paraphrasing_agent(self, stop_event):
        """
        Summarization agent
        """
        print("Running paraphrasing agent")

        result = generate_paraphrase(self.query, self.cfg, stop_event)

        async for text, finish_reason in result:
            yield text, finish_reason

    async def get_content_using_query(self, query):
        try:
            # Scrape Links using Duckduck go api
            # search_engine = Duckduckgo(query=query)
            # search_urls = search_engine.search(
            #     max_results=self.cfg.max_search_results_per_query
            # )
            # search_urls = [url.get("href") for url in search_urls]

            # Scrape Links using Custom bs4 scraper.
            search_urls = await get_links_from_queries(
                [query], max_links=self.cfg.max_search_results_per_query
            )

            print("search_urls", search_urls)

            new_search_urls = await self.get_unique_urls(
                search_urls
            )  # filter out the same urls

            content_scraper = Scraper(new_search_urls)
            content = content_scraper.run()

            return content

        except Exception as e:
            print(
                f"{Fore.RED} Error while getting content using query {e}{Style.RESET_ALL}"
            )
            return []

    async def get_chunks(self, content):
        chunks = []
        chunking = Chunking(self.cfg.chunk_size, self.cfg.chunk_overlap)

        for each_content in content:
            chunks += chunking.run(
                content=each_content["raw_content"],
                metadatas={"url": each_content["url"]},
            )

        return chunks

    async def get_unique_urls(self, urls):
        new_urls = []
        for url in urls:
            if url not in self.visited_urls:
                await stream_output(f"✅ Adding url {url} to our research", websocket=self.websocket)
                new_urls.append(url)
                self.visited_urls.add(url)

        return new_urls

    # @traceable(run_type="chain", name='context')
    async def get_similar_context(self, query, content):
        # chunk where?
        try:
            chunks = await self.get_chunks(content)
            hybrid_retriever = HybridRetriever(
                chunks, max_results=self.cfg.max_chunks_per_query
            )
            similar_context = hybrid_retriever.get_context(query)

            return similar_context
        except Exception as e:
            print(
                f"{Fore.RED} Error while getting content using query {e}{Style.RESET_ALL}"
            )
            return []


    async def process_files(self):
        await stream_output(f"🔍 Searching your files...", websocket=self.websocket)
        all_file_content =  await get_file_from_r2(self.files) #maybe through api req

        chunks = []
        chunking = Chunking(self.cfg.chunk_size, self.cfg.chunk_overlap)

        # each_content has type {'page_content': 'something', "metadata": {
    #   "source": "5031-Article Text-8094-1-10-20190709.pdf",
    #   "file_path": "5031-Article Text-8094-1-10-20190709.pdf",
    #   "page": 0,
    #   "total_pages": 8,
    #   "format": "PDF 1.5",
    #   "title": "Get IT Scored Using AutoSAS!",
    #   "author": "Yaman Kumar, Swati Aggarwal, Debanjan Mahata, Rajiv Ratn Shah, Ponnurangam Kumaraguru, Roger Zimmermann",
    #   "subject": "",
    #   "keywords": "",
    #   "creator": "TeX",
    #   "producer": "MiKTeX pdfTeX-1.40.17",
    #   "creationDate": "D:20190630120825+05'30'",
    #   "modDate": "D:20190630120825+05'30'",
    #   "trapped": ""
    # },}
        for each_content in all_file_content:
            chunks += chunking.run(
                content=each_content.page_content,
                metadatas={'filename' : each_content.metadata['source'], 'page number': each_content.metadata['page']},
            )

        # chunk where?
        try:
            hybrid_retriever = HybridRetriever(
                chunks, max_results=self.cfg.max_chunks_per_query
            )

            return hybrid_retriever
        except Exception as e:
            print(
                f"{Fore.RED} Error while getting content using query {e}{Style.RESET_ALL}"
            )
            return None 


        

        