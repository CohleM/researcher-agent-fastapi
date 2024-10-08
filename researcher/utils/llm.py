from openai import OpenAI
import logging
from langsmith.run_helpers import traceable
from typing import AsyncGenerator, NoReturn
import os
from researcher.prompts.prompts import youtube_notes_prompt

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

from dotenv import load_dotenv

from openai import AsyncOpenAI

load_dotenv()

# client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def get_ai_response(stop_event, messages: str, cfg) -> AsyncGenerator[str, None]:
    """
    OpenAI Response
    """

    try:
        
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = await client.chat.completions.create(
            model=cfg.llm,
            messages=messages,
            stream=True,
        )

        all_content = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            finish_reason = chunk.choices[0].finish_reason
            # print("haha", content)
            # print(content)
            # if content:
            # all_content += content
            if content:
                all_content += content
                # Check the stop event and exit the loop if it's set
                if stop_event.is_set():
                    await client.close()
                    break
            yield all_content, finish_reason

    except Exception as e:
        print('yolooo haha , error', e)

# previously we used this
async def create_chat_completion(messages, cfg, stream=False):
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=os.getenv('OPENAI_API_KEY')
    )

    if not stream:
        chat_completion = client.chat.completions.create(
            messages=messages, model=cfg.llm, temperature=cfg.temperature
        )

        print(f"Token Usage: {chat_completion.usage}")

        return chat_completion.choices[0].message.content




async def generate_youtube_notes(transcript, cfg):

    messages = [
        {"role": "system", "content": "You are a youtube assistant that assists students in explaining topics from a youtube transcript."},
        {"role": "user", "content": youtube_notes_prompt(transcript)},
    ]
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    chat_completion =  await client.chat.completions.create(messages=messages, model=cfg.llm)
    return chat_completion.choices[0].message.content