# tas_tools.py
# This file creates a LangChain Tool that provides structured answers about Tasmanian import requirements
# It combines structured data (from tas_data.py) with semantic search (from tas_index.py) to provide
# accurate and detailed responses about plant quarantine requirements

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from tas_index import retriever_tas
from langchain.agents import Tool
from tas_data import commodity_db, CommodityType
from typing import Set, Optional

# Create a RetrievalQA chain that combines:
# 1. The FAISS retriever from tas_index.py (for semantic search)
# 2. A ChatOpenAI model (for generating answers)
# 3. Source document tracking (for citations)
qa_chain_tas = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(temperature=0),  # Use 0 temperature for consistent, factual responses
    retriever=retriever_tas,        # Use the FAISS retriever from tas_index.py
    return_source_documents=True    # Track which parts of the manual were used
)

def format_pest_info(pest_codes: Set[str], origin_state: Optional[str] = None) -> str:
    """
    Format pest information into a readable string, including state-specific details.
    This helps provide context about which pests are relevant based on origin.
    """
    if not pest_codes:
        return ""
    
    parts = []
    for code in pest_codes:
        pest = commodity_db.get_pest_info(code)
        if pest:
            pest_info = f"{code} ({pest.name})"
            if origin_state and origin_state in pest.present_in:
                pest_info += f" - Present in {origin_state}"
            parts.append(pest_info)
    
    return "Pests: " + ", ".join(parts) if parts else ""

def format_phylloxera_info(phylloxera_info):
    """
    Format phylloxera zone requirements into a readable string.
    This is crucial for plant material as phylloxera zones affect import conditions.
    """
    if not phylloxera_info:
        return ""
    
    parts = []
    if phylloxera_info.pez_requirements:
        parts.append(f"PEZ requirements: {phylloxera_info.pez_requirements}")
    if phylloxera_info.prz_requirements:
        parts.append(f"PRZ requirements: {phylloxera_info.prz_requirements}")
    if phylloxera_info.piz_requirements:
        parts.append(f"PIZ requirements: {phylloxera_info.piz_requirements}")
    
    return "\n".join(parts) if parts else ""

def format_ir_info(ir_number):
    """
    Format Import Requirement (IR) information including applicable ICAs.
    This provides structured information about specific import conditions.
    """
    ir_info = commodity_db.get_ir_info(ir_number)
    if not ir_info:
        return f"IR {ir_number}"
    
    parts = [f"IR {ir_number}: {ir_info.title}"]
    
    if ir_info.is_revoked:
        parts.append("(REVOKED)")
    elif ir_info.applicable_icas:
        ica_parts = []
        for ica in ir_info.applicable_icas:
            if ica.status == "Accepted":
                ica_parts.append(f"{ica.number}: {ica.title}")
        if ica_parts:
            parts.append("Applicable ICAs:")
            parts.extend(f"- {ica}" for ica in ica_parts)
    
    return "\n".join(parts)

def tas_manual_lookup(query: str, origin_state: Optional[str] = None) -> str:
    """
    Main lookup function that combines structured data with semantic search.
    
    The process is:
    1. First try to find exact match in structured commodity database
    2. If found, use that to construct a precise query for the manual
    3. Otherwise fall back to semantic search
    
    This two-step approach ensures:
    - Accurate matching of known commodities
    - Graceful fallback for unknown or ambiguous terms
    - Context-aware responses based on origin state
    
    Args:
        query: The commodity to look up
        origin_state: Optional state of origin (e.g., "NSW", "VIC")
    """
    q = query.lower().strip()
    
    # Try exact match first
    commodity = commodity_db.lookup(q)
    if commodity:
        # Construct precise query based on structured data
        query_parts = [f"Import Requirements for {commodity.name}"]
        
        # Add origin state if provided
        if origin_state:
            query_parts.append(f"from {origin_state}")
            
            # Add state-specific pest information
            state_pests = commodity_db.get_pests_by_state(origin_state)
            if state_pests:
                pest_codes = {pest.code for pest in state_pests}
                query_parts.append(format_pest_info(pest_codes, origin_state))
        
        # Add commodity type context
        if commodity.commodity_type == CommodityType.FRUIT:
            query_parts.append("(Fruit)")
            if origin_state:
                fruit_flies = commodity_db.get_fruit_flies_by_state(origin_state)
                if fruit_flies:
                    query_parts.append("Fruit Fly Host")
                    for fly in fruit_flies:
                        if fly.code == "QFF" and commodity.qff_host:
                            query_parts.append("QFF host")
                        elif fly.code == "MFF" and commodity.mff_host:
                            query_parts.append("MFF host")
        elif commodity.commodity_type == CommodityType.PLANT:
            query_parts.append("(Plant/Nursery Stock)")
            if origin_state:
                phylloxera = commodity_db.get_phylloxera_by_state(origin_state)
                if phylloxera and commodity.phylloxera_info:
                    query_parts.append("Phylloxera Requirements:\n" + format_phylloxera_info(commodity.phylloxera_info))
        elif commodity.commodity_type == CommodityType.SEED:
            query_parts.append("(Seed)")
        elif commodity.commodity_type == CommodityType.GRAIN:
            query_parts.append("(Grain)")
        elif commodity.commodity_type == CommodityType.EQUIPMENT:
            query_parts.append("(Equipment/Machinery)")
        
        if commodity.ir_numbers:
            ir_details = [format_ir_info(ir) for ir in commodity.ir_numbers]
            query_parts.append("IRs:\n" + "\n".join(f"- {ir}" for ir in ir_details))
        
        if commodity.pests:
            query_parts.append(format_pest_info(commodity.pests, origin_state))
        
        if commodity.restricted_entry:
            query_parts.append("Restricted Entry")
        
        # Add specific request for section and page numbers
        q = "Refer only to the Tasmanian PQM. Include specific section numbers and page numbers for each requirement. " + " | ".join(query_parts)
    else:
        # Try fuzzy search
        matches = commodity_db.search(q)
        if matches:
            # Use the first match to construct query
            commodity = matches[0]
            q = f"Refer only to the Tasmanian PQM. Include specific section numbers and page numbers. Import Requirements for {commodity.name}"
            if origin_state:
                q += f" from {origin_state}"
        else:
            q = f"Refer only to the Tasmanian PQM. Include specific section numbers and page numbers. {q}"

    # Use the RetrievalQA chain to get an answer
    result = qa_chain_tas.invoke({"query": q})
    answer = result["result"]
    
    # Add source document information if available
    if "source_documents" in result and result["source_documents"]:
        sources = []
        for doc in result["source_documents"]:
            if hasattr(doc.metadata, "page") and hasattr(doc.metadata, "source"):
                sources.append(f"Page {doc.metadata.page} in {doc.metadata.source}")
        if sources:
            answer += "\n\nSources: " + "; ".join(sources)
    
    return answer

# Expose as LangChain tool for use in the agent
# This tool can be used by the agent to look up import requirements
# The agent will use this tool when it needs to consult the PQM
tas_manual_tool = Tool(
    name="tas_manual_lookup",
    func=tas_manual_lookup,
    description=(
        "Consult the Tasmanian Plant Quarantine Manual (PQM). "
        "Input = commodity name (e.g. 'potato', 'cut flowers'). "
        "Specify if it's a plant, fruit, seed, or equipment. "
        "Optionally specify origin state (e.g., 'NSW', 'VIC')."
    )
)
