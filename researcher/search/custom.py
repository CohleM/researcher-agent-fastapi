import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time


async def fetch_url(session, query, max_links):
    url = f"https://duckduckgo.com/html?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            links = [a["href"] for a in soup.find_all("a", class_="result__url")][
                :max_links
            ]
            return links
        else:
            print(f"Error: {response.status}")
            return []


async def get_links_from_queries(search_queries, max_links=4):
    """
    Input:
    search_queries [list] : list of search_quries

    Returns:

    """

    # Add your search queries here
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, query, max_links) for query in search_queries]
        results = await asyncio.gather(*tasks)

    for query, links in zip(search_queries, results):
        if links:
            #             print(f"Links for query '{query}':")
            return links
        else:
            print(f"No links found for query '{query}'.")
