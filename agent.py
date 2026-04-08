from google.adk.agents import Agent
from google.adk.tools import google_search, AgentTool
from .tools import get_market_pulse_toolset

# 1. Fetch and Configure your MCP toolset
# We call the helper function, then manually override the timeout setting.
market_pulse_mcp = get_market_pulse_toolset()

# We set this to 60.0 seconds to account for yfinance data fetching
# and the "cold start" time of the Cloud Run container.
market_pulse_mcp.request_timeout = 60.0

# 2. Define the Specialist Agent
# This agent handles the real-time news gathering via Google Search.
search_specialist = Agent(
    name="search_specialist", 
    model="gemini-2.5-flash",
    description="Expert at finding real-time market catalysts and news breaks.",
    instruction="Find 3 critical news bullets for the ticker from the last 24 hours.",
    tools=[google_search]
)

# 3. Define the Orchestrator Agent (The Senior Quant)
root_agent = Agent(
    name="market_analyst_pro",
    model="gemini-2.5-flash",
    instruction="""
    Act as a Senior Quant Strategist. Your goal is to provide a DECISIVE trade recommendation.
    
    OPERATIONAL STEPS:
    1. Use your MCP tools to get price, change, and technical data for the ticker.
    2. Use 'search_specialist' to identify 3 recent news catalysts.
    3. EVALUATE: Weigh the news against the price action. 
       - Partnerships/Defense contracts = Positive.
       - Regulatory hurdles/High multiples = Negative.
    
    REQUIRED OUTPUT FORMAT (Do not skip):
    - **Ticker**: [Name] | **Price**: [Price] ([Change%])
    - **Sentiment Score**: [X/10] (1=Bearish, 10=Bullish)
    - **Verdict**: [BUY / HOLD / AVOID]
    - **Logic Summary**: 2-3 sentences explaining the 'Why' behind the score.
    """,
    # We pass the MCP toolset and the Search Specialist as tools for the root agent.
    tools=[market_pulse_mcp, AgentTool(agent=search_specialist)]
)

# --- Web UI Exports ---
# This list defines what appears in the dropdown menu of your deployed app.
market_agents = [root_agent, search_specialist]

# 'apps' is the mandatory variable name the ADK Web Server looks for.
apps = market_agents
