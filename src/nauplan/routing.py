"""Sea distances between load and discharge ports.

Computed with searoute (Eurostat MARNET sea network). These are modelled routes, not a
published distance table; validate against voyage records before relying on them.

Variants per port pair:
  shortest    default network; may pass Torres Strait (max draft 12.5 m, see passages.csv)
  deep_draft  Torres Strait removed, for laden Panamax / Capesize from Queensland
  avoid_suez  deep_draft network, also avoiding Suez and Bab-el-Mandeb (Cape of Good Hope)
"""
from __future__ import annotations

import copy
from functools import lru_cache
from importlib.metadata import version

import pandas as pd
import searoute as sr

from nauplan.config import REFERENCE
from nauplan.reference import ports

# (lon_min, lon_max, lat_min, lat_max)
TORRES_STRAIT = (141.0, 143.6, -11.2, -9.0)
DANISH_STRAITS = (9.5, 13.0, 54.3, 57.9)

BASE_RESTRICTIONS = ["northwest"]  # searoute default: no Northwest Passage
VARIANTS = {
    "shortest": (False, BASE_RESTRICTIONS),
    "deep_draft": (True, BASE_RESTRICTIONS),
    "avoid_suez": (True, BASE_RESTRICTIONS + ["suez", "babalmandab"]),
}


def _inside(box: tuple[float, float, float, float], point) -> bool:
    lon, lat = point[0], point[1]
    return box[0] <= lon <= box[1] and box[2] <= lat <= box[3]


@lru_cache
def _network(without_torres: bool):
    net = copy.deepcopy(sr.setup_M())
    if without_torres:
        cut = [(u, v) for u, v in net.edges() if _inside(TORRES_STRAIT, u) or _inside(TORRES_STRAIT, v)]
        net.remove_edges_from(cut)
        net.remove_nodes_from([n for n in list(net.nodes) if net.degree(n) == 0])
        net.update_kdtree()
    return net


def route(origin: tuple[float, float], destination: tuple[float, float], variant: str = "deep_draft") -> dict:
    """origin / destination as (lon, lat). Returns distance in nautical miles and what the route crosses."""
    without_torres, restrictions = VARIANTS[variant]
    r = sr.searoute(list(origin), list(destination), units="naut", M=_network(without_torres),
                    restrictions=list(restrictions), return_passages=True)
    coords = r.geometry["coordinates"]
    return {
        "distance_nm": round(r.properties["length"]),
        "passages": ";".join(r.properties.get("traversed_passages") or []),
        "via_torres_strait": any(_inside(TORRES_STRAIT, c) for c in coords),
        "via_danish_straits": any(_inside(DANISH_STRAITS, c) for c in coords),
    }


def compute_distances() -> pd.DataFrame:
    p = ports().set_index("port_id")
    load = p[p["role"] == "load"]
    discharge = p[p["role"] == "discharge"]
    method = f"searoute {version('searoute')} (Eurostat MARNET)"
    rows = []
    for o, orow in load.iterrows():
        for d, drow in discharge.iterrows():
            for variant in VARIANTS:
                res = route((orow.lon, orow.lat), (drow.lon, drow.lat), variant)
                rows.append({"origin": o, "destination": d, "variant": variant, **res, "method": method})
    return pd.DataFrame(rows)


def distances() -> pd.DataFrame:
    return pd.read_csv(REFERENCE / "distances.csv", keep_default_na=False)


def write_distances() -> str:
    path = REFERENCE / "distances.csv"
    compute_distances().to_csv(path, index=False)
    return str(path)
