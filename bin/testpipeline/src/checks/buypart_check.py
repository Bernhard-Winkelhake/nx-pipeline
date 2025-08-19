# buypart_check.py (lazy NX work part)
import NXOpen
from utils.notify import popup

STANDARDTEXT_PRICE = {"0", "n/a", "-", "hier einzelteilpreis eintragen"}
STANDARDTEXT_ORDERLINK = {"n/a", "kein link", "-", "hier link hinterlegen"}

def _work_part():
    session = NXOpen.Session.GetSession()
    return getattr(session.Parts, "Work", None)

def _get_attr(name: str) -> str:
    wp = _work_part()
    if wp is None:
        return ""
    try:
        return wp.GetUserAttributeAsString(name, NXOpen.NXObject.AttributeType.String, -1).strip().lower()
    except Exception:
        return ""

def validate_buy_part() -> bool:
    is_buy_part = _get_attr("01_Part_isBuyPart")
    price = _get_attr("01_Part_price")
    order_link = _get_attr("01_Part_orderLink")

    if is_buy_part == "nein":
        return True

    if is_buy_part == "ja":
        price_ok = bool(price) and price not in STANDARDTEXT_PRICE
        link_ok = bool(order_link) and order_link not in STANDARDTEXT_ORDERLINK
        return price_ok and link_ok

    return False

def validate_buy_part_with_popup() -> bool:
    ok = validate_buy_part()
    is_buy_part = _get_attr("01_Part_isBuyPart")
    price = _get_attr("01_Part_price")
    order_link = _get_attr("01_Part_orderLink")

    if ok:
        if is_buy_part == "nein":
            popup("Kaufteil-Check", "ℹ️ Kein Kaufteil: Check übersprungen.", "note")
        else:
            popup("Kaufteil-Check", "✔️ Preis und Bestelllink sind gültig.", "info")
    else:
        if not is_buy_part:
            popup("Kaufteil-Check", "⚠️ Attribut '01_Part_isBuyPart' ist nicht gesetzt.", "warning")
        elif is_buy_part not in {"ja", "nein"}:
            popup("Kaufteil-Check", f"⚠️ Ungültiger Wert für '01_Part_isBuyPart': '{is_buy_part}'", "warning")
        else:
            msg = []
            if not price or price in STANDARDTEXT_PRICE:
                msg.append("Preis fehlt/Platzhalter")
            if not order_link or order_link in STANDARDTEXT_ORDERLINK:
                msg.append("Bestelllink fehlt/Platzhalter")
            popup("Kaufteil-Check", "⚠️ " + ", ".join(msg), "warning")
    return ok
