from __future__ import annotations

from app.live_sheet_snapshot import (
    _main_payloads,
    _product_name_candidate,
    _sheet_date,
    _usage_payloads,
    classify_main,
    classify_usage,
    cross_sheet_conflicts,
)


def main() -> None:
    if _sheet_date(46023) != "2026-01-01":
        raise AssertionError("Google date serial normalization failed")
    if _product_name_candidate("10cc Syringe (1/2026)") != ("10cc Syringe", "2026-01"):
        raise AssertionError("terminal expiry suffix normalization failed")
    if _product_name_candidate("Ambu Bag (Adult)") != ("Ambu Bag (Adult)", None):
        raise AssertionError("product-defining parentheses must not be stripped")

    main_values = [
        [
            "No.",
            "Items",
            "Expiry Date",
            "Unit",
            "Remaining Stock",
            "Received Stock",
            "Stock Status Today",
            "This Month Usage",
            "CMS Price",
            "Price",
            "Remark",
            "Serial Code",
            "CS Name",
        ],
        [1, "10cc Syringe (1/2026)", 46023, "Pcs", 200, "", 100, 100, 1.4, 1.4, "", "S10100667", "Syringe 10cc"],
        [2, "Unmapped Item", "", "Pcs", 10, 5, 15, 0, "", "", "", "Nil", ""],
        [3, "ECG / USG Transmission Gel", "", "Bot", 20, 0, 20, 0, 10.7, 10.7, "Recycled ID", "S10100193", "Diathermy Patient Plate"],
        [4, "No Expiry Consumable", "", "Pcs", 8, 2, 10, 0, 3.0, 3.0, "", "S10000001", "No Expiry CMS"],
        [5, "Expiry Mismatch (5/2024)", 46143, "Pcs", 5, 0, 5, 0, 1.0, 1.0, "", "S10000002", "Mismatch CMS"],
        [6, "Discontinued Local Item", "", "Pcs", 3, 0, 3, 0, 2.0, 2.0, "CMS Discontinued (Local Stock Retained)", "M20000001", "Old CMS Item"],
    ]

    usage_header = [
        "No.",
        "Items",
        "Remaining Stock",
        "Received Stock",
        *[str(day) for day in range(1, 32)],
        "This Month Usage",
        "This Month Remaining",
        "Remark",
        "Expiry Date",
    ]
    usage_row_1 = [1, "10cc Syringe (1/2026)", 200, "", 100, *([""] * 30), 100, 100, "", 46023]
    usage_row_2 = [2, "Unmapped Item", 10, 5, *([""] * 31), 0, 15, "", ""]
    usage_row_3 = [3, "ECG / USG Transmission Gel", 20, 0, *([""] * 31), 0, 20, "", ""]
    usage_row_4 = [4, "No Expiry Consumable", 8, 2, *([""] * 31), 0, 10, "", ""]
    usage_row_5 = [5, "Expiry Mismatch (5/2024)", 5, 0, *([""] * 31), 0, 5, "", 46143]
    usage_row_6 = [6, "Discontinued Local Item", 3, 0, *([""] * 31), 0, 3, "", ""]
    usage_values = [usage_header, usage_row_1, usage_row_2, usage_row_3, usage_row_4, usage_row_5, usage_row_6]

    main_rows = _main_payloads(main_values)
    usage_rows = _usage_payloads(usage_values)
    if len(main_rows) != 6 or len(usage_rows) != 6:
        raise AssertionError("live-shaped row parsing failed")

    syringe = main_rows[0]
    if syringe["product_name_candidate"] != "10cc Syringe" or syringe["expiry_date"] != "2026-01-01":
        raise AssertionError("Product/Lot normalization failed")
    if classify_main(syringe)[0] != "SAFE":
        raise AssertionError("valid Main Stock row should classify SAFE")

    if main_rows[1]["mapping_hint"] != "UNMAPPED" or classify_main(main_rows[1])[0] != "NEW_UNMAPPED":
        raise AssertionError("Nil/blank CMS code should classify NEW_UNMAPPED")

    if main_rows[2]["mapping_hint"] != "RECYCLED_CODE" or classify_main(main_rows[2])[0] != "REVIEW":
        raise AssertionError("Recycled ID must stay reviewable rather than auto-sync")

    if classify_main(main_rows[3])[0] != "SAFE":
        raise AssertionError("a valid non-expiry consumable must not be rejected solely for missing expiry")

    if not main_rows[4]["expiry_suffix_mismatch"] or classify_main(main_rows[4])[0] != "REVIEW":
        raise AssertionError("expiry suffix/structured date mismatch must stay REVIEW")

    if main_rows[5]["mapping_hint"] != "CMS_DISCONTINUED" or classify_main(main_rows[5])[0] != "SAFE":
        raise AssertionError("CMS-discontinued local stock must remain inventory-safe when stock arithmetic is valid")

    if classify_usage(usage_rows[0])[0] != "SAFE" or classify_usage(usage_rows[3])[0] != "SAFE":
        raise AssertionError("valid Daily Usage rows, including non-expiry items, should classify SAFE")

    conflicts = cross_sheet_conflicts(main_rows, usage_rows)
    expected_mismatch_key = ("expiry mismatch", "2026-05-01")
    if expected_mismatch_key in conflicts:
        raise AssertionError("expiry suffix review is not itself a cross-sheet quantity conflict")

    conflict_usage = [dict(row) for row in usage_rows]
    conflict_usage[0]["this_month_remaining"] = "99"
    conflict = cross_sheet_conflicts(main_rows, conflict_usage)
    if not conflict:
        raise AssertionError("cross-sheet remaining mismatch was not detected")

    print("F6D live-shaped snapshot adapter verification PASS")
    print(
        "date_serial=pass expiry_suffix=pass product_parentheses=pass "
        "no_expiry=pass recycled_mapping=pass discontinued_mapping=pass "
        "new_unmapped=pass cross_sheet_conflict=pass"
    )


if __name__ == "__main__":
    main()
