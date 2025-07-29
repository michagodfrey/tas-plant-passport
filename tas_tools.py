# tas_tools.py
# This file creates a LangChain Tool that provides structured answers about Tasmanian fruit fly import requirements
# It uses the simplified fruit fly database to assess risk and provide ICA conditions

from langchain.agents import Tool
from tas_data import fruit_fly_db
from typing import Optional

def _normalize_commodity_name(commodity_name: str) -> str:
    """
    Normalize commodity names to handle plurals and common variations.
    This converts common plural forms to singular to match the database.
    """
    name = commodity_name.lower().strip()
    
    # Common plural to singular mappings
    plural_to_singular = {
        # Fruits
        "apples": "apple",
        "grapes": "grape", 
        "strawberries": "strawberry",
        "bananas": "banana",
        "oranges": "sweet orange",  # Most common orange type
        "lemons": "lemon",
        "limes": "lime",
        "peaches": "peach",
        "nectarines": "nectarine",
        "plums": "plum",
        "cherries": "sweet cherry",
        "apricots": "apricot",
        "pears": "pear",
        "mangoes": "mango",
        "mangos": "mango",
        "avocados": "avocado",
        "tomatoes": "tomato",
        "capsicums": "capsicum",
        "chillies": "chilli",
        "chilis": "chilli",
        "papayas": "papaya",
        "guavas": "guava",
        "lychees": "lychee",
        "longans": "longan",
        "rambutans": "rambutan",
        "passionfruits": "passionfruit",
        "dragonfruits": "dragon fruit",
        "dragon fruits": "dragon fruit",
        "custard apples": "custard apple",
        "breadfruits": "breadfruit",
        "jackfruits": "jackfruit",
        "starfruits": "star fruit",
        "star fruits": "star fruit",
        "feijoas": "feijoa",
        "kiwifruits": "kiwifruit",
        "kiwi fruits": "kiwifruit",
        "persimmons": "persimmon",
        "figs": "fig",
        "quinces": "quince",
        "tamarillos": "tamarillo",
        "loquats": "loquat",
        "kumquats": "kumquat",
        "pomegranates": "pomegranate",
        "nashis": "nashi",
        "rollinias": "rollinia",
        "blackberries": "blackberry",
        "raspberries": "raspberry",
        "loganberries": "loganberry",
        "boysenberries": "boysenberry",
        "youngberries": "youngberry",
        "blueberries": "blueberry",
        "dates": "date",
        "olives": "olive",
        "coffee cherries": "coffee cherry",
        "coffee beans": "coffee cherry",  # Common term for coffee fruit
        
        # Vegetables
        "eggplants": "eggplant",
        "aubergines": "eggplant",
        "pepinos": "pepino",
        
        # Common variations
        "table grapes": "grape",
        "wine grapes": "grape",
        "seedless grapes": "grape",
        "red grapes": "grape",
        "white grapes": "grape",
        "green grapes": "grape",
        "black grapes": "grape",
        "sweet oranges": "sweet orange",
        "navel oranges": "sweet orange",
        "valencia oranges": "sweet orange",
        "blood oranges": "sweet orange",
        "mandarins": "mandarin",
        "tangerines": "mandarin",
        "clementines": "mandarin",
        "satsumas": "mandarin",
        "grapefruits": "grapefruit",
        "pink grapefruits": "grapefruit",
        "white grapefruits": "grapefruit",
        "red grapefruits": "grapefruit",
        "pomelos": "pummelo",
        "pummelos": "pummelo",
        "tangelos": "tangelo",
        "citrons": "citron",
        "meyer lemons": "meyer lemon",
        "rangpur limes": "rangpur lime",
        "tahitian limes": "tahitian lime",
        "seville oranges": "seville orange",
        "desert limes": "desert lime",
        "japanese plums": "japanese plum",
        "sour cherries": "sour cherry",
        "plumcots": "plumcot",
        "peacharines": "peacharine",
        "black sapotes": "black sapote",
        "white sapotes": "white sapote",
        "star apples": "star apple",
        "rose apples": "rose apple",
        "mountain apples": "mountain apple",
        "wax apples": "wax apple",
        "spanish cherries": "spanish cherry",
        "madagascar olives": "madagascar olive",
        "bourbon oranges": "bourbon orange",
        "mamey sapotes": "mamey sapote",
        "surinam cherries": "surinam cherry",
        "grumichamas": "grumichama",
        "jaboticabas": "jaboticaba",
        "monsteras": "monstera",
        "mulberries": "mulberry",
        "mock oranges": "mock orange",
        "granadillas": "granadilla",
        "cape gooseberries": "cape gooseberry",
        "abius": "abiu",
        "durians": "durian",
        "mangosteens": "mangosteen",
        "walnuts": "walnut",
        "aceroas": "acerola",
        "crab apples": "crab apple",
        "sapodillas": "sapodilla",
        "japanese persimmons": "japanese persimmon",
        "tropical almonds": "tropical almond",
        "chebulic myrobalans": "chebulic myrobalan",
        "cacaos": "cacao",
        "cashew apples": "cashew apple",
        "cherimoyas": "cherimoya",
        "pond apples": "pond apple",
        "soursops": "soursop",
        "akee apples": "akee apple",
        "babacos": "babaco",
        "natal plums": "natal plum",
        "hawthorns": "hawthorn",
        "excelsa coffees": "excelsa coffee",
        "liberian coffees": "liberian coffee",
        "robusta coffees": "robusta coffee",
        "lilly pillies": "lilly pilly",
        "jerusalem cherries": "jerusalem cherry",
        "jew plums": "jew plum",
        "jambus": "jambu",
        "tahitian limes": "tahitian lime",
        "rangpur limes": "rangpur lime",
        "meyer lemons": "meyer lemon",
        "seville oranges": "seville orange",
        "desert limes": "desert lime",
        "pummelos": "pummelo",
        "tahitian limes": "tahitian lime",
        "citrons": "citron",
        "meyer lemons": "meyer lemon",
        "grapefruits": "grapefruit",
        "mandarins": "mandarin",
        "rangpur limes": "rangpur lime",
        "sweet oranges": "sweet orange",
        "tangelos": "tangelo",
        "coffee cherries": "coffee cherry",
        "excelsa coffees": "excelsa coffee",
        "liberian coffees": "liberian coffee",
        "robusta coffees": "robusta coffee",
        "hawthorns": "hawthorn",
        "quinces": "quince",
        "tamarillos": "tamarillo",
        "persimmons": "persimmon",
        "black sapotes": "black sapote",
        "japanese persimmons": "japanese persimmon",
        "durians": "durian",
        "loquats": "loquat",
        "grumichamas": "grumichama",
        "surinam cherries": "surinam cherry",
        "longans": "longan",
        "figs": "fig",
        "kumquats": "kumquat",
        "strawberries": "strawberry",
        "mangosteens": "mangosteen",
        "dragonfruits": "dragon fruit",
        "dragon fruits": "dragon fruit",
        "walnuts": "walnut",
        "lychees": "lychee",
        "aceroas": "acerola",
        "apples": "apple",
        "crab apples": "crab apple",
        "mangoes": "mango",
        "mangos": "mango",
        "sapodillas": "sapodilla",
        "spanish cherries": "spanish cherry",
        "monsteras": "monstera",
        "mulberries": "mulberry",
        "mock oranges": "mock orange",
        "bananas": "banana",
        "jaboticabas": "jaboticaba",
        "rambutans": "rambutan",
        "madagascar olives": "madagascar olive",
        "bourbon oranges": "bourbon orange",
        "olives": "olive",
        "prickly pears": "prickly pear",
        "passionfruits": "passionfruit",
        "granadillas": "granadilla",
        "avocados": "avocado",
        "dates": "date",
        "cape gooseberries": "cape gooseberry",
        "mamey sapotes": "mamey sapote",
        "almonds": "almond",
        "apricots": "apricot",
        "sweet cherries": "sweet cherry",
        "sour cherries": "sour cherry",
        "plums": "plum",
        "plumcots": "plumcot",
        "peaches": "peach",
        "nectarines": "nectarine",
        "peacharines": "peacharine",
        "guavas": "guava",
        "pomegranates": "pomegranate",
        "nashis": "nashi",
        "pears": "pear",
        "rollinias": "rollinia",
        "blackberries": "blackberry",
        "raspberries": "raspberry",
        "loganberries": "loganberry",
        "boysenberries": "boysenberry",
        "youngberries": "youngberry",
        "tomatoes": "tomato",
        "eggplants": "eggplant",
        "pepinos": "pepino",
        "jerusalem cherries": "jerusalem cherry",
        "jew plums": "jew plum",
        "mombins": "mombin",
        "jambus": "jambu",
        "rose apples": "rose apple",
        "mountain apples": "mountain apple",
        "wax apples": "wax apple",
        "lilly pillies": "lilly pilly",
        "tropical almonds": "tropical almond",
        "chebulic myrobalans": "chebulic myrobalan",
        "cacaos": "cacao",
        "blueberries": "blueberry",
        "grapes": "grape"
    }
    
    # Check if the name is in our plural mapping
    if name in plural_to_singular:
        return plural_to_singular[name]
    
    # If not found, return the original name (might already be singular)
    return name

