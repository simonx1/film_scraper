import os
import autogen
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

config_list = [
    {
        'model': 'gpt-4',
        'api_key': os.getenv('OPENAI_API_KEY')
    },
    {
        'model': 'gpt-3.5-turbo',
        'api_key': os.getenv('OPENAI_API_KEY')
    }
]

llm_config = {
    "request_timeout": 600,
    "seed": 41,
    "config_list": config_list,
    "temperature": 0
}

# Create user proxy agent, coder, product manager
# user_proxy = autogen.UserProxyAgent(
#     name="User_proxy",
#     system_message="A human admin who will give the idea and run the code provided by Coder.",
#     code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
#     human_input_mode="ALWAYS",
# )

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    code_execution_config=False,
    llm_config=llm_config,
    system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
)

engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message='''Engineer. You follow an approved plan. You write python code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)

analyst = autogen.AssistantAgent(
    name="Analyst",
    llm_config=llm_config,
    system_message="""Analyst. You follow an approved plan. You are able to search internet and extract desired data from the web. You don't write code."""
)

planner = autogen.AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a analyst who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a analyst.
''',
    llm_config=llm_config,
)

executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "code"},
    max_consecutive_auto_reply=20,
)

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
    llm_config=llm_config,
)

groupchat = autogen.GroupChat(agents=[user_proxy, engineer, analyst, planner, executor, critic], messages=[], max_round=10)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

user_proxy.initiate_chat(
    manager,
    message="""
Lookup https://kinoinfo.pl/premiery.jsp for movies comming to the polish theates withing the next 10 days. Then get each movie and lookup for this information for each:
- title (in polish)
- orignal title
- imdb id
- kinoinfo id
- yt embedded code
- description
- poster (url to the image)
- polish distributor
- release date
- genres
- actors
- directors
- duration
- rating
- country
- year of production
You can use https://kinoinfo.pl/ as well as https://www.themoviedb.org/ or any other source to get the movie information. Scrape the page content, do not use APIs. Translate the content to polish if needed. The result should be a list of movies with the information above in JSON format.
""",
)