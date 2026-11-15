"""Build pub dataset (name, address, coords, colour) + London boundary."""
import json, re
import pandas as pd, geopandas as gpd
from shapely.geometry import LineString
from shapely.ops import linemerge, unary_union, polygonize

# ---------- boundary ----------
rel = json.load(open("london_boundary_raw.json", encoding="utf-8"))["elements"][0]
outer = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
         for m in rel["members"] if m["type"] == "way" and m["role"] == "outer"]
poly = unary_union(list(polygonize(linemerge(outer))))
gpd.GeoSeries([poly], crs=4326).to_file("london_boundary.geojson", driver="GeoJSON")

# ---------- pubs ----------
els = json.load(open("pubs_raw.json", encoding="utf-8"))["elements"]
rows = []
for e in els:
    t = e.get("tags", {})
    lat, lon = (e["lat"], e["lon"]) if e["type"] == "node" else (e["center"]["lat"], e["center"]["lon"])
    street = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
    addr = ", ".join(x for x in [t.get("addr:housename"), street, t.get("addr:suburb"),
                                 t.get("addr:city"), t.get("addr:postcode")] if x)
    rows.append(dict(osm_id=f'{e["type"]}/{e["id"]}', name=t.get("name"), address=addr or None,
                     housenumber=t.get("addr:housenumber"), street=t.get("addr:street"),
                     suburb=t.get("addr:suburb"), city=t.get("addr:city"),
                     postcode=t.get("addr:postcode"), operator=t.get("operator"),
                     lon=lon, lat=lat))
df = pd.DataFrame(rows)

# ---------- colour match (basic colour words only, whole words) ----------
COLOURS = {"red": "red", "white": "white", "black": "black", "green": "green", "blue": "blue",
           "yellow": "yellow", "gold": "gold", "golden": "gold", "silver": "silver",
           "orange": "orange", "pink": "pink", "purple": "purple", "grey": "grey",
           "gray": "grey", "brown": "brown"}
word_re = re.compile(r"\b(" + "|".join(COLOURS) + r")\b", re.I)
surname_re = re.compile(r"\bbrown['’]?s\b", re.I)   # Brown's = surname, not a colour
# "Green" as a place (Bethnal Green, on the Green, The Green, Village Green...) is not a colour
place_re = re.compile(r"\b(bethnal|kensal|walham|village|parsons|turnham|stamford|peckham|"
                      r"newington|on the) green\b|^(the )?green( w7)?$|\bgreen w7\b", re.I)


def match(name):
    """First basic colour word in the name; whole words only, surname uses skipped."""
    if not isinstance(name, str):
        return None
    n = surname_re.sub("", name)
    n = place_re.sub("", n)
    m = word_re.search(n)
    return COLOURS[m.group(1).lower()] if m else None


df["colour"] = df["name"].map(match)
df.to_csv("pubs_london_all.csv", index=False)
g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326)
g = g[g.within(poly)]          # keep only pubs inside the boundary polygon
g.to_file("pubs_london_all.geojson", driver="GeoJSON")
c = g[g.colour.notna()]
c.to_csv("pubs_london_colour.csv", index=False)
c.to_file("pubs_london_colour.geojson", driver="GeoJSON")
print(len(df), "pubs;", df.name.isna().sum(), "unnamed;", len(g), "inside boundary;", len(c), "colour pubs")
print(c.colour.value_counts())
