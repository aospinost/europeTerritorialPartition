from src.config import VERTEX_CSV, IMPUTATED_VERTEX_CSV
from src.parsers.map_parser import *

def CreateVertices():
    df = CallDefinitions()
    positions = CallProvincePositions()
    coastal_map = IdentifyCoastalProvinces()

    # Create new columns for unit coordinates
    df['unit_x'] = df['province'].map(lambda pid: positions.get(pid, None)[0] if positions.get(pid, None) else None)
    df['unit_y'] = df['province'].map(lambda pid: positions.get(pid, None)[1] if positions.get(pid, None) else None)

    # Add a True/False column
    df['coastal'] = df['province'].map(lambda pid: coastal_map.get(pid, False))

    return df

def ExportVertices(df, province_ids):
    vertex_df = df[df['province'].isin(province_ids)].copy()
    vertex_df.to_csv(VERTEX_CSV, index=False)
    print(f"Exported {len(vertex_df)} vertices for Europe.")
    return

def ImportVertices():
    df = pd.read_csv(IMPUTATED_VERTEX_CSV)
    
    return df