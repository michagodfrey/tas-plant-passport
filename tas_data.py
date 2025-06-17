# tas_data.py
# This file defines the structured data models and database for Tasmanian import requirements
# It provides a foundation for accurate, deterministic lookups of:
# - Commodity types and their requirements
# - Pest presence by state
# - Import Requirements (IRs) and their ICA equivalents
# - Phylloxera zone requirements
# - Fruit fly host status

from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass
from pathlib import Path
import json
from enum import Enum
from data.table_1 import pest_info  # Import the pest information

class CommodityType(Enum):
    """Enumeration of possible commodity types.
    This helps categorize items and apply appropriate import rules."""
    FRUIT = "fruit"        # Fresh fruits and vegetables
    PLANT = "plant"        # Nursery stock and plants
    SEED = "seed"          # Seeds for planting
    GRAIN = "grain"        # Grains and cereals
    EQUIPMENT = "equipment" # Machinery and equipment
    OTHER = "other"        # Miscellaneous items

@dataclass
class PestInfo:
    """Information about a pest or disease.
    Tracks presence by state and categorizes the type of pest."""
    code: str              # Short code (e.g., "QFF", "MFF", "GP")
    name: str              # Full name of the pest
    present_in: List[str]  # List of states where the pest is present
    is_fruit_fly: bool = False    # Whether it's a fruit fly species
    is_phylloxera: bool = False  # Whether it's phylloxera
    is_weed: bool = False        # Whether it's a declared weed
    is_gm: bool = False          # Whether it's genetically modified

@dataclass
class ICAInfo:
    """Information about an Interstate Certification Assurance (ICA).
    ICAs are agreements between states about import conditions."""
    number: str            # ICA number (e.g., "ICA-1")
    title: str            # Full title of the ICA
    status: str           # Current status ("Accepted", "Not Accepted", etc.)
    applicable_irs: List[str]  # List of IRs this ICA applies to

@dataclass
class IRInfo:
    """Information about an Import Requirement (IR).
    IRs are the specific conditions that must be met for import."""
    number: str           # IR number (e.g., "IR-1")
    title: str           # Full title of the IR
    applicable_icas: List[ICAInfo]  # List of ICAs that apply to this IR
    is_revoked: bool = False  # Whether this IR is no longer in force

@dataclass
class PhylloxeraZoneInfo:
    """Information about phylloxera zone requirements.
    Different zones (PEZ, PRZ, PIZ) have different import conditions."""
    pez_requirements: Optional[str] = None  # Phylloxera Exclusion Zone
    prz_requirements: Optional[str] = None  # Phylloxera Risk Zone
    piz_requirements: Optional[str] = None  # Phylloxera Infested Zone

@dataclass
class CommodityInfo:
    """Structured information about a commodity's import requirements.
    This is the core data structure that ties everything together."""
    name: str             # Common name of the commodity
    commodity_type: CommodityType  # Type of commodity
    botanical_name: Optional[str] = None  # Scientific name
    ir_numbers: List[str] = None  # List of applicable IRs
    pests: Set[str] = None  # Set of relevant pest codes
    is_fruit_fly_host: bool = False  # Whether it's a fruit fly host
    qff_host: bool = False  # Specifically a Queensland Fruit Fly host
    mff_host: bool = False  # Specifically a Mediterranean Fruit Fly host
    restricted_entry: bool = False  # Whether it has special restrictions
    phylloxera_info: Optional[PhylloxeraZoneInfo] = None  # Phylloxera requirements
    parent_commodity: Optional[str] = None  # Broader category (e.g., "citrus" for "orange")
    alternative_names: List[str] = None  # Other names for this commodity

