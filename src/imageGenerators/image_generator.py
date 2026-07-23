from PIL import Image, ImageDraw
import numpy as np
from src.config import PROVINCES_BMP, COLORED_MAPS, SAT_MAPS, PROVINCES_BMP_ORIGINAL, DIST
from src.graph.data import LoadCultureColors
from src.graph.graph import *
from src.graph.metrics import ApplySatisfactionScores

def ShowMapBySelectedProvinces(df, province_ids, save_path="geographicMap.bmp", padding = 20):
    # Filter only European provinces
    df_europe = df[df['province'].isin(province_ids)]
    
    # Load map
    img = Image.open(PROVINCES_BMP).convert('RGB')
    img_array = np.array(img)

    # Temporary fix: flip image
    img_array = np.flipud(img_array)  # first flip

    # Ensure RGB are integers
    colors = df_europe[['red', 'green', 'blue']].astype(int).values

    # Vectorize by creating a single integer per pixel
    img_flat = img_array[:,:,0].astype(np.uint32) << 16
    img_flat += img_array[:,:,1].astype(np.uint32) << 8
    img_flat += img_array[:,:,2].astype(np.uint32)

    # Same for colors
    color_values = (colors[:,0].astype(np.uint32) << 16) + (colors[:,1].astype(np.uint32) << 8) + colors[:,2].astype(np.uint32)

    # Create mask efficiently
    mask = np.isin(img_flat, color_values)

# Create output image
    output = np.ones_like(img_array) * 255  # white background
    output[mask] = img_array[mask]
    
    # --------------------------------------------------------
    # Calculate Bounding Box of Masked Provinces
    # --------------------------------------------------------
    # np.where returns (row_indices, col_indices) which correspond to (y, x)
    y_indices, x_indices = np.where(mask)

    if len(x_indices) == 0 or len(y_indices) == 0:
        # Fallback safeguard: if no provinces matched, default to the whole image
        min_x, max_x = 0, output.shape[1]
        min_y, max_y = 0, output.shape[0]
    else:
        min_x, max_x = np.min(x_indices), np.max(x_indices)
        min_y, max_y = np.min(y_indices), np.max(y_indices)

    # --------------------------------------------------------
    # Add padding
    # --------------------------------------------------------

    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)

    max_x = min(output.shape[1], max_x + padding)
    max_y = min(output.shape[0], max_y + padding)

    # --------------------------------------------------------
    # Crop image
    # --------------------------------------------------------

    cropped = output[min_y:max_y, min_x:max_x]

    # --------------------------------------------------------
    # Save BMP
    # --------------------------------------------------------

    result = Image.fromarray(
        cropped.astype(np.uint8)
    )

    result.save(DIST / save_path, format="BMP")

def ShowMapWithSelectedVerticesOnTop(df, province_ids):
    """
    Plots vertices on the European provinces map using unit coordinates.
    df: DataFrame with 'province', 'unit_x', 'unit_y', etc.
    province_ids: list of European provinces
    """
    # Filter European provinces
    df_europe = df[df['province'].isin(province_ids)]
    
    # Load map and flip vertically
    img = Image.open(PROVINCES_BMP).convert('RGB')
    img_array = np.flipud(np.array(img))  # flip vertically
    
    img_with_vertices = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img_with_vertices)
    
    # Draw a small filled circle for each province's unit coordinates
    radius = 1  # smaller, prudent size
    for _, row in df_europe.iterrows():
        x, y = row['unit_x'], row['unit_y']
        if x is not None and y is not None:
            # Flip y to match flipped image
            y_flipped = img_array.shape[0] - y
            draw.ellipse(
                (x-radius, y_flipped-radius, x+radius, y_flipped+radius),
                fill='white'  # filled dot
            )
    
    # Show image
    img_with_vertices.show(title="European Provinces with Vertices")
    return

