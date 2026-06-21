# Lovable Prompts — Usage Order

Paste into Lovable as 3 separate chat turns. Wait for the preview to render between each.

| File | What it builds | Paste order |
|------|---------------|-------------|
| 01_structure_and_design.md | Header · mode banner · stat cards · filter bar · layout shell | 1st |
| 02_reservations_table.md | Full reservation table with 8 hardcoded guest rows | 2nd |
| 03_agent_panel_and_api.md | Agent Ops panel · SSE feed · Scenarios · Escalations · live API wiring | 3rd |

**Before pasting Prompt 3:** make sure the FastAPI backend is running:
  cd villa_antica_barcelona && python main.py

**If Lovable can't reach localhost:** use ngrok:
  ngrok http 8000
Then replace "http://localhost:8000" with the ngrok URL in the prompt before pasting.

## Design provenance

This is an original visual identity — ink-teal header, terracotta/gold accents,
warm sand background — built for a fictional Mediterranean boutique hotel.
It follows general enterprise PMS dashboard *conventions* (dark top nav, stat
cards, reservation grid, collapsible side panel) that show up across nearly
every PMS vendor (Opera, Mews, Cloudbeds, Shiji, etc.) because that's how the
job gets done, not because it's copied from any one of them. No vendor colors,
exact spacing, or copy were reused. Safe to present as your own work.
