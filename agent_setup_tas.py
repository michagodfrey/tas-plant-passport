# agent_setup_tas.py
# This file configures the LangChain agent that provides structured answers about
# Tasmanian import requirements. It combines:
# 1. A zero-shot agent that can reason about import requirements
# 2. The tas_manual_tool for looking up specific requirements
# 3. A structured prompt that ensures consistent, well-formatted responses

from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from tas_tools import tas_manual_tool

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
    # The tas_manual_tool provides access to the structured database and semantic search
    tools=[tas_manual_tool],
    
    # Use a zero-temperature model for consistent, factual responses
    llm=ChatOpenAI(temperature=0),
    
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
            "You are PlantPassport.ai, a regulatory assistant for **Tasmania only**.\n"
            "When a user asks about bringing a commodity into Tasmania, follow these steps exactly:\n"
            "1. Identify the commodity and its type (fruit, plant, seed, etc.).\n"
            "2. Call `tas_manual_lookup` with that commodity.\n"
            "3. Structure your response as follows:\n"
            "   a. Commodity Type: [fruit/plant/seed/etc.]\n"
            "   b. Import Requirements:\n"
            "      - List each IR number with its full title\n"
            "      - For each IR, cite the specific section and page number\n"
            "      - Detail any applicable ICAs with their status\n"
            "   c. Pest Considerations:\n"
            "      - List relevant pests from Table 1\n"
            "      - Note any state-specific pest presence\n"
            "   d. Additional Requirements:\n"
            "      - Any special conditions (e.g., phylloxera zones)\n"
            "      - Treatment requirements if specified\n"
            "4. Always append the generic pre-entry reminder in full.\n"
            "5. If the commodity isn't listed, explicitly state this and still give the generic footer.\n\n"
            "Use clear formatting with bullet points and section headers. "
            "Never invent requirements - only cite what's explicitly in the Tasmanian PQM."
        )
    }
)

# Example usage
if __name__ == '__main__':
    # Test the agent with a sample query - edit the line below to test different queries
    print(agent.invoke({"input": "What conditions do I need to meet to bring potatoes from Victoria into Tasmania?"}))
