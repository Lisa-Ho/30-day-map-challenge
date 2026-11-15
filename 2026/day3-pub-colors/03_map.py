"""Voronoi map: nearest pub with a colour in its name, across Greater London (EPSG:27700)."""
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pyfonts import load_google_font
from shapely.geometry import MultiPoint
from shapely.ops import voronoi_diagram

CRS = 27700
BG = "#1b1b1f"
# Vibrant palette; the same colour is used for a cell and the pub that owns it.
# "black" is a dark slate so it stays visible on the dark background.
COL = {"red": "#d6505a", "white": "#f2eee4", "black": "#4c5062", "green": "#4fa47c",
       "blue": "#4e82c4", "gold": "#f2cb55", "orange": "#e98b45", "grey": "#929cab",
       "brown": "#a0714f", "silver": "#c9d0d9", "purple": "#8f72b8", "yellow": "#f6e27a",
       "pink": "#e58aa8"}

# Custom fonts via pyfonts (Google Fonts)
F_REG = load_google_font("Poppins", weight=400)
F_MED = load_google_font("Poppins", weight=500)
F_BOLD = load_google_font("Poppins", weight=700)

london = gpd.read_file("london_boundary.geojson").to_crs(CRS)
pubs = gpd.read_file("pubs_london_colour.geojson").to_crs(CRS).reset_index(drop=True)
all_pubs = len(gpd.read_file("pubs_london_all.geojson"))
boundary = london.geometry.unary_union

# Voronoi cells (planar, metres), clipped to London
cells = voronoi_diagram(MultiPoint(list(pubs.geometry)), envelope=boundary.buffer(5000))
cells = gpd.GeoDataFrame(geometry=list(cells.geoms), crs=CRS)
cells = gpd.sjoin(cells, pubs, predicate="contains").drop(columns="index_right")
cells["geometry"] = cells.geometry.intersection(boundary)
cells.to_file("voronoi_cells.geojson", driver="GeoJSON")

# ---------- plot (4:3) ----------
fig, ax = plt.subplots(figsize=(12, 9), dpi=200, facecolor=BG)
ax.set_facecolor(BG)
cells.plot(ax=ax, color=cells.colour.map(COL), edgecolor=BG, linewidth=0.6)
gpd.GeoSeries([boundary], crs=CRS).boundary.plot(ax=ax, color="#9a9aa5", linewidth=0.8)
# owning pubs: small solid black dots, no outline
ax.scatter(pubs.geometry.x, pubs.geometry.y, s=6, c="#000000", linewidths=0, zorder=4)
ax.set_axis_off()
ax.set_aspect("equal")
minx, miny, maxx, maxy = boundary.bounds
cx = (minx + maxx) / 2
h = (maxy - miny) * 1.30        # 4:3 canvas; map sits low so the title has clear space above
w = h * 4 / 3
ax.set_xlim(cx - w / 2, cx + w / 2)
ax.set_ylim(miny - 0.06 * h, miny - 0.06 * h + h)

order = pubs.colour.value_counts().index
handles = [Line2D([], [], marker="o", ls="", markersize=11, markerfacecolor=COL[c],
                  markeredgecolor="white", markeredgewidth=0.4,
                  label=f"{c.title()} ({(pubs.colour == c).sum()})") for c in order]
leg = ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1.0, 0.05), frameon=False,
                labelcolor="#f0f0f5", prop=F_REG.copy(), title="Colour (# of pubs)",
                title_fontproperties=F_MED, ncol=2, labelspacing=0.8, columnspacing=1.0,
                handletextpad=0.5)
for t in leg.get_texts():
    t.set_fontproperties(F_REG)
    t.set_fontsize(13)
leg.get_title().set_fontsize(14)
leg.get_title().set_color("#ffffff")
leg._legend_box.align = "left"

fig.text(0.04, 0.945, "London pub colours", color="#ffffff", fontsize=32,
         fontproperties=F_BOLD, ha="left", va="top")
fig.text(0.04, 0.875, "Each area is shaded by the colour in the name of its closest pub",
         color="#c4c4ce", fontsize=15, fontproperties=F_REG, ha="left", va="top")
fig.text(0.04, 0.03, f"Data: Based on {len(pubs)} of {all_pubs:,} pubs on OpenStreetMap",
         color="#9a9aa5", fontsize=11, fontproperties=F_REG, ha="left", va="bottom")
fig.subplots_adjust(0, 0, 1, 1)
fig.savefig("pub-colors.png", facecolor=BG)
print("saved")