def ShowMapWithColoring(
    df,
    partition,
    save_path="partitionTemp.bmp",
    padding=20
):

    print("\n=== RENDERING PARTITION MAP ===")

    # --------------------------------------------------------
    # Load country metadata
    # --------------------------------------------------------

    metadata = LoadCountryMetadata()

    # --------------------------------------------------------
    # Load province bitmap
    # --------------------------------------------------------

    img = Image.open(PROVINCES_BMP_ORIGINAL).convert('RGB')

    img_array = np.array(img)

    # --------------------------------------------------------
    # Flip vertically
    # --------------------------------------------------------

    img_array = np.flipud(img_array)

    # --------------------------------------------------------
    # Build packed province color map
    # --------------------------------------------------------

    province_color_to_id = {}

    for _, row in df.iterrows():

        packed = (
            (int(row['red']) << 16)
            + (int(row['green']) << 8)
            + int(row['blue'])
        )

        province_color_to_id[packed] = row['province']

    # --------------------------------------------------------
    # Pack image pixels
    # --------------------------------------------------------

    img_flat = (
        img_array[:, :, 0].astype(np.uint32) << 16
    )

    img_flat += (
        img_array[:, :, 1].astype(np.uint32) << 8
    )

    img_flat += (
        img_array[:, :, 2].astype(np.uint32)
    )

    # --------------------------------------------------------
    # Output image
    # --------------------------------------------------------

    output = np.ones_like(img_array) * 255

    # --------------------------------------------------------
    # Bounding box initialization
    # --------------------------------------------------------

    min_x = img_array.shape[1]
    min_y = img_array.shape[0]

    max_x = 0
    max_y = 0

    # --------------------------------------------------------
    # Recolor province-by-province
    # --------------------------------------------------------

    unique_colors = np.unique(img_flat)

    for packed_color in unique_colors:

        province = province_color_to_id.get(
            int(packed_color)
        )

        if province is None:
            continue

        # ----------------------------------------------------
        # Province owner
        # ----------------------------------------------------

        owner = partition.country_of(province)

        if owner is None:
            continue

        # ----------------------------------------------------
        # Country color
        # ----------------------------------------------------

        if owner not in metadata:
            continue

        color = metadata[owner]['color']

        rgb = (
            int(color[0] * 255),
            int(color[1] * 255),
            int(color[2] * 255)
        )

        # ----------------------------------------------------
        # Province mask
        # ----------------------------------------------------

        mask = (img_flat == packed_color)

        output[mask] = rgb

        # ----------------------------------------------------
        # Update bounding box
        # ----------------------------------------------------

        ys, xs = np.where(mask)

        if len(xs) == 0:
            continue

        min_x = min(min_x, xs.min())
        max_x = max(max_x, xs.max())

        min_y = min(min_y, ys.min())
        max_y = max(max_y, ys.max())

    # --------------------------------------------------------
    # Add padding
    # --------------------------------------------------------

    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)

    max_x = min(output.shape[1], max_x + padding)
    max_y = min(output.shape[0], max_y + padding)

    # --------------------------------------------------------
    # Crop image
    # --------------------------------------------------------

    cropped = output[min_y:max_y, min_x:max_x]

    # --------------------------------------------------------
    # Save BMP
    # --------------------------------------------------------

    result = Image.fromarray(
        cropped.astype(np.uint8)
    )

    result.save(COLORED_MAPS / save_path, format="BMP")

    # --------------------------------------------------------
    # Show image
    # --------------------------------------------------------

    #result.show(title="Partition Coloring")

    print(f"=== MAP SAVED TO {save_path} ===")

    return

