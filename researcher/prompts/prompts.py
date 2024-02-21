from datetime import datetime


def summarize(original_text):
    return f"""
        Generate a concise and coherent summary from the given Context. 
        Condense the context into a well-written summary that captures the main ideas, key points, and insights presented in the context. 
        Prioritize clarity and brevity while retaining the essential information. 
        Aim to convey the context's core message and any supporting details that contribute to a comprehensive understanding. 
        Craft the summary to be self-contained, ensuring that readers can grasp the content even if they haven't read the context. 
        Provide context where necessary and avoid excessive technical jargon or verbosity.
        The goal is to create a summary that effectively communicates the context's content while being easily digestible and engaging.
        CONTEXT: {original_text}
        SUMMARY: 
        """


def generate_paraphrase_prompt(original_text):
    return f"""
    Rephrase the given passage with the aim of expressing the content in a different way while preserving its original meaning.
    Pay close attention to the choice of words, sentence structure, and overall tone. 
    Ensure that the paraphrased version remains coherent, accurate, and contextually appropriate. 
    The goal is to convey the information in a unique manner without altering the core meaning or message. 
    Take into account any nuances, idiomatic expressions, or specific terminology present in the original passage. 
    Please provide a comprehensive paraphrased version that captures the essence of the original text.
    PASSAGE : {original_text}
    Paraphrased text: 
    """


def generate_qa_prompt(question, context):
    print("yes using qa prompt for web")
    return (
        f'Relevant Information: """{context}"""\n\n'
        f"Using the above relevant information, answer the following"
        f' query or task: "{question}" in detail'
        "Your answer should be short and simple, accurate, and to the point"
        f"with facts and numbers if available."
        "You must write the answer with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        f" Do NOT deter to general and meaningless conclusions. If you don't know the answer please say I couln't find the answer and don't try to make up your own answer.\n"
        "ALWAYS return Inline SOURCES alongside the sentences if there are any and all the inline sources in the end."
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )
def generate_qa_prompt_using_files_and_web(question, context):
    print("yes using qa prompt for both")
    return (
        f'Relevant Information: """{context}"""\n\n'
        f"Using the above relevant information, answer the following"
        f' query or task: "{question}" in detail'
        "Your answer should be short and simple, accurate, and to the point"
        f"with facts and numbers if available."
        "You must write the answer with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        f" Do NOT deter to general and meaningless conclusions. If you don't know the answer please say I couln't find the answer and don't try to make up your own answer.\n"
        "ALWAYS return Inline SOURCES alongside the sentences if there are any and all the inline sources in the end. There will be two types of sources: one that contains URL and another that contains filenames. For sources containing URL cite them as normal url but for the sources containing filename cite them using their filename and page number in this format (filename, p. page number), just cite them as normal text. "
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )

def generate_qa_prompt_text_only(question, context):
    print("Using prompt for text ONLY ")
    return (
        f'Relevant Information: """{context}"""\n\n'
        f"Using the above relevant information, answer the following"
        f' query or task: "{question}" in detail'
        "Your answer should be short and simple, accurate, and to the point"
        f"with facts and numbers if available."
        "You must write the answer with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        f" Do NOT deter to general and meaningless conclusions. If you don't know the answer please say I couln't find the answer and don't try to make up your own answer.\n"
       
    )

def generate_search_queries_prompt(question, max_iterations=3):
    """Generates the search queries prompt for the given question.
    Args: question (str): The question to generate the search queries prompt for
    Returns: str: The search queries prompt for the given question
    """

    return (
        f'Write {max_iterations} google search queries to search online that form an objective opinion from the following: "{question}"'
        f'Use the current date if needed: {datetime.now().strftime("%B %d, %Y")}.\n'
        f'You must respond with a list of strings in the following format: ["query 1", "query 2", "query 3"].'
    )


# def generate_report_prompt(question, context, report_format="APA", total_words=1000):
#     """Generates the report prompt for the given question and research summary.
#     Args: question (str): The question to generate the report prompt for
#             research_summary (str): The research summary to generate the report prompt for
#     Returns: str: The report prompt for the given question and research summary
#     """
#     print('using web prompt')
#     return (
#         f'Information: """{context}"""\n\n'
#         f"Using the above information, answer the following"
#         f' query or task: "{question}" in a detailed report --'
#         " The report should focus on the answer to the query, should be well structured, informative,"
#         f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n"
#         "You should strive to write the report as long as you can using all relevant and necessary information provided.\n"
#         "You must write the report with markdown syntax.\n "
#         f"Use an unbiased and journalistic tone. \n"
#         "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
#         f"You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n"
#         f"You MUST write the report in {report_format} format.\n "
#         f"You MUST Cite search results using inline notations. Only cite the most \
#             relevant results that answer the query accurately. Place these citations at the end \
#             of the sentence or paragraph that reference them.\n"
#         f"Please do your best, this is very important to my career. "
#         f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
#     )

