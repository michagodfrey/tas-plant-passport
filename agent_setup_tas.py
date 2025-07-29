# agent_setup_tas.py
# This file configures the LangChain agent that provides structured answers about
# Tasmanian fruit fly import requirements. It focuses specifically on:
# 1. Fruit fly host identification
# 2. State-specific pest presence assessment
# 3. ICA condition requirements

import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from tas_tools import fruit_fly_tool

# Load environment variables
load_dotenv()

# Generic footer that must be appended to all responses
# This ensures users are always reminded of the baseline requirements
GENERIC_TAS_FOOTER = (
    "⚠️  **Pre-entry paperwork (PBM-Tas §2.2)**\n"
    "• Lodge a *Notice of Intention (NoI) to Import* with Biosecurity Tasmania at least **24 h before the consignment arrives**; and\n"
    "• If required, attach an acceptable Plant Health Certificate, PHAC or equivalent phytosanitary certificate.\n\n"
    "Commodity-specific conditions (see above) apply on top of these baseline rules."
)

# Initialize the agent with specific configuration
agent = initialize_agent(
    # The fruit_fly_tool provides access to the fruit fly database and assessment
    tools=[fruit_fly_tool],
    
    # Use Gemini Pro for consistent, factual responses
    llm=ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        convert_system_message_to_human=True  # Gemini doesn't support system messages directly
    ),
    
    # Use the ZERO_SHOT_REACT_DESCRIPTION agent type
    # This allows the agent to:
    # 1. Reason about the query without examples
    # 2. Use the ReAct framework (Reason + Act)
    # 3. Generate structured responses
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    
    # Enable verbose output for debugging
    verbose=True,
    
    # Configure the agent's behavior with a detailed prompt
    agent_kwargs={
        "prefix": (
            "You are PlantPassport.ai, a regulatory assistant for **Tasmania fruit fly conditions only**.\n\n"
            "**STRUCTURED APPROACH**: Always analyze queries using these 3 key variables:\n"
            "1. **COMMODITY**: Identify the specific commodity (e.g., 'table grapes', 'apples', 'citrus')\n"
            "2. **DESTINATION**: Always Tasmania (this is fixed for this system)\n"
            "3. **ORIGIN**: The state/territory of origin (e.g., 'NSW', 'Victoria', 'WA') - this is CRITICAL for fruit fly assessment\n\n"
            "**FRUIT FLY ASSESSMENT PROCESS**:\n"
            "1. Extract the commodity and origin state from the user query\n"
            "2. **FIRST**: Check if the commodity is a fruit fly host (QFF or MFF)\n"
            "3. **THEN**: Check if the origin state has the relevant fruit fly present\n"
            "4. **FINALLY**: Determine appropriate ICA conditions and treatment requirements\n\n"
            "**RESPONSE FORMAT**:\n"
            "**Commodity**: [Commodity Name]\n"
            "**Origin**: [State/Territory]\n"
            "**Destination**: Tasmania\n\n"
            "**Fruit Fly Host Status**:\n"
            "• QFF host: YES/NO\n"
            "• MFF host: YES/NO\n\n"
            "**Risk Assessment**:\n"
            "• [Risk details or 'No risk detected']\n\n"
            "**Required ICA Conditions**:\n"
            "• [List applicable ICAs and conditions]\n\n"
            "**Treatment Requirements**:\n"
            "• [List treatment options]\n\n"
            "**Documentation Required**:\n"
            "• [List required certificates and paperwork]\n\n"
            "**⚠️ Pre-entry Requirements**:\n"
            "[Always include the generic footer]\n\n"
            "**IMPORTANT DECISION RULES**:\n"
            "- Origin state is CRITICAL - different states have different fruit fly profiles\n"
            "- QFF is present in QLD, NSW, VIC, NT, and parts of SA\n"
            "- MFF is present in WA and parts of SA\n"
            "- Tasmania is free from both fruit flies\n"
            "- If origin information is missing, ask for clarification\n"
            "- Use clear formatting with bullet points and section headers\n"
            "- Always call the fruit_fly_assessment tool with both commodity and origin state"
        )
    }
)

# Example usage
if __name__ == '__main__':
    # Test the agent with a sample query - edit the line below to test different queries
    print(agent.invoke({"input": "I want to bring strawberry fruit from QLD into Tasmania."}))
