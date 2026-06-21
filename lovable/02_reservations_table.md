# Lovable Prompt 2 of 3 — Reservations Table
# Paste this AFTER Prompt 1 is done. It adds the main content area.

Now add the reservations table below the filter bar.

## Table header (bg `--bg-table-header`, 38px, border-bottom `--border-table`)
Columns in order — all 11px semibold uppercase `--text-muted`:

checkbox 40px | GUEST NAME 180px | VIP MEMBERSHIP 100px | EXT. REF. NO. 120px | RES. STATUS 100px | PREFERENCES 90px | ROOM NO. ROOM TYPE 100px | ROOM STATUS HK STATUS 100px | GUESTS CONF. NO. 80px | ↑ ARRIVAL DEPARTURE (NIGHTS) 150px | RATE PLAN GTD. TYPE 100px | RATE AMOUNT BALANCE 110px | PAY. METHOD GROUP CODE 110px | NOTES 50px | TASKS 50px | LINKS 160px | INDICATES 80px | (actions) 80px

## Hardcoded rows (8 guests)
Each row: white bg, border-bottom `--border-table`, 13px `--text-primary`. Hover: bg `--selected-card-bg`.
Guest name cell: 2-letter avatar circle (rotate through terracotta/teal/gold) + "Lastname, Firstname, Title".
Res. Status: teal pill badge "DI  Due In" (bg `--status-teal-bg`, text `--status-teal-text`, full pill shape, no border).
Room No. cell: "Assign" link in `--accent-primary` underline + room type code in 11px grey below.
Actions column: → button (outlined, 28px, check-in icon) + ⋮ + ∨

Row 1: Đình, Thế, Mrs | — | PMS Import | DI | — | Assign / TWDX | — | 2/0 · RES0045 | 15/06/2026 00:07 · 18/06 07:18 (3) | BARRES · PRE | 529.00 EUR · 0.00 | PRE | 📄 | clipboard | Grupo ACS · Madrid Viajes | 2 stays
Row 2: Milani, Jolanda, Mrs | — | — | DI | 2 Prefs | Assign / TWSP | — | 1/0 · RES0082 | 15/06/2026 00:20 · 17/06 11:00 (2) | CORL25 · PRE | 351.00 EUR · 0.00 | PRE | 📄 | clipboard | Grupo Catalana Occidente | 5 stays
Row 3: Đặng, Diện, Mr | — | — | DI | — | Assign / KGDX | — | 2/0 · RES0031 | 15/06/2026 01:01 · 20/06 12:00 (5) | BAR10 · HOLD | 561.00 EUR · 0.00 | HOLD | 📄 | clipboard | Tui Spain | 2 stays
Row 4: Bourque, Hamilton, Mr | — | — | DI | 2 Prefs | Assign / TWDX | — | 2/0 · RES0119 | 15/06/2026 01:25 · 18/06 10:00 (3) | BARRES · PRE | 512.00 EUR · 0.00 | PRE | 📄 | clipboard (red badge "2") | Telefonica | 3 stays
Row 5: Martins, Ryan, Mr | — | — | DI | 1 Pref | Assign / KGDX | — | 2/0 · RES0056 | 15/06/2026 01:35 · 16/06 12:00 (1) | BAR · OFF | XXXXX EUR · 0.00 | OFF | 📄 | clipboard | Saudi Aramco | 3 stays
Row 6: Gairbekova, Laura, Ms | VIP | — | DI | — | Assign / KGST | — | 1/0 · RES0007 | 15/06/2026 02:48 · 21/06 11:00 (6) | BARRES · PRE | 748.00 EUR · 0.00 | PRE | 📄 | clipboard | Saudi Aramco | 14 stays
Row 7: Araujo, Isabela, Mrs | — | — | DI | 1 Pref | Assign / TWDX | — | 2/0 · RES0093 | 15/06/2026 02:59 · 19/06 10:00 (4) | BARRES · PRE | 529.00 EUR · 0.00 | PRE | 📄 | clipboard | Siemens Gamesa · American Express Fine H... | 12 stays
Row 8: Bennet, Kate, Ms | — | — | DI | — | Assign / TWDX | — | 1/0 · RES0144 | 15/06/2026 03:00 · 17/06 10:00 (2) | BAR10 · PRE | 399.00 EUR · 0.00 | PRE | 📄 | clipboard | — | 5 stays

## Interaction behaviours
- Clicking → (check-in) shows a toast: "In agent mode, check-in is handled automatically when conditions are met."
- Clicking "Assign" shows a toast: "Housekeeping agent will assign optimally based on guest profile and room status."
- Clicking "+ Add Task" (filter bar) shows a modal: "Feature demo — in agent mode, tasks are auto-assigned."
- No routing, no real form submission.
