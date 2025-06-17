import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import re

@dataclass
class CleanedTable:
    """Structured representation of a cleaned table"""
    name: str
    headers: List[str]
    rows: List[Dict[str, str]]
    metadata: Dict[str, str]

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing characters"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    # Normalize dashes
    text = text.replace('-', '-').replace('—', '-')
    # Normalize ellipsis
    text = text.replace('…', '...')
    return text

def extract_headers(row: List[str]) -> List[str]:
    """Extract and clean headers from a row"""
    return [clean_text(h) for h in row if h]

def clean_row(row: List[str], headers: List[str]) -> Dict[str, str]:
    """Clean a row and convert it to a dictionary"""
    return {
        headers[i]: clean_text(cell)
        for i, cell in enumerate(row)
        if i < len(headers) and cell
    }

def process_raw_json(file_path: Path) -> CleanedTable:
    """Process a raw JSON file and return a cleaned table"""
    with open(file_path) as f:
        raw_data = json.load(f)
    
    # Extract table name from filename
    table_name = file_path.stem.replace('_raw', '')
    
    # Initialize metadata
    metadata = {
        "source_file": file_path.name,
        "page_count": len(raw_data)
    }
    
    # Process all pages
    all_rows = []
    headers = []
    
    for page in raw_data:
        if not page.get("rows"):
            continue
            
        # Find header row (usually first or second row)
        for row in page["rows"][:2]:
            if any("import requirement" in cell.lower() for cell in row if cell):
                headers = extract_headers(row)
                break
        
        # If no headers found, use first non-empty row
        if not headers and page["rows"]:
            headers = extract_headers(page["rows"][0])
        
        # Process data rows
        for row in page["rows"]:
            if not row or not any(row):  # Skip empty rows
                continue
            if headers:  # Only process if we have headers
                cleaned_row = clean_row(row, headers)
                if cleaned_row:  # Only add non-empty rows
                    all_rows.append(cleaned_row)
    
    return CleanedTable(
        name=table_name,
        headers=headers,
        rows=all_rows,
        metadata=metadata
    )

def save_cleaned_data(table: CleanedTable, output_dir: Path):
    """Save cleaned data to a JSON file"""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{table.name}_cleaned.json"
    
    with open(output_file, 'w') as f:
        json.dump(asdict(table), f, indent=2)

def clean_all_tables():
    """Clean all raw JSON files in the data directory"""
    data_dir = Path("mnt/data")
    output_dir = Path("mnt/data/cleaned")
    
    # Process all raw JSON files
    for file_path in data_dir.glob("*_raw.json"):
        print(f"Processing {file_path.name}...")
        try:
            cleaned_table = process_raw_json(file_path)
            save_cleaned_data(cleaned_table, output_dir)
            print(f"Successfully cleaned {file_path.name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    clean_all_tables() 