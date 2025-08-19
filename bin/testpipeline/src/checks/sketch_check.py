# sketch_check.py (lazy NX work part)
import NXOpen
import NXOpen.Layer
from typing import List
from utils.config_loader import load_config

def _work_part():
    session = NXOpen.Session.GetSession()
    return getattr(session.Parts, "Work", None)

config = load_config()
SKETCH_LAYER_EXPECTED = config.get("layers", {}).get("sketch", 21)

def move_object_to_layer(obj: NXOpen.DisplayableObject, layer: int):
    wp = _work_part()
    if wp is None: 
        raise RuntimeError("No active Work Part")
    wp.Layers.MoveDisplayableObjects(layer, [obj])

def get_all_sketches() -> List[NXOpen.Sketch]:
    wp = _work_part()
    if wp is None:
        return []
    return list(wp.Sketches)

def assign_sketches_to_layer():
    for sketch in get_all_sketches():
        move_object_to_layer(sketch, SKETCH_LAYER_EXPECTED)

def check_sketches_on_expected_layer() -> bool:
    sketches = get_all_sketches()
    if not sketches:
        return True
    try:
        return all(getattr(s, "Layer", None) == SKETCH_LAYER_EXPECTED for s in sketches)
    except Exception:
        return False