def ShowMapWithSatisfaction(
    df: pd.DataFrame,
    partition: "Partition",
    G: nx.Graph,
    save_path: str = "satisfactionTemp.bmp",
    padding: int = 20
) -> None:
    """
    Renders and exports a high-resolution BMP satisfaction map exactly like 
    ShowMapWithColoring, passing G explicitly to ensure exact matching metrics.
    """
    print("\n=== RENDERING SATISFACTION HEATMAP MAP ===")

    # --------------------------------------------------------
    # 1. Create a clean operational copy and apply metrics
    # --------------------------------------------------------
    H = G.copy()
    partition.apply(H)
    ApplySatisfactionScores(H)

    # --------------------------------------------------------
    # 2. Load map template coordinates
    # --------------------------------------------------------
    img = Image.open(PROVINCES_BMP_ORIGINAL).convert('RGB')
    img_array = np.array(img)

    # Invert layout matching project canvas space
    img_array = np.flipud(img_array)

    # --------------------------------------------------------
    # 3. Map creation & Bitwise pixel array packing
    # --------------------------------------------------------
    province_color_to_id = {}
    for _, row in df.iterrows():
        packed = (
            (int(row['red']) << 16)
            + (int(row['green']) << 8)
            + int(row['blue'])
        )
        province_color_to_id[packed] = int(row['province'])

    img_flat = (img_array[:, :, 0].astype(np.uint32) << 16)
    img_flat += (img_array[:, :, 1].astype(np.uint32) << 8)
    img_flat += img_array[:, :, 2].astype(np.uint32)

    # Output array generation (Defaulting to white backdrop layout)
    output = np.ones_like(img_array) * 255

    # Crop frame coordinates
    min_x, min_y = img_array.shape[1], img_array.shape[0]
    max_x, max_y = 0, 0

    # --------------------------------------------------------
    # 4. Process and recolor pixels province-by-province
    # --------------------------------------------------------
    unique_colors = np.unique(img_flat)

    for packed_color in unique_colors:
        province = province_color_to_id.get(int(packed_color))
        if province is None:
            continue

        owner = partition.country_of(province)
        if owner is None:
            continue

        # Extract satisfaction calculations computed with real populations
        node_data = H.nodes.get(province, {})
        satisfaction = node_data.get('satisfaction', 0.0)
        
        # Enforce strict 0.0 to 1.0 color boundary conditions
        satisfaction = max(0.0, min(1.0, satisfaction))

        # Precision Red-to-Green Gradient Interpolation
        red = int((1.0 - satisfaction) * 255)
        green = int(satisfaction * 255)
        blue = 0
        rgb = (red, green, blue)

        # Apply generated graphics mask
        mask = (img_flat == packed_color)
        output[mask] = rgb

        # Dynamically scale regional crop limits
        ys, xs = np.where(mask)
        if len(xs) == 0:
            continue

        min_x, max_x = min(min_x, xs.min()), max(max_x, xs.max())
        min_y, max_y = min(min_y, ys.min()), max(max_y, ys.max())

    # --------------------------------------------------------
    # 5. Apply dynamic frame margins & crop
    # --------------------------------------------------------
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(output.shape[1], max_x + padding)
    max_y = min(output.shape[0], max_y + padding)

    cropped = output[min_y:max_y, min_x:max_x]

    # --------------------------------------------------------
    # 6. File system serialization
    # --------------------------------------------------------
    result = Image.fromarray(cropped.astype(np.uint8))
    result.save(SAT_MAPS / save_path, format="BMP")

    # Present GUI window frame layout
    #result.show(title="Satisfaction Heatmap")

    print(f"=== MAP SAVED TO {save_path} ===")
    return

