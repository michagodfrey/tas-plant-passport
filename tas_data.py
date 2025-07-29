# tas_data.py
# This file defines the structured data models and database for Tasmanian fruit fly import requirements
# It provides a foundation for accurate, deterministic lookups of:
# - Fruit fly host status for commodities
# - Pest presence by state
# - ICA conditions for fruit fly hosts

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class FruitFlyInfo:
    """Information about a fruit fly species."""
    common_name: str
    acronym: str
    scientific_name: str
    hosts: List[str]
    states_present: List[Dict[str, str]]
    states_absent: List[str]

@dataclass
class CommodityInfo:
    """Structured information about a commodity's fruit fly host status."""
    name: str
    qff_host: bool = False
    mff_host: bool = False
    is_fruit_fly_host: bool = False

class FruitFlyDatabase:
    """Main database class that manages fruit fly data from pests.json."""
    
    def __init__(self):
        """Initialize the database and load fruit fly data."""
        self.fruit_flies: Dict[str, FruitFlyInfo] = {}
        self.commodities: Dict[str, CommodityInfo] = {}
        self._load_pest_data()
        self._build_commodity_index()
    
    def _load_pest_data(self):
        """Load fruit fly data from pests.json."""
        try:
            with open("data/pests.json", "r") as f:
                data = json.load(f)
            
            for pest in data["pests"]:
                # Only process fruit flies
                if pest["pest_acronym"] in ["QFF", "MFF"]:
                    self.fruit_flies[pest["pest_acronym"]] = FruitFlyInfo(
                        common_name=pest["pest_common_name"],
                        acronym=pest["pest_acronym"],
                        scientific_name=pest["scientific_name"],
                        hosts=pest["hosts"],
                        states_present=pest["states_present"],
                        states_absent=pest["states_absent"]
                    )
        except Exception as e:
            print(f"Error loading pest data: {e}")
    
    def _build_commodity_index(self):
        """Build an index of all commodities and their fruit fly host status."""
        # Get all unique hosts from both fruit flies
        all_hosts = set()
        for fruit_fly in self.fruit_flies.values():
            all_hosts.update(fruit_fly.hosts)
        
        # Create commodity entries
        for host in all_hosts:
            qff_host = host in self.fruit_flies.get("QFF", FruitFlyInfo("", "", "", [], [], [])).hosts
            mff_host = host in self.fruit_flies.get("MFF", FruitFlyInfo("", "", "", [], [], [])).hosts
            
            self.commodities[host.lower()] = CommodityInfo(
                name=host,
                qff_host=qff_host,
                mff_host=mff_host,
                is_fruit_fly_host=qff_host or mff_host
            )
    
    def get_fruit_fly_info(self, acronym: str) -> Optional[FruitFlyInfo]:
        """Get information about a specific fruit fly."""
        return self.fruit_flies.get(acronym)
    
    def is_pest_present_in_state(self, pest_acronym: str, state: str) -> bool:
        """Check if a pest is present in a specific state."""
        pest = self.fruit_flies.get(pest_acronym)
        if not pest:
            return False
        
        # Check states_present
        for state_info in pest.states_present:
            if state_info["state_code"] == state:
                return True
        
        # Check states_absent
        return state not in pest.states_absent
    
    def get_commodity_info(self, commodity_name: str) -> Optional[CommodityInfo]:
        """Get information about a commodity."""
        return self.commodities.get(commodity_name.lower())
    
    def search_commodities(self, query: str) -> List[CommodityInfo]:
        """Search for commodities containing the query string."""
        query = query.lower().strip()
        return [
            info for name, info in self.commodities.items()
            if query in name
        ]
    
    def get_fruit_fly_hosts_for_state(self, state: str) -> Dict[str, List[str]]:
        """Get all fruit fly hosts that are relevant for a specific state."""
        result = {"QFF": [], "MFF": []}
        
        for commodity_name, commodity_info in self.commodities.items():
            if commodity_info.qff_host and self.is_pest_present_in_state("QFF", state):
                result["QFF"].append(commodity_info.name)
            if commodity_info.mff_host and self.is_pest_present_in_state("MFF", state):
                result["MFF"].append(commodity_info.name)
        
        return result
    
    def assess_fruit_fly_risk(self, commodity_name: str, origin_state: str) -> Dict[str, any]:
        """Assess fruit fly risk for a commodity from a specific state."""
        commodity = self.get_commodity_info(commodity_name)
        if not commodity:
            return {"error": f"Commodity '{commodity_name}' not found"}
        
        risk_assessment = {
            "commodity": commodity.name,
            "origin_state": origin_state,
            "is_fruit_fly_host": commodity.is_fruit_fly_host,
            "qff_risk": False,
            "mff_risk": False,
            "risk_details": []
        }
        
        if commodity.qff_host:
            qff_present = self.is_pest_present_in_state("QFF", origin_state)
            risk_assessment["qff_risk"] = qff_present
            if qff_present:
                risk_assessment["risk_details"].append(
                    f"{commodity.name} is a Queensland Fruit Fly host and QFF is present in {origin_state}"
                )
        
        if commodity.mff_host:
            mff_present = self.is_pest_present_in_state("MFF", origin_state)
            risk_assessment["mff_risk"] = mff_present
            if mff_present:
                risk_assessment["risk_details"].append(
                    f"{commodity.name} is a Mediterranean Fruit Fly host and MFF is present in {origin_state}"
                )
        
        return risk_assessment

# Create singleton instance for use throughout the application
fruit_fly_db = FruitFlyDatabase() 