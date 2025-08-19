import NXOpen
import NXOpen.Layer

theSession = NXOpen.Session.GetSession()
ui = NXOpen.UI.GetUI()
workPart = theSession.Parts.Work

def move_object_to_layer(object: NXOpen.DisplayableObject, layer:int):
    objectArray1 = [NXOpen.DisplayableObject.Null] * 1
    objectArray1[0] = object
    workPart.Layers.MoveDisplayableObjects(layer, objectArray1)







def main():
    

    # Erwartete Layer
    SKETCH_LAYER_EXPECTED = 21
    PLANE_LAYER_EXPECTED = 62

    fully_constrained_sketches = []
    under_constrained_sketches = []
    wrong_layer_sketches = []
    wrong_layer_planes = []


    # Skizzen prüfen
    for sketch in workPart.Sketches:
        name = sketch.Name
        status, dof_needed = sketch.GetStatus()

        if status.value == 3:
            fully_constrained_sketches.append(name)
        else:
            under_constrained_sketches.append(f"{name} (Status: {status}, DOF Needed: {dof_needed})")

        if sketch.Layer != SKETCH_LAYER_EXPECTED:
            wrong_layer_sketches.append(f"{name} (Layer: {sketch.Layer})")

    # Ebenen prüfen und ggf. Layer korrigieren (nur DatumPlanes)
    for feature in workPart.Features:
        if isinstance(feature, NXOpen.Features.DatumPlane):
            datum_plane = feature
            name = datum_plane.Name

            # Die eigentliche geometrische Plane extrahieren
            plane = datum_plane.GetEntities()[0]

            current_layer = workPart.LayerManager.GetLayerOfObject(plane)
            if current_layer != PLANE_LAYER_EXPECTED:
                wrong_layer_planes.append(f"{name} (Layer: {current_layer})")
                workPart.LayerManager.SetObjectLayer(plane, PLANE_LAYER_EXPECTED)


            



    # Attribut "Ansprechpartner" prüfen
    attribute_value = None
    try:
        attributes = workPart.GetUserAttributes()
        for attr in attributes:
            if attr.Title.strip().lower() == "ansprechpartner":
                attribute_value = attr.StringValue.strip()
                break
    except Exception:
        attribute_value = None



    # Ergebnisnachricht zusammenstellen
    message = ""

    # Ansprechpartner-Attribut prüfen
    if attribute_value and attribute_value.lower() != "hier deinen namen eintragen":
        message += f"✅ Attribut 'Ansprechpartner' ist gesetzt: {attribute_value}\n\n"
    else:
        message += f"⛔️ Attribut 'Ansprechpartner' ist NICHT korrekt gesetzt!\n\n"

    # Skizzenstatus prüfen
    if under_constrained_sketches:
        message += "⛔️ Nicht vollständig bestimmte Skizzen:\n"
        message += "\n".join(f" - {name}" for name in sorted(under_constrained_sketches)) + "\n\n"
    else:
        message += "✅ Alle Skizzen sind vollständig bestimmt.\n\n"

    # Layer der Skizzen prüfen
    if wrong_layer_sketches:
        message += f"⚠️ Skizzen nicht auf Layer {SKETCH_LAYER_EXPECTED}:\n"
        message += "\n".join(f" - {name}" for name in sorted(wrong_layer_sketches)) + "\n\n"
    else:
        message += f"✅ Alle Skizzen sind auf Layer {SKETCH_LAYER_EXPECTED}.\n\n"

    # Layer der Ebenen prüfen
    if wrong_layer_planes:
        message += f"⚠️ Ebenen nicht auf Layer {PLANE_LAYER_EXPECTED}:\n"
        message += "\n".join(f" - {name}" for name in sorted(wrong_layer_planes)) + "\n\n"
    else:
        message += f"✅ Alle Ebenen sind auf Layer {PLANE_LAYER_EXPECTED}.\n\n"

    # Ergebnis anzeigen
    ui.NXMessageBox.Show("Skizzen-, Ebenen- und Attributprüfung", NXOpen.NXMessageBox.DialogType.Information, message)

if __name__ == '__main__':
    main()
