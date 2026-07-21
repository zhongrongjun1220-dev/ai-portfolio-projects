from agents import Agent
from agents.models._openai_shared import set_use_responses_by_default
from .tools import (
    get_weather,
    preview_theme,
    analyze_sales_data,
    generate_deep_research_report,
)
from dotenv import load_dotenv
load_dotenv()

import os
default_model = os.getenv("DEFAULT_MODEL", "step-3.7-flash")

set_use_responses_by_default(False)

my_agent = Agent(
    name="ProAssistant",
    model=default_model,
    instructions="""You are an advanced assistant. Use the available tools when the user asks for weather, theme previews, sales analysis, or deep research. Answer in Chinese by default unless the user asks for another language.""",
    tools=[
        get_weather,
        preview_theme,
        analyze_sales_data,
        generate_deep_research_report,
    ],
)
