# solidbody_check.py (lazy NX work part)
import NXOpen
from typing import List

def _work_part():
    session = NXOpen.Session.GetSession()
    return getattr(session.Parts, "Work", None)

HOLE_LAYER_EXPECTED = 1

def move_object_to_layer(obj: NXOpen.DisplayableObject, layer: int):
    wp = _work_part()
    if wp is None: 
        raise RuntimeError("No active Work Part")
    wp.Layers.MoveDisplayableObjects(layer, [obj])

def assign_holes_to_layer():
    wp = _work_part()
    if wp is None:
        return
    all_features = wp.Features
    for feature in all_features:
        if getattr(feature, "FeatureType", "") == "HOLE":
            bodies = feature.GetBodies()
            for body in bodies:
                if isinstance(body, NXOpen.Body) and body.IsSolidBody:
                    move_object_to_layer(body, HOLE_LAYER_EXPECTED)

def _all_hole_bodies() -> List[NXOpen.Body]:
    wp = _work_part()
    if wp is None:
        return []
    bodies = []
    for feature in wp.Features:
        if getattr(feature, "FeatureType", "") == "HOLE":
            for b in feature.GetBodies():
                if isinstance(b, NXOpen.Body) and b.IsSolidBody:
                    bodies.append(b)
    return bodies

def check_holes_on_expected_layer() -> bool:
    holes = _all_hole_bodies()
    if not holes:
        return True
    try:
        return all(getattr(b, "Layer", None) == HOLE_LAYER_EXPECTED for b in holes)
    except Exception:
        return False
