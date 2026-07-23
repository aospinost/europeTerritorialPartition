import matplotlib.pyplot as plt

from matplotlib.offsetbox import (
    AnchoredOffsetbox,
    VPacker,
    HPacker,
    TextArea,
    DrawingArea
)
import matplotlib.patches as mpatches
import networkx as nx
from typing import Literal
from src.graph.data import LoadCultureColors
from src.graph.metrics import GlobalSatisfaction

def _DrawGraph(G: nx.Graph,
               color_mode: Literal['default', 'satisfaction', 'culture'] = 'default',
               global_metrics: tuple[int, int, float] | None = None,
               tags: str | list[str] | None = None,
               show_labels: bool = False) -> None:
    # TAG FILTERING
    if tags is not None:
        # Single tag -> convert to list
        if isinstance(tags, str):
            tags = [tags]
        # Keep only matching provinces
        nodes_to_keep = [
            n for n in G.nodes()
            if G.nodes[n].get('country_tag') in tags
        ]

        # Temporary visualization subgraph
        G = G.subgraph(nodes_to_keep).copy()
    
    pos = nx.get_node_attributes(G, 'pos')

    culture_colors = LoadCultureColors()
    colors = []

    # Track country colors dynamically for the legend box
    visible_countries = {}
    visible_cultures = {}

    for n in G.nodes():
        node = G.nodes[n]

        # DEFAULT COUNTRY COLORS
        if color_mode == 'default':
            colors.append(node['color'])
            node_color = node.get('color', (0.5, 0.5, 0.5))
            # Map the human-readable country name to its RGB color tuple
            if 'country' in node:
                visible_countries[node['country']] = node_color

        # SATISFACTION HEATMAP
        elif color_mode == 'satisfaction':
            satisfaction = node.get('satisfaction',0)

            # Clamp just in case
            satisfaction = max(0,min(1, satisfaction))

            # Red -> Green gradient
            red = 1 - satisfaction
            green = satisfaction
            blue = 0
            colors.append((red, green, blue))

        elif color_mode == 'culture':
            population_data = node.get('population',[])

            # No population data
            if not population_data:
                colors.append((0.5, 0.5, 0.5))

            else:
                # Largest culture
                majority_culture = max(
                    population_data,
                    key=lambda x: x[1]
                )[0]

                color = culture_colors.get(
                    majority_culture,
                    (0.5, 0.5, 0.5)
                )

                colors.append(color)
                visible_cultures[majority_culture] = color

    fig, ax = plt.subplots(figsize=(14, 10),dpi=100)

    # DRAW NODES
    nodes = nx.draw_networkx_nodes(
        G,
        pos,
        node_color=colors,
        node_size=40,
        ax=ax
    )

    # CULTURAL MINORITY OVERLAY

    if color_mode == 'culture':
        for province in G.nodes():
            node = G.nodes[province]
            population_data = node.get(
                'population',
                []
            )

            # Need at least 2 cultures
            if len(population_data) < 2: continue

            # Sort by population
            populations = sorted(
                population_data,
                key=lambda x: x[1],
                reverse=True
            )

            primary_culture, primary_pop = populations[0]

            secondary_culture, secondary_pop = populations[1]

            # Minority ratio
            ratio = secondary_pop / primary_pop

            # Significant minority
            if ratio > 0.5:
                secondary_color = (
                    culture_colors.get(
                        secondary_culture,
                        (0.5, 0.5, 0.5)
                    )
                )

                x, y = pos[province]

                # Scale dot size by ratio
                inner_size = 40 * ratio * 0.45

                ax.scatter(
                    x,
                    y,
                    s=inner_size,
                    color=secondary_color,
                    zorder=3,
                    edgecolors='black',
                    linewidths=0.2
                )

    # DRAW EDGES
    nx.draw_networkx_edges(
        G,
        pos,
        alpha=0.15,
        width=0.5,
        ax=ax
    )

    ax.set_aspect('equal')
    ax.axis('off')

    # TOOLTIP
    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(15, 15),
        textcoords="offset points",
        bbox=dict(
            boxstyle="round",
            fc="white",
            alpha=0.9
        ),
        arrowprops=dict(
            arrowstyle="->"
        )
    )

    annot.set_visible(False)
    locked = {'value': False}
    node_list = list(G.nodes())

    # UPDATE TOOLTIP
    def update_annotation(ind):
        node_index = ind["ind"][0]
        province_id = node_list[node_index]
        node = G.nodes[province_id]
        x, y = pos[province_id]
        annot.xy = (x, y)

        # Province name
        text = f"{node['name']} ({province_id})\n"

        # Country if exists
        if 'country' in node:
            text += f"Country: {node['country']}\n"

        text += "\n"

        # Population
        population_data = node.get('population',[])
        if population_data:
            total_pop = sum(pop for _, pop in population_data)
            text += f"Total Population: {total_pop}\n"

            satisfied_pops = node.get('satisfied_population')
            if satisfied_pops is not None:
                text += f"Satisfied Population: {satisfied_pops}\n"
            
            satisfaction = node.get('satisfaction')
            if satisfaction is not None:
                text += f"Satisfaction: {satisfaction:.2%}\n\n"

            for culture, pop in sorted(
                population_data,
                key=lambda x: x[1],
                reverse=True
            ):

                text += f"{culture}: {pop}\n"

        else:
            text += "No population data"

        annot.set_text(text)

    # HOVER EVENT
    def hover(event):
        if locked['value']: return

        visible = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = nodes.contains(event)
            if cont:
                update_annotation(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()

            else:
                if visible:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    def click(event):
        if event.inaxes != ax: return

        cont, ind = nodes.contains(event)
        # Clicked node -> lock tooltip
        if cont:
            update_annotation(ind)
            annot.set_visible(True)
            locked['value'] = True
            fig.canvas.draw_idle()

        # Clicked empty space -> unlock
        else:
            locked['value'] = False
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    fig.canvas.mpl_connect("button_press_event", click)

    # GLOBAL METRICS BOX
    if global_metrics is not None:
        (total_population,
         total_satisfied_population,
         satisfaction_score) = global_metrics

        metrics_text = (
            f"Total Population: "
            f"{total_population}\n"

            f"Satisfied Population: "
            f"{total_satisfied_population}\n"

            f"Global Satisfaction: "
            f"{satisfaction_score:.2%}"
        )

        ax.text(
            0.02,               # x position
            0.02,               # y position
            metrics_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='bottom',
            bbox=dict(
                boxstyle='round',
                facecolor='white',
                alpha=0.9
            )
        )

    # MULTI-COLUMN DYNAMIC LEGEND (BOTTOM RIGHT)
    # Determine if we should show a legend and what data to populate it with
    visible_items = None
    if show_labels:
        if color_mode == 'default':
            visible_items = visible_countries
        elif color_mode == 'culture':
            visible_items = visible_cultures

    if visible_items:
        # Adjust MAX_ROWS to change column splitting thresholds
        MAX_ROWS = 20  
        sorted_item_names = sorted(visible_items.keys())
        columns_data = [sorted_item_names[i:i + MAX_ROWS] for i in range(0, len(sorted_item_names), MAX_ROWS)]

        h_list = [] # Holds our horizontal layout columns

        for col in columns_data:
            v_list = []
            for item_name in col:
                r, g, b = visible_items[item_name]
                
                # 1. OPTIMIZED: Shrunk canvas matrix to 8x8 and patch to 6.5x6.5
                color_square_canvas = DrawingArea(width=8, height=8)
                square_patch = mpatches.Rectangle((0, 0), 6.5, 6.5, facecolor=(r, g, b), edgecolor='none')
                color_square_canvas.add_artist(square_patch)
                
                # 2. OPTIMIZED: Crisp font size for high-res exports
                text_label = TextArea(f" {item_name}   ", textprops=dict(fontsize=6.5, color='black'))
                
                # 3. Vertical alignment micro-shifter wrapper
                text_shifter = VPacker(children=[text_label], align="center", pad=0, sep=0)
                
                # 4. Pair them horizontally using center alignment
                row_item = HPacker(children=[color_square_canvas, text_shifter], align="center", pad=0, sep=0)
                v_list.append(row_item)
                
            # OPTIMIZED: Dropped separation to 0; typography line-height supplies the rest
            column_box = VPacker(children=v_list, align="left", pad=0, sep=0)
            h_list.append(column_box)

        # Arrange generated columns side-by-side horizontally
        # Lowered separation between columns to 8 for a tighter horizontal profile
        main_legend_box = HPacker(children=h_list, align="top", pad=2, sep=8)

        # Anchor the master layout box to the lower-right axis panel
        anchored_box = AnchoredOffsetbox(
            loc='lower right', 
            child=main_legend_box, 
            pad=0.4,
            frameon=True, 
            bbox_to_anchor=(0.98, 0.02),
            bbox_transform=ax.transAxes
        )
        
        # Style background attributes uniformly to match global metrics panel
        # OPTIMIZED: pad=0.15 makes the bounding frame look tailored and sleek
        anchored_box.patch.set_boxstyle("round,pad=0.15")
        anchored_box.patch.set_facecolor("white")
        anchored_box.patch.set_alpha(0.9)
        anchored_box.set_zorder(5)

        ax.add_artist(anchored_box)

    plt.tight_layout()
    plt.show()
    return

# -----------------------------------
# PUBLIC FUNCTIONS
# -----------------------------------

def ShowGeographicGraph(G: nx.Graph) -> None:
    _DrawGraph(G)


def ShowPartitionedGraph(G: nx.Graph,
                         tags: str | list[str] | None = None,
                         include_metrics: bool = True,
                         show_labels: bool = True) -> None:
    if include_metrics:
        global_metrics = GlobalSatisfaction(G, tags = tags)
        _DrawGraph(G, color_mode='default', tags = tags, global_metrics = global_metrics, show_labels = show_labels)
        return
    _DrawGraph(G, color_mode='default', tags = tags, show_labels = show_labels)

def ShowSatisfactionMap(G: nx.Graph,
                        tags: str | list[str] | None = None,
                        include_metrics: bool = True) -> None:
    if include_metrics:
        global_metrics = GlobalSatisfaction(G, tags = tags)
        _DrawGraph(G, color_mode='satisfaction', tags = tags, global_metrics = global_metrics)
        return
    _DrawGraph(G, color_mode='satisfaction', tags = tags)

def ShowCulturalMap(G: nx.Graph,
                    tags: str | list[str] | None = None,
                    include_metrics: bool = True,
                    show_labels: bool = True) -> None:
    if include_metrics:
        global_metrics = GlobalSatisfaction(G,tags=tags)
        _DrawGraph(G, color_mode='culture',tags=tags, global_metrics=global_metrics, show_labels = show_labels)
        return
    _DrawGraph(G,color_mode='culture',tags=tags, show_labels = show_labels)