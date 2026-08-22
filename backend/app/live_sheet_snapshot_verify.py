from __future__ import annotations

from app.live_sheet_snapshot import _main_payloads, _usage_payloads, classify_main, classify_usage, cross_sheet_conflicts


def main() -> None:
    main_values = [
        ["No.", "Items", "Expiry Date ", "Unit", "Remaining Stock", "Received Stock", "Stock Status Today", "This Month Usage", "Serial Code", "CS Name"],
        [1, "10cc Syringe (1/2026)", "Jan-2026", "Pcs", 200, "", 100, 100, "S10100667", "Syringe 10cc"],
        [2, "Unmapped Item", "Dec-2028", "Pcs", 10, 5, 15, 0, "", ""],
    ]
    usage_header = ["No.", "Items", "Remaining  Stock", "Received Stock", *[str(day) for day in range(1, 32)], "This Month Usage", "This Month Remaining", "Remark", "Expiry Date"]
    usage_row_1 = [1, "10cc Syringe (1/2026)", 200, "", 100, *([""] * 30), 100, 100, "", "Jan-2026"]
    usage_row_2 = [2, "Unmapped Item", 10, 5, *([""] * 31), 0, 15, "", "Dec-2028"]
    usage_values = [usage_header, usage_row_1, usage_row_2]

    main_rows = _main_payloads(main_values)
    usage_rows = _usage_payloads(usage_values)
    if len(main_rows) != 2 or len(usage_rows) != 2:
        raise AssertionError("live-shaped row parsing failed")
    if classify_main(main_rows[0])[0] != "SAFE":
        raise AssertionError("valid Main Stock row should classify SAFE")
    if classify_main(main_rows[1])[0] != "NEW_UNMAPPED":
        raise AssertionError("missing CMS code should classify NEW_UNMAPPED")
    if classify_usage(usage_rows[0])[0] != "SAFE" or classify_usage(usage_rows[1])[0] != "SAFE":
        raise AssertionError("valid Daily Usage rows should classify SAFE")
    if cross_sheet_conflicts(main_rows, usage_rows):
        raise AssertionError("aligned Main Stock and Daily Usage rows should not conflict")

    conflict_usage = [dict(usage_rows[0]), usage_rows[1]]
    conflict_usage[0]["this_month_remaining"] = "99"
    conflict = cross_sheet_conflicts(main_rows, conflict_usage)
    if not conflict:
        raise AssertionError("cross-sheet remaining mismatch was not detected")

    print("F6B live-shaped snapshot adapter verification PASS")
    print("header_mapping=pass balance_checks=pass new_unmapped=pass cross_sheet_conflict=pass")


if __name__ == "__main__":
    main()
