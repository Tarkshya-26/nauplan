"""Reference data: ports, berth limits and vessel classes. Every limit value must carry a source."""
import pandas as pd

from nauplan.config import REFERENCE

LIMIT_COLUMNS = ["max_loa_m", "max_beam_m", "max_draft_m", "max_dwt_t", "max_displacement_t", "discharge_rate_tpd"]


def ports() -> pd.DataFrame:
    return pd.read_csv(REFERENCE / "ports.csv")


def discharge_ports() -> pd.DataFrame:
    p = ports()
    return p[p["role"] == "discharge"].reset_index(drop=True)


def berths() -> pd.DataFrame:
    """Berth-level limits. A blank value means not yet sourced, not unlimited."""
    return pd.read_csv(REFERENCE / "berths.csv")


def vessel_classes() -> pd.DataFrame:
    return pd.read_csv(REFERENCE / "vessel_classes.csv")