def generate_report_prompt_using_files_and_web(question, context, report_format="APA", total_words=3000):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    print('using REPORT both prompt')
    return (
        f'Information: """{context}"""\n\n'
        f"Using the above information, answer the following"
        f' query or task: "{question}" in a detailed report --'
        " The report should focus on the answer to the query, should be well structured, informative,"
        f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n"
        "You should strive to write the report as long as you can using all relevant and necessary information provided.\n"
        "You must write the report with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
        f"You MUST write all used source at the end of the report as references, and make sure to not add duplicated sources. "
        "There will be two types of sources: one that contains webpage url and another that contains filenames."
         """You should reference each sources in this format.
        1. For sources having url. Reference them in this format:
            domain name (url)
        2. For sources having filenames. Reference them in this format:
            filename, p. page_number 
        """
        "For example: If the source is like this"
           "```metadata={'url': 'https://www.consumeraffairs.com/finance/mutual-funds-vs-etfs.html'}``` then you should reference them as ConsumerAffairs. ('https://www.consumeraffairs.com/finance/mutual-funds-vs-etfs.html') "
           "If the source is like this"
           "```metadata={'filename': 'sec-guide-to-savings-and-investing.pdf', 'page number': 13})``` then you should reference them as  sec-guide-to-savings-and-investing.pdf, p. 13"
        f"You MUST write the report in {report_format} format.\n "
        f"You MUST Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them. \n"
        f"Please do your best, this is very important to my career. "
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )

def generate_essay_prompt_using_files_and_web(question, context, report_format="APA", total_words=3000):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    print('using ESSAY both prompt')
    return (
        f'Information: """{context}"""\n\n'
        f"Using the above information, answer the following"
        f' query or task: "{question}" in a detailed essay --'
        " The essay should focus on the answer to the query, should be well structured, informative,"
        f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n"
        "You should strive to write the essay as long as you can using all relevant and necessary information provided.\n"
        "You must write the essay with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
        f"You MUST write all used source at the end of the essay as references, and make sure to not add duplicated sources. There will be two types of sources: one that contains URL and another that contains filenames. \n"
        """You should reference each sources in this format.
        1. For sources having url. Reference them in this format:
            domain name (url)
        2. For sources having filenames. Reference them in this format:
            filename, p. page_number 
        """
        "For example: If the source is like this"
           "```metadata={'url': 'https://www.consumeraffairs.com/finance/mutual-funds-vs-etfs.html'}``` then you should reference them as ConsumerAffairs. ('https://www.consumeraffairs.com/finance/mutual-funds-vs-etfs.html') "
           "If the source is like this"
           "```metadata={'filename': 'sec-guide-to-savings-and-investing.pdf', 'page number': 13})``` then you should reference them as  sec-guide-to-savings-and-investing.pdf, p. 13"
        f"You MUST write the essay in {report_format} format.\n "
        f"You MUST Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them. \n"
        f"Please do your best, this is very important to my career. "
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )


def generate_report_prompt(question, context, report_format="APA", total_words=3000):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    print('Using both but report prompt')
    return (
        f'Information: """{context}"""\n\n'
        f"Using the above information, answer the following"
        f' query or task: "{question}" in a detailed report --'
        " The report should focus on the answer to the query, should be well structured, informative,"
        f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n"
        "You should strive to write the report as long as you can using all relevant and necessary information provided.\n"
        "You must write the report with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
        f"You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n"
        f"You MUST write the report in {report_format} format.\n "
        f"You MUST Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them. \n"
        f"Please do your best, this is very important to my career. "
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )

def generate_essay_prompt(question, context, report_format="APA", total_words=3000):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    print('using ESSAY prompt')
    return (
        f'Information: """{context}"""\n\n'
        f"Using the above information, answer the following"
        f' query or task: "{question}" in a detailed essay --'
        " The essay should focus on the answer to the query, should be well structured, informative,"
        f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n"
        "You should strive to write the essay as long as you can using all relevant and necessary information provided.\n"
        "You must write the essay with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
        f"You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n"
        f"You MUST write the essay in {report_format} format.\n "
        f"You MUST Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them. \n"
        f"Please do your best, this is very important to my career. "
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )


