"""Reference data: ports and vessel classes. Every constraint value must carry a source."""
import pandas as pd

from nauplan.config import REFERENCE


def ports() -> pd.DataFrame:
    return pd.read_csv(REFERENCE / "ports.csv")


def discharge_ports() -> pd.DataFrame:
    p = ports()
    return p[p["role"] == "discharge"].reset_index(drop=True)
