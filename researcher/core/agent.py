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


class Researcher:
    def __init__(self, query):
        self.query = query
        self.cfg = Config()
        self.agent = None
        self.role = None
        self.visited_urls = set()
        self.context = []

    async def run_researcher_agent(self):
        """
        Run the researcher
        """
        if self.cfg.search_engine == "Duckduckgo":
            retriever = Duckduckgo()

        print(f"📘 Starting research for query: {self.query}")
        self.agent, self.role = await choose_agent(self.query, self.cfg)
        print(f"Running {self.agent} ...")

        # query modification
        sub_queries = await get_sub_queries(self.query, self.role, self.cfg) + [
            self.query
        ]

        for each_query in sub_queries:
            print(f"🔍 Searching web with query: {each_query}")
            content = await self.get_content_using_query(each_query)
            context = await self.get_similar_context(each_query, content)
            self.context.append(context)

        total_chunks = 0
        for chunk in self.context:
            total_chunks += len(chunk)

        print(f"Total chunk count {total_chunks}")

        print("Generating Report...")
        result = generate_report(self.context, self.query, self.role, self.cfg)

        async for text, finish_reason in result:
            yield text, finish_reason

    async def run_qa_agent(self):
        """
        QA agent
        """
        print("Running QA agent")

        print(f"🔍 Searching web with query: {self.query}")
        content = await self.get_content_using_query(self.query)
        context = await self.get_similar_context(self.query, content)
        self.context.append(context)

        total_chunks = 0
        for chunk in self.context:
            total_chunks += len(chunk)

        print(total_chunks)
        # print(f"Total chunk count {total_chunks}")

        print("Generating Answers...")
        result = generate_qa(self.context, self.query, self.cfg)

        async for text, finish_reason in result:
            yield text, finish_reason

    # Run summarization agent
    async def run_summarization_agent(self):
        """
        Summarization agent
        """
        print("Running summarization agent")

        result = generate_summary(self.query, self.cfg)

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

            print("searhc_urls", search_urls)

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
                print(f"✅ Adding url {url} to our research")
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
