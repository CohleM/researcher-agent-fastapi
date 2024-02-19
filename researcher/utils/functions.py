import json
from colorama import Fore, Style
import asyncio
from .llm import *
from researcher.prompts.prompts import *
from langsmith.run_helpers import traceable
from .youtube_transcript import _parse_video_id, combine_transcript
from youtube_transcript_api import YouTubeTranscriptApi


async def get_sub_queries(query, role, cfg):
    try:
        messages = [
            {"role": "system", "content": role},
            {"role": "user", "content": generate_search_queries_prompt(query)},
        ]

        response = await create_chat_completion(messages, cfg=cfg)
        response = json.loads(response)

        return response

    except Exception as e:
        print(
            f"{Fore.RED} Error while generating multiple queries {e}{Style.RESET_ALL}"
        )
        return []
    




async def choose_agent(query, cfg):
    try:
        response = await create_chat_completion(
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {query}"},
            ],
            cfg=cfg,
        )

        agent = json.loads(response)
        return agent["server"], agent["agent_role_prompt"]

    except Exception as e:
        print(f"{Fore.RED} Error in choose_agent: {e}{Style.RESET_ALL}")
        return (
            "Default Agent",
            "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text.",
        )


@traceable(run_type="llm", name="report")
async def generate_report(context, question, agent_role, cfg, search_type, stop_event):
    
    

    if search_type == 'web':
        prompt = generate_report_prompt(question, context)
    else:
        prompt = generate_report_prompt_using_files_and_web(question, context)


    response = ""
    try:
        print(f"using {cfg.total_words} words ")
        response = get_ai_response(
            stop_event,
            messages=[
                {"role": "system", "content": f"{agent_role}"},
                {
                    "role": "user",
                    # "content": f"task: {generate_report_prompt(question, context, total_words = cfg.total_words)}",
                    "content": f"task: {prompt}",
                },
            ],
            cfg=cfg,
        )

        # return response
        async for text, finish_reason in response:
            yield text, finish_reason

    except Exception as e:
        print(f"{Fore.RED} Error while generating report {e}{Style.RESET_ALL}")
        yield response


async def generate_qa(context, question, cfg, search_type, stop_event):

    if search_type == 'web':
        prompt = generate_qa_prompt(question, context)
    elif search_type == None:
        print('YOOOOO')
        prompt = generate_qa_prompt_text_only(question, context)
    else:
        prompt = generate_qa_prompt_using_files_and_web(question, context)

    response = ""
    try:
        print(f"using {cfg.total_words} words ")
        response = get_ai_response(stop_event,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured answers for user's question",
                },
                {
                    "role": "user",
                    "content": f"task: {prompt}",
                },
            ],
            cfg=cfg,
        )

        # return response
        async for text, finish_reason in response:
            yield text, finish_reason

    except Exception as e:
        print(f"{Fore.RED} Error while QA answers {e}{Style.RESET_ALL}")
        yield response


# Generate Summary
async def generate_summary(original_text, cfg, stop_event):
    response = ""
    try:
        response = get_ai_response(stop_event,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert summarizer and analyzer who can help me.",
                },
                {
                    "role": "user",
                    "content": f"task: {summarize(original_text)}",
                },
            ],
            cfg=cfg,
        )

        # return response
        async for text, finish_reason in response:
            yield text, finish_reason

    except Exception as e:
        print(f"{Fore.RED} Error while QA answers {e}{Style.RESET_ALL}")
        yield response


# Generate paraphrased version
async def generate_paraphrase(original_text, cfg, stop_event):
    response = ""
    try:
        response = get_ai_response(stop_event,
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert paraphraser and analyzer who can help me.",
                },
                {
                    "role": "user",
                    "content": f"task: {generate_paraphrase_prompt(original_text)}",
                },
            ],
            
            cfg=cfg,
            
        )

        # return response
        async for text, finish_reason in response:
            yield text, finish_reason

    except Exception as e:
        print(f"{Fore.RED} Error while QA answers {e}{Style.RESET_ALL}")
        yield response


async def stream_output(message, websocket):
    if websocket:
        await websocket.send_json({"content": message, "type": "log"})



## Summarized notes from youtube
async def notes_from_youtube(link, cfg):
    # Get the video id from link
    video_id = _parse_video_id(link)
    # Generate transcript from link
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    # Combine the transcript 
    combined_transcript = combine_transcript(transcript)
    
    #Generate
    try:
        tasks = [generate_youtube_notes(transcript, cfg) for transcript in combined_transcript]
        response = await asyncio.gather(*tasks)
        combined_results = ''
        for i in response:
            combined_results += i + '\n\n'
        return combined_results, combined_transcript

    except Exception as e:
        print(
            f"{Fore.RED} Error while generating multiple queries {e}{Style.RESET_ALL}"
        )
        return []