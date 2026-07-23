import pandas as pd
from PIL import Image
import numpy as np
from src.config import PROVINCES_BMP, EDGE_CSV
from src.parsers.map_parser import *

def CreateProvinceEdges(df, province_ids):
    """
    Create a DataFrame of all province pairs that share a border,
    but only for the given province_ids (subset of provinces).
    """
    # Filter dataframe to the region of interest
    df_region = df[df['province'].isin(province_ids)].copy()
    
    # Load full map
    img = Image.open(PROVINCES_BMP).convert('RGB')
    img_array = np.array(img)

    # Convert RGB to single integer per pixel
    reds   = img_array[:,:,0].astype(np.uint32) << 16
    greens = img_array[:,:,1].astype(np.uint32) << 8
    blues  = img_array[:,:,2].astype(np.uint32)
    img_flat = reds + greens + blues

    # Map region colors to province IDs
    reds_r   = df_region['red'].to_numpy(dtype=np.uint32)
    greens_r = df_region['green'].to_numpy(dtype=np.uint32)
    blues_r  = df_region['blue'].to_numpy(dtype=np.uint32)
    df_region['color_val'] = (reds_r << 16) + (greens_r << 8) + blues_r
    color_to_province = dict(zip(df_region['color_val'], df_region['province']))

    # Create a province map: pixels outside the region get 0
    province_map = np.vectorize(lambda c: color_to_province.get(c, 0))(img_flat)

    # Scan neighbors for edges
    edges = set()
    H, W = province_map.shape
    for y in range(H):
        for x in range(W):
            pid = province_map[y, x]
            if pid == 0:
                continue
            # Check 4 neighbors
            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = y+dy, x+dx
                if 0 <= ny < H and 0 <= nx < W:
                    n_pid = province_map[ny, nx]
                    if n_pid != 0 and n_pid != pid:
                        edges.add(tuple(sorted((pid, n_pid))))

    edges_df = pd.DataFrame(list(edges), columns=['province_1','province_2'])
    return edges_df

def ExportEdges(edges_df):
    edges_df.to_csv(EDGE_CSV, index=False)
    print(f"Exported {len(edges_df)} edges for Europe.")