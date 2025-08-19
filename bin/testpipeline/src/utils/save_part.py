import NXOpen

def save_active_part():
    session = NXOpen.Session.GetSession()
    workPart = session.Parts.Work

    if workPart.IsModified:
        save_status = workPart.Save(NXOpen.BasePartSaveComponents.ValueOf(True),
                                    NXOpen.BasePartCloseAfterSave.ValueOf(False)           

        )
