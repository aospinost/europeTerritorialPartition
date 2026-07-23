import pandas as pd
import re
from src.config import DEFINITION_CSV, CONTINENT_FILE, POSITIONS_FILE

def CallDefinitions():
    # Load the CSV
    df = pd.read_csv(
        DEFINITION_CSV,
        sep=";",
        encoding="latin1",
        usecols=[0, 1, 2, 3, 4]
    )

    # Rename columns
    df.rename(columns={'x': 'name'}, inplace=True)

    # Force integer types
    df['province'] = df['province'].astype(int)

    df[['red', 'green', 'blue']] = (
        df[['red', 'green', 'blue']]
        .astype(int)
    )

    return df

def CallEuropeanProvinces():
    # Read continent file
    with open(CONTINENT_FILE) as f:
        content = f.read()

    # Find the Europe section
    europe_match = re.search(r"europe\s*=\s*{(.*?)}\s*$", content, re.DOTALL | re.MULTILINE)
    europe_data = europe_match.group(1)

    # Extract all province numbers
    province_ids = re.findall(r'\b\d+\b', europe_data)
    province_ids = [int(pid) for pid in province_ids]

    return province_ids

def CallProvincePositions():
    positions_file = POSITIONS_FILE
    
    # Read file content
    with open(positions_file, 'r', encoding='latin1') as f:
        content = f.read()
    
    # Split into province blocks
    province_blocks = re.findall(r'(\d+)\s*=\s*{(.*?)(?=\n\d+\s*=|$)', content, re.DOTALL)
    
    positions = {}
    
    for pid, block in province_blocks:
        # First try to find 'unit'
        match = re.search(r'unit\s*=\s*{[^}]*?x\s*=\s*([\d.]+)[^}]*?y\s*=\s*([\d.]+)', block, re.DOTALL)
        
        if not match:
            # Fallback: text_position
            match = re.search(r'text_position\s*=\s*{[^}]*?x\s*=\s*([\d.]+)[^}]*?y\s*=\s*([\d.]+)', block, re.DOTALL)
        if not match:
            # Fallback: factory
            match = re.search(r'factory\s*=\s*{[^}]*?x\s*=\s*([\d.]+)[^}]*?y\s*=\s*([\d.]+)', block, re.DOTALL)
        
        if match:
            x, y = match.groups()
            positions[int(pid)] = (float(x), float(y))
        else:
            # No coordinates found at all
            positions[int(pid)] = (None, None)
    
    return positions

def IdentifyCoastalProvinces():
    positions_file = POSITIONS_FILE
    
    with open(positions_file, 'r', encoding='latin1') as f:
        content = f.read()
    
    province_blocks = re.findall(r'(\d+)\s*=\s*{(.*?)(?=\n\d+\s*=|$)', content, re.DOTALL)
    
    coastal = {}
    
    for pid, block in province_blocks:
        # Search for naval_base anywhere inside building_position
        match = re.search(
            r'building_position\s*=\s*{.*?naval_base\s*=\s*{',
            block,
            re.DOTALL
        )
        coastal[int(pid)] = bool(match)
    
    return coastal