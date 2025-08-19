# utils/notify.py

import NXOpen

def popup(title: str, message: str, level: str = "info"):
    ui = NXOpen.UI.GetUI()
    message_box = ui.NXMessageBox

    # Sichere Zuordnung der Levels zu den korrekten DialogType-Enums
    dialog_type_map = {
        "info": NXOpen.NXMessageBox.DialogType.Information,
        # "note": NXOpen.NXMessageBox.DialogType.Note,
        "warning": NXOpen.NXMessageBox.DialogType.Warning,
        "error": NXOpen.NXMessageBox.DialogType.Error
    }

    # Fallback auf "info" falls ungültig
    dialog_type = dialog_type_map.get(level.lower(), NXOpen.NXMessageBox.DialogType.Information)

    # Popup anzeigen
    message_box.Show(title, dialog_type, message)
