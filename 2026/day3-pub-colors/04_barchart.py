"""Bar chart: top 10 most common pub names with a colour in them (Greater London)."""
import re
import pandas as pd
import matplotlib.pyplot as plt
from pyfonts import load_google_font

BG = "#1b1b1f"
# Same palette as the map (03_map.py)
COL = {"red": "#d6505a", "white": "#f2eee4", "black": "#4c5062", "green": "#4fa47c",
       "blue": "#4e82c4", "gold": "#f2cb55", "orange": "#e98b45", "grey": "#929cab",
       "brown": "#a0714f", "silver": "#c9d0d9", "purple": "#8f72b8"}

F_REG = load_google_font("Poppins", weight=400)
F_MED = load_google_font("Poppins", weight=500)
F_BOLD = load_google_font("Poppins", weight=700)

pubs = pd.read_csv("pubs_london_colour.csv")
all_pubs = len(pd.read_csv("pubs_london_all.csv"))


def clean(name):
    """Group variants: drop a leading 'The' / 'Ye' / 'Ye Olde' and tidy case."""
    n = re.sub(r"^(the|ye olde|ye)\s+", "", name.strip(), flags=re.I)
    return n.title()


pubs["pub_name"] = pubs["name"].map(clean)
top = (pubs.groupby("pub_name").agg(n=("osm_id", "count"), colour=("colour", "first"))
       .sort_values(["n", "pub_name"], ascending=[False, True]).head(10))
top.to_csv("top10_pub_names.csv")
print(top)
top = top.iloc[::-1]        # largest bar on top

fig, ax = plt.subplots(figsize=(12, 9), dpi=200, facecolor=BG)
ax.set_facecolor(BG)
bars = ax.barh(top.index, top.n, color=top.colour.map(COL), height=0.72)
for b, n in zip(bars, top.n):
    ax.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2, str(n), va="center",
            ha="left", color="#f0f0f5", fontproperties=F_MED, fontsize=15)
ax.set_yticks(range(len(top)))
ax.set_yticklabels(top.index, fontproperties=F_REG, fontsize=15, color="#f0f0f5")
ax.tick_params(axis="y", length=0, pad=8)
ax.set_xticks([])
ax.set_xlim(0, top.n.max() * 1.1)
for s in ax.spines.values():
    s.set_visible(False)

fig.text(0.04, 0.945, "Most common pub names with a colour", color="#ffffff", fontsize=30,
         fontproperties=F_BOLD, ha="left", va="top")
fig.text(0.04, 0.875, "Number of pubs in Greater London, bars shaded by the colour in the name",
         color="#c4c4ce", fontsize=15, fontproperties=F_REG, ha="left", va="top")
fig.text(0.04, 0.03, f"Data: Based on {len(pubs)} of {all_pubs:,} pubs on OpenStreetMap. "
         "Leading 'The' / 'Ye Olde' ignored.", color="#9a9aa5", fontsize=11,
         fontproperties=F_REG, ha="left", va="bottom")
fig.subplots_adjust(left=0.27, right=0.95, top=0.80, bottom=0.09)
fig.savefig("pub-colors-top10.png", facecolor=BG)
print("saved")