def ShowMapWithCulture(
    G: nx.Graph,
    df,
    save_path="cultureMap.bmp",
    padding=20
):

    print("\n=== RENDERING CULTURE MAP ===")

    # --------------------------------------------------------
    # Load culture colors
    # --------------------------------------------------------

    culture_colors = LoadCultureColors()

    # --------------------------------------------------------
    # Load province bitmap
    # --------------------------------------------------------

    img = Image.open(PROVINCES_BMP_ORIGINAL).convert('RGB')

    img_array = np.array(img)

    # --------------------------------------------------------
    # Flip vertically
    # --------------------------------------------------------

    img_array = np.flipud(img_array)

    # --------------------------------------------------------
    # Build packed province color map
    # --------------------------------------------------------

    province_color_to_id = {}

    for _, row in df.iterrows():

        packed = (
            (int(row['red']) << 16)
            + (int(row['green']) << 8)
            + int(row['blue'])
        )

        province_color_to_id[packed] = row['province']

    # --------------------------------------------------------
    # Pack image pixels
    # --------------------------------------------------------

    img_flat = (
        img_array[:, :, 0].astype(np.uint32) << 16
    )

    img_flat += (
        img_array[:, :, 1].astype(np.uint32) << 8
    )

    img_flat += (
        img_array[:, :, 2].astype(np.uint32)
    )

    # --------------------------------------------------------
    # Output image
    # --------------------------------------------------------

    output = np.ones_like(img_array) * 255

    # --------------------------------------------------------
    # Bounding box initialization
    # --------------------------------------------------------

    min_x = img_array.shape[1]
    min_y = img_array.shape[0]

    max_x = 0
    max_y = 0

    # --------------------------------------------------------
    # Recolor province-by-province
    # --------------------------------------------------------

    unique_colors = np.unique(img_flat)

    for packed_color in unique_colors:

        province = province_color_to_id.get(
            int(packed_color)
        )

        if province is None:
            continue

        # Province missing from graph
        if province not in G.nodes:
            continue

        node = G.nodes[province]

        # ----------------------------------------------------
        # Population data
        # ----------------------------------------------------

        population_data = node.get(
            'population',
            []
        )

        if not population_data:
            continue

        # ----------------------------------------------------
        # Sort cultures
        # ----------------------------------------------------

        populations = sorted(
            population_data,
            key=lambda x: x[1],
            reverse=True
        )

        primary_culture, primary_pop = populations[0]

        primary_color = culture_colors.get(
            primary_culture,
            (0.5, 0.5, 0.5)
        )

        primary_rgb = (
            int(primary_color[0] * 255),
            int(primary_color[1] * 255),
            int(primary_color[2] * 255)
        )

        # ----------------------------------------------------
        # Province mask
        # ----------------------------------------------------

        mask = (img_flat == packed_color)

        # ----------------------------------------------------
        # Update bounding box
        # ----------------------------------------------------

        ys, xs = np.where(mask)

        if len(xs) == 0:
            continue

        min_x = min(min_x, xs.min())
        max_x = max(max_x, xs.max())

        min_y = min(min_y, ys.min())
        max_y = max(max_y, ys.max())

        # Base fill
        output[mask] = primary_rgb

        # ----------------------------------------------------
        # Secondary culture overlay
        # ----------------------------------------------------

        if len(populations) >= 2:

            secondary_culture, secondary_pop = populations[1]

            ratio = secondary_pop / primary_pop

            # Significant minority
            if ratio > 0.5:

                secondary_color = culture_colors.get(
                    secondary_culture,
                    (0.5, 0.5, 0.5)
                )

                secondary_rgb = (
                    int(secondary_color[0] * 255),
                    int(secondary_color[1] * 255),
                    int(secondary_color[2] * 255)
                )

                # --------------------------------------------
                # Diagonal stripe pattern
                # --------------------------------------------

                ys, xs = np.where(mask)

                # Stripe settings
                stripe_spacing = 8
                stripe_width = 2

                stripe_mask = (
                    ((xs + ys) % stripe_spacing)
                    < stripe_width
                )

                output[
                    ys[stripe_mask],
                    xs[stripe_mask]
                ] = secondary_rgb

    # --------------------------------------------------------
    # Add padding
    # --------------------------------------------------------

    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)

    max_x = min(output.shape[1], max_x + padding)
    max_y = min(output.shape[0], max_y + padding)

    # --------------------------------------------------------
    # Crop image
    # --------------------------------------------------------

    cropped = output[min_y:max_y, min_x:max_x]

    # --------------------------------------------------------
    # Save BMP
    # --------------------------------------------------------

    result = Image.fromarray(
        cropped.astype(np.uint8)
    )

    result.save(DIST / save_path, format="BMP")

    print(f"=== CULTURE MAP SAVED TO {save_path} ===")

    return