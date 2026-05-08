import re

_BROWSERS = [
    (r"Edg/",        "Edge"),
    (r"OPR/|Opera",  "Opera"),
    (r"Chrome/",     "Chrome"),
    (r"Firefox/",    "Firefox"),
    (r"Safari/",     "Safari"),
]

_OS = [
    (r"Windows NT",    "Windows"),
    (r"Mac OS X",      "macOS"),
    (r"Android",       "Android"),
    (r"iPhone|iPad",   "iOS"),
    (r"Linux",         "Linux"),
]

def parse_user_agent(ua: str | None) -> dict[str, str]:
    if not ua:
        return {"browser": "Unknown", "os": "Unknown", "device": "desktop"}

    browser = next((name for pat, name in _BROWSERS if re.search(pat, ua)), "Other")
    os      = next((name for pat, name in _OS      if re.search(pat, ua)), "Other")

    if re.search(r"iPhone|Android.*Mobile|Mobile", ua):
        device = "mobile"
    elif re.search(r"iPad|Android(?!.*Mobile)|Tablet", ua):
        device = "tablet"
    else:
        device = "desktop"

    return {"browser": browser, "os": os, "device": device}