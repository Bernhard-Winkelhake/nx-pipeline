# plane_check.py (lazy NX work part)
import NXOpen
import NXOpen.Layer
from typing import List
from utils.config_loader import load_config

def _work_part():
    session = NXOpen.Session.GetSession()
    return getattr(session.Parts, "Work", None)

config = load_config()
DATUM_PLANES_LAYER_EXPECTED = config.get("layers", {}).get("plane", 62)

def move_object_to_layer(obj: NXOpen.DisplayableObject, layer: int):
    wp = _work_part()
    if wp is None: 
        raise RuntimeError("No active Work Part")
    wp.Layers.MoveDisplayableObjects(layer, [obj])

def get_all_datum_planes() -> List[NXOpen.DatumPlane]:
    wp = _work_part()
    if wp is None:
        return []
    return [d for d in wp.Datums if isinstance(d, NXOpen.DatumPlane)]

def assign_datum_planes_to_layer():
    for datum in get_all_datum_planes():
        move_object_to_layer(datum, DATUM_PLANES_LAYER_EXPECTED)

def check_datum_planes_on_expected_layer() -> bool:
    planes = get_all_datum_planes()
    if not planes:
        return True
    try:
        return all(getattr(p, "Layer", None) == DATUM_PLANES_LAYER_EXPECTED for p in planes)
    except Exception:
        return False