class CommodityDatabase:
    """Main database class that manages all structured data.
    Provides methods for loading data and performing lookups."""
    
    def __init__(self):
        """Initialize the database and load all data sources."""
        self.commodities: Dict[str, CommodityInfo] = {}  # Commodity lookup table
        self.ir_info: Dict[str, IRInfo] = {}           # IR lookup table
        self.ica_info: Dict[str, ICAInfo] = {}         # ICA lookup table
        self.pest_info: Dict[str, PestInfo] = {}       # Pest lookup table
        self._load_pest_info()  # Load pest information first
        self._load_data()       # Then load all other data
    
    def _load_pest_info(self):
        """Load pest information from table_1.py.
        This provides the foundation for pest-related lookups."""
        for code, info in pest_info.items():
            # Determine pest type based on code
            is_fruit_fly = code in ["QFF", "MFF"]
            is_phylloxera = code == "GP"
            is_weed = code == "DW"
            is_gm = code == "GMP"
            
            self.pest_info[code] = PestInfo(
                code=code,
                name=info["name"],
                present_in=info["present_in"],
                is_fruit_fly=is_fruit_fly,
                is_phylloxera=is_phylloxera,
                is_weed=is_weed,
                is_gm=is_gm
            )
    
    def _load_cleaned_data(self, file_path: Path):
        """Load data from a cleaned JSON file.
        Different tables are processed differently based on their content."""
        with open(file_path) as f:
            data = json.load(f)
        
        table_name = data["name"]
        rows = data["rows"]
        
        # Route to appropriate processor based on table type
        if "SCHEDULE-1A-FRUIT-FLY-HOST-FRUIT" in table_name:
            self._process_fruit_fly_hosts(rows)
        elif "SCHEDULE-1-Hosts-of-Grape-Phylloxera" in table_name:
            self._process_phylloxera_hosts(rows)
        elif "Table3-Index-of-IRs-for-Seeds-and-Grains" in table_name:
            self._process_seeds_and_grains(rows)
        elif "Table4-Index-of-IRs-for-Other-Restricted-matter" in table_name:
            self._process_other_restricted_matter(rows)
        elif "Cross-Index-of-Tasmanian-IRs-by-ICA-Equivalent" in table_name:
            self._process_cross_index(rows)
    
    def _process_fruit_fly_hosts(self, rows: List[Dict[str, str]]):
        """Process fruit fly host data.
        Identifies which commodities are hosts for different fruit fly species."""
        for row in rows:
            if not row.get("Botanical Name") or not row.get("Common Name"):
                continue
                
            name = row["Common Name"].strip()
            botanical = row["Botanical Name"].strip()
            is_qff = "QFF" in row.get("QFF", "")
            is_mff = "MFF" in row.get("MFF", "")
            restricted = "restricted entry" in botanical.lower()
            
            # Determine commodity type
            commodity_type = CommodityType.FRUIT
            if "seed" in name.lower() or "seed" in botanical.lower():
                commodity_type = CommodityType.SEED
            
            self.commodities[name.lower()] = CommodityInfo(
                name=name,
                botanical_name=botanical,
                commodity_type=commodity_type,
                is_fruit_fly_host=True,
                qff_host=is_qff,
                mff_host=is_mff,
                restricted_entry=restricted
            )
    
    def _process_phylloxera_hosts(self, rows: List[Dict[str, str]]):
        """Process phylloxera host data.
        Identifies which plants are hosts for phylloxera and their zone requirements."""
        for row in rows:
            if not row.get("Host"):
                continue
                
            name = row["Host"].strip()
            if name.lower() in self.commodities:
                self.commodities[name.lower()].phylloxera_info = PhylloxeraZoneInfo(
                    pez_requirements=row.get("PEZ Requirements"),
                    prz_requirements=row.get("PRZ Requirements"),
                    piz_requirements=row.get("PIZ Requirements")
                )
    
    def _process_seeds_and_grains(self, rows: List[Dict[str, str]]):
        """Process seeds and grains data.
        Identifies import requirements for seeds and grains."""
        for row in rows:
            if not row.get("Commodity"):
                continue
                
            name = row["Commodity"].strip()
            irs = [ir.strip() for ir in row.get("IR", "").split(",")] if row.get("IR") else []
            pests = set(pest.strip() for pest in row.get("Pests", "").split(",")) if row.get("Pests") else set()
            
            # Determine if it's a seed or grain
            commodity_type = CommodityType.SEED if "seed" in name.lower() else CommodityType.GRAIN
            
            if name.lower() in self.commodities:
                # Update existing entry
                self.commodities[name.lower()].ir_numbers = irs
                self.commodities[name.lower()].pests = pests
                self.commodities[name.lower()].commodity_type = commodity_type
            else:
                # Create new entry
                self.commodities[name.lower()] = CommodityInfo(
                    name=name,
                    commodity_type=commodity_type,
                    ir_numbers=irs,
                    pests=pests
                )
    
    def _process_other_restricted_matter(self, rows: List[Dict[str, str]]):
        """Process other restricted matter data.
        Handles miscellaneous items with special import requirements."""
        for row in rows:
            if not row.get("Commodity"):
                continue
                
            name = row["Commodity"].strip()
            irs = [ir.strip() for ir in row.get("IR", "").split(",")] if row.get("IR") else []
            pests = set(pest.strip() for pest in row.get("Pests", "").split(",")) if row.get("Pests") else set()
            
            # Determine commodity type
            commodity_type = CommodityType.EQUIPMENT
            if "seed" in name.lower():
                commodity_type = CommodityType.SEED
            elif "plant" in name.lower():
                commodity_type = CommodityType.PLANT
            
            if name.lower() in self.commodities:
                # Update existing entry
                self.commodities[name.lower()].ir_numbers = irs
                self.commodities[name.lower()].pests = pests
                self.commodities[name.lower()].commodity_type = commodity_type
            else:
                # Create new entry
                self.commodities[name.lower()] = CommodityInfo(
                    name=name,
                    commodity_type=commodity_type,
                    ir_numbers=irs,
                    pests=pests
                )
    
    def _process_cross_index(self, rows: List[Dict[str, str]]):
        """Process cross-index data.
        Links Import Requirements (IRs) with their ICA equivalents."""
        for row in rows:
            if not row.get("IR Number"):
                continue
                
            ir_number = row["IR Number"].strip()
            ir_title = row.get("IR Title", "").strip()
            ica_info = row.get("ICA Equivalent", "").strip()
            
            # Create IR info
            self.ir_info[ir_number] = IRInfo(
                number=ir_number,
                title=ir_title,
                applicable_icas=[],
                is_revoked="REVOKED" in ir_title
            )
            
            # Process ICA information
            if ica_info and "ICA-" in ica_info:
                ica_parts = ica_info.split(":")
                if len(ica_parts) >= 2:
                    ica_number = ica_parts[0].strip()
                    ica_title = ica_parts[1].strip()
                    
                    ica = ICAInfo(
                        number=ica_number,
                        title=ica_title,
                        status="Accepted",  # Default, update based on data
                        applicable_irs=[ir_number]
                    )
                    self.ica_info[ica_number] = ica
                    self.ir_info[ir_number].applicable_icas.append(ica)
    
    def _load_data(self):
        """Load and merge data from all cleaned tables.
        This builds the complete database from all available sources."""
        cleaned_dir = Path("mnt/data/cleaned")
        if not cleaned_dir.exists():
            raise RuntimeError("Cleaned data directory not found. Run data_cleaner.py first.")
        
        for file_path in cleaned_dir.glob("*_cleaned.json"):
            try:
                self._load_cleaned_data(file_path)
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
    
    # Public lookup methods
    
    def get_pest_info(self, pest_code: str) -> Optional[PestInfo]:
        """Get information about a specific pest."""
        return self.pest_info.get(pest_code)
    
    def get_pests_by_state(self, state: str) -> List[PestInfo]:
        """Get all pests present in a specific state."""
        return [
            pest for pest in self.pest_info.values()
            if state in pest.present_in
        ]
    
    def get_fruit_flies_by_state(self, state: str) -> List[PestInfo]:
        """Get fruit flies present in a specific state."""
        return [
            pest for pest in self.pest_info.values()
            if pest.is_fruit_fly and state in pest.present_in
        ]
    
    def get_phylloxera_by_state(self, state: str) -> List[PestInfo]:
        """Get phylloxera presence in a specific state."""
        return [
            pest for pest in self.pest_info.values()
            if pest.is_phylloxera and state in pest.present_in
        ]
    
    def get_weeds_by_state(self, state: str) -> List[PestInfo]:
        """Get declared weeds present in a specific state."""
        return [
            pest for pest in self.pest_info.values()
            if pest.is_weed and state in pest.present_in
        ]
    
    def get_gm_by_state(self, state: str) -> List[PestInfo]:
        """Get GM presence in a specific state."""
        return [
            pest for pest in self.pest_info.values()
            if pest.is_gm and state in pest.present_in
        ]
    
    def lookup(self, query: str) -> Optional[CommodityInfo]:
        """Look up a commodity by name (case-insensitive)."""
        query = query.lower().strip()
        return self.commodities.get(query)
    
    def search(self, query: str) -> List[CommodityInfo]:
        """Search for commodities containing the query string."""
        query = query.lower().strip()
        return [
            info for name, info in self.commodities.items()
            if query in name
        ]
    
    def get_ir_info(self, ir_number: str) -> Optional[IRInfo]:
        """Get information about a specific IR."""
        return self.ir_info.get(ir_number)
    
    def get_ica_info(self, ica_number: str) -> Optional[ICAInfo]:
        """Get information about a specific ICA."""
        return self.ica_info.get(ica_number)

# Create singleton instance for use throughout the application
commodity_db = CommodityDatabase() 