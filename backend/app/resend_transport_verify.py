from __future__ import annotations

import ast
from pathlib import Path


def main() -> None:
    source = Path(__file__).with_name("email_recovery.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    text = source
    assert '"Accept": "application/json"' in text
    assert '"User-Agent": "MedicineStoreAssistant/1.0 (+https://inventory.drthorne.uk)"' in text
    print("resend_transport_headers=pass")


if __name__ == "__main__":
    main()