def fruit_fly_assessment(query: str, origin_state: Optional[str] = None) -> str:
    """
    Main assessment function for fruit fly conditions.
    
    The process is:
    1. Identify the commodity from the query
    2. Check if it's a fruit fly host
    3. Check if the origin state has the relevant fruit fly
    4. Provide appropriate ICA conditions
    
    Args:
        query: The commodity to assess (e.g., "table grapes", "apples") or "commodity, state" format
        origin_state: Optional state of origin (e.g., "NSW", "VIC", "WA")
    """
    # Handle the case where the agent passes "commodity, state" as a single string
    if "," in query and not origin_state:
        parts = query.split(",", 1)
        if len(parts) == 2:
            commodity_name = parts[0].strip()
            origin_state = parts[1].strip()
        else:
            return "ERROR: Invalid input format. Expected 'commodity, state' or separate parameters."
    else:
        commodity_name = query
    
    if not origin_state:
        return "ERROR: Origin state is required for fruit fly assessment. Please specify the state of origin."
    
    # Clean up and normalize the commodity name (handle plurals)
    commodity_name = _normalize_commodity_name(commodity_name)
    
    # Try exact match first
    commodity = fruit_fly_db.get_commodity_info(commodity_name)
    if not commodity:
        # Try search
        matches = fruit_fly_db.search_commodities(commodity_name)
        if matches:
            commodity = matches[0]
        else:
            return f"ERROR: Commodity '{commodity_name}' not found in fruit fly host database."
    
    # Assess fruit fly risk
    risk_assessment = fruit_fly_db.assess_fruit_fly_risk(commodity.name, origin_state)
    
    if "error" in risk_assessment:
        return risk_assessment["error"]
    
    # Build response
    response_parts = []
    response_parts.append(f"**Commodity**: {commodity.name}")
    response_parts.append(f"**Origin State**: {origin_state}")
    response_parts.append(f"**Destination**: Tasmania")
    response_parts.append("")
    
    # Fruit fly host status
    if commodity.is_fruit_fly_host:
        response_parts.append("**Fruit Fly Host Status**:")
        if commodity.qff_host:
            response_parts.append(f"• Queensland Fruit Fly (QFF) host: YES")
        if commodity.mff_host:
            response_parts.append(f"• Mediterranean Fruit Fly (MFF) host: YES")
        response_parts.append("")
    else:
        response_parts.append("**Fruit Fly Host Status**: NOT a fruit fly host")
        response_parts.append("")
    
    # Risk assessment
    if risk_assessment["qff_risk"] or risk_assessment["mff_risk"]:
        response_parts.append("**⚠️ FRUIT FLY RISK DETECTED**:")
        for detail in risk_assessment["risk_details"]:
            response_parts.append(f"• {detail}")
        response_parts.append("")
        
        # ICA conditions for fruit fly hosts
        response_parts.append("**Required ICA Conditions**:")
        if risk_assessment["qff_risk"]:
            response_parts.append("• **ICA-1**: Queensland Fruit Fly Hosts")
            response_parts.append("  - Must be treated with approved treatment")
            response_parts.append("  - Must have valid phytosanitary certificate")
            response_parts.append("  - Must be free from fruit fly")
        if risk_assessment["mff_risk"]:
            response_parts.append("• **ICA-2**: Mediterranean Fruit Fly Hosts")
            response_parts.append("  - Must be treated with approved treatment")
            response_parts.append("  - Must have valid phytosanitary certificate")
            response_parts.append("  - Must be free from fruit fly")
        response_parts.append("")
        
        response_parts.append("**Treatment Requirements**:")
        response_parts.append("• Cold treatment: 1°C for 14 days")
        response_parts.append("• Heat treatment: 47°C for 20 minutes")
        response_parts.append("• Fumigation: Methyl bromide or phosphine")
        response_parts.append("")
        
        response_parts.append("**Documentation Required**:")
        response_parts.append("• Phytosanitary certificate with treatment details")
        response_parts.append("• Treatment certificate")
        response_parts.append("• Notice of Intention (NOI) 24h before arrival")
        response_parts.append("")
        
    else:
        response_parts.append("**✅ NO FRUIT FLY RISK**:")
        response_parts.append("• No fruit fly hosts present in origin state")
        response_parts.append("• No specific ICA conditions required for fruit fly")
        response_parts.append("")
        
        if commodity.is_fruit_fly_host:
            response_parts.append("**Note**: While this commodity is a fruit fly host, the relevant fruit fly is not present in the origin state.")
        response_parts.append("")
    
    # Generic footer
    response_parts.append("⚠️  **Pre-entry Requirements**:")
    response_parts.append("• Lodge a *Notice of Intention (NoI) to Import* with Biosecurity Tasmania at least **24 h before the consignment arrives**")
    response_parts.append("• Attach required phytosanitary certificates")
    response_parts.append("• Ensure all treatment requirements are met")
    
    return "\n".join(response_parts)

# Expose as LangChain tool for use in the agent
fruit_fly_tool = Tool(
    name="fruit_fly_assessment",
    func=fruit_fly_assessment,
    description=(
        "Assess fruit fly conditions for importing commodities into Tasmania. "
        "Input = commodity name (e.g. 'table grapes', 'apples') or 'commodity, state' format. "
        "Specify origin state (e.g., 'NSW', 'VIC', 'WA'). "
        "Returns ICA conditions and treatment requirements."
    )
)