def generate_report_prompt1(question, context, report_format="apa", total_words=3000):
    """Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    return (
        f'Information: """{context}"""\n\n'
        f"Using the above information, answer the following"
        f' query or task: "{question}" in a detailed report --'
        " The report should focus on the answer to the query, should be well structured, informative,"
        f" in depth and comprehensive, with facts and numbers if available \n"
        ""
        "You must write the report with markdown syntax.\n "
        f"Use an unbiased and journalistic tone. \n"
        "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
        f"You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n"
        f"You MUST write the report in {report_format} format.\n "
        f"Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them.\n  The whole report MUST be \
            a long detailed \ report with minimum of 5000 words. You should strive to write the report as long as you can using all relevant and necessary information provided.\n \
            Please do your best, this is very important to my career. "
        f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"
    )


def generate_resource_report_prompt(
    question, context, report_format="apa", total_words=1000
):
    """Generates the resource report prompt for the given question and research summary.

    Args:
        question (str): The question to generate the resource report prompt for.
        context (str): The research summary to generate the resource report prompt for.

    Returns:
        str: The resource report prompt for the given question and research summary.
    """
    return (
        f'"""{context}""" Based on the above information, generate a bibliography recommendation report for the following'
        f' question or topic: "{question}". The report should provide a detailed analysis of each recommended resource,'
        " explaining how each source can contribute to finding answers to the research question."
        " Focus on the relevance, reliability, and significance of each source."
        " Ensure that the report is well-structured, informative, in-depth, and follows Markdown syntax."
        " Include relevant facts, figures, and numbers whenever available."
        " The report should have a minimum length of 1,200 words."
    )


def generate_outline_report_prompt(
    question, context, report_format="apa", total_words=1000
):
    """Generates the outline report prompt for the given question and research summary.
    Args: question (str): The question to generate the outline report prompt for
            research_summary (str): The research summary to generate the outline report prompt for
    Returns: str: The outline report prompt for the given question and research summary
    """

    return (
        f'"""{context}""" Using the above information, generate an outline for a research report in Markdown syntax'
        f' for the following question or topic: "{question}". The outline should provide a well-structured framework'
        " for the research report, including the main sections, subsections, and key points to be covered."
        " The research report should be detailed, informative, in-depth, and a minimum of 1,200 words."
        " Use appropriate Markdown syntax to format the outline and ensure readability."
    )


def get_report_by_type(report_type):
    report_type_mapping = {
        "research_report": generate_report_prompt,
        "resource_report": generate_resource_report_prompt,
        "outline_report": generate_outline_report_prompt,
    }
    return report_type_mapping[report_type]


def auto_agent_instructions():
    return """
        This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific server, defined by its type and role, with each server requiring distinct instructions.
        Agent
        The server is determined by the field of the topic and the specific name of the server that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each server type is associated with a corresponding emoji.

        examples:
        task: "should I invest in apple stocks?"
        response: 
        {
            "server": "💰 Finance Agent",
            "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
        }
        task: "could reselling sneakers become profitable?"
        response: 
        { 
            "server":  "📈 Business Analyst Agent",
            "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
        }
        task: "what are the most interesting sites in Tel Aviv?"
        response:
        {
            "server:  "🌍 Travel Agent",
            "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
        }
    """


def generate_summary_prompt(query, data):
    """Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return (
        f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the '
        f"query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual "
        f"information such as numbers, stats, quotes, etc if available. "
    )

def youtube_notes_prompt(transcript):

    return f""" TRANSCRIPT: {transcript}.

    You need to perform these tasks step by step.

    1. Read all the transcript provided above.
    2. Generate the important titles, and for each title, you must describe them in bullet points.


    IMPORTANT POINT TO CONSIDER
    1. Your response should be well structured, informative, in depth and comprehensive, with facts and numbers if available.
    2. You should strive to write the as long as you can using all relevant and necessary information provided.
    3. DONOT include conslusion in your response.
    4. Please give your response in markdown syntax
    5. Please do your best, this is very important to my career. 
    6. DONOT include any other text in your response besides what's described above.
    7. DONOT generate Numbered titles.

    Your response format should be in this format:

    ## Title 1
    - Explanation 1
    - Explanation 2

    ## Title 2
    - Explanation 1
    - Explanation 2


    Please do your best, this is very important to my career. 
    """


## YOUTUBE

# async def generate_notes(transcript):
#     user_message = f""" TRANSCRIPT: {combined_transcript[0]['text']}.

#     You need to perform these tasks step by step.

#     1. Read all the transcript provided above.
#     2. Generate the important titles, and for each title, you must describe them in bullet points.


#     IMPORTANT POINT TO CONSIDER
#     1. Your response should be well structured, informative, in depth and comprehensive, with facts and numbers if available.
#     2. You should strive to write the as long as you can using all relevant and necessary information provided.
#     3. DONOT include conslusion in your response.
#     4. Please give your response in markdown syntax
#     5. Please do your best, this is very important to my career. 
#     6. DONOT include any other text in your response besides what's described above.
#     7. DONOT generate Numbered titles.

#     Your response format should be in this format:

#     ## Title 1
#     - Explanation 1
#     - Explanation 2

#     ## Title 2
#     - Explanation 1
#     - Explanation 2




#     Please do your best, this is very important to my career. 
#     """


#     messages = [
#         {"role": "system", "content": "You are a youtube assistant that assists students in explaining topics from a youtube transcript."},
#         {"role": "user", "content": user_message},
#     ]
#     chat_completion =  client.chat.completions.create(messages=messages, model='gpt-3.5-turbo-0125')
#     return chat_completion.choices[0].message.content

# async def generate_all():
#     tasks = [generate_notes(transcript) for transcript in combined_transcript]
#     results = await asyncio.gather(*tasks)
#     return results

# # Run the main function
# # final_notes = asyncio.run(main())

# results = await generate_all()