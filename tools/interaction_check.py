"""Herb-Drug Interaction Checker.

Displays known herb-drug interactions with severity badges for a single
herb or a multi-herb formula. Loads interaction data from the shared
data layer.

When the interaction database is not yet populated (empty list/dict),
the tool displays an informational message rather than failing.
"""

import gradio as gr

try:
    from core.data_loader import INTERACTIONS, MONOGRAPHS
except Exception:
    INTERACTIONS: list | dict = []
    MONOGRAPHS: list | dict = []


# ---------------------------------------------------------------------------
# Severity badge rendering
# ---------------------------------------------------------------------------

_SEVERITY_BADGES: dict[str, str] = {
    "high": "**[HIGH]**",
    "moderate": "**[MODERATE]**",
    "low": "[low]",
    "theoretical": "[theoretical]",
    "unknown": "[unknown]",
}

_EVIDENCE_LABELS: dict[str, str] = {
    "clinical": "Clinical evidence",
    "case_report": "Case report(s)",
    "in_vitro": "In vitro / animal",
    "traditional": "Traditional caution",
    "theoretical": "Theoretical / pharmacological reasoning",
}


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _get_herb_names() -> list[str]:
    """Extract a sorted list of herb names from available data."""
    names: set[str] = set()

    # INTERACTIONS may be a list of dicts or a dict keyed by herb name
    if isinstance(INTERACTIONS, dict):
        names.update(INTERACTIONS.keys())
    elif isinstance(INTERACTIONS, list):
        for entry in INTERACTIONS:
            if isinstance(entry, dict):
                name = entry.get("herb") or entry.get("name") or entry.get("herb_name")
                if name:
                    names.add(name)

    # Also pull names from MONOGRAPHS if available
    if isinstance(MONOGRAPHS, dict):
        names.update(MONOGRAPHS.keys())
    elif isinstance(MONOGRAPHS, list):
        for entry in MONOGRAPHS:
            if isinstance(entry, dict):
                name = entry.get("common_name") or entry.get("name")
                if name:
                    names.add(name)

    return sorted(names)


def _get_interactions_for_herb(herb_name: str) -> list[dict]:
    """Return a list of interaction dicts for a given herb name."""
    results: list[dict] = []

    if isinstance(INTERACTIONS, dict):
        herb_data = INTERACTIONS.get(herb_name, [])
        if isinstance(herb_data, list):
            results.extend(herb_data)
        elif isinstance(herb_data, dict):
            results.append(herb_data)
    elif isinstance(INTERACTIONS, list):
        for entry in INTERACTIONS:
            if not isinstance(entry, dict):
                continue
            entry_name = (
                entry.get("herb")
                or entry.get("name")
                or entry.get("herb_name")
                or ""
            )
            if entry_name.lower() == herb_name.lower():
                interactions = entry.get("interactions", [])
                if isinstance(interactions, list):
                    results.extend(interactions)
                else:
                    results.append(entry)

    return results


def _format_interaction(interaction: dict) -> str:
    """Format a single interaction dict as Markdown."""
    drug = interaction.get("drug") or interaction.get("interacts_with") or "Unknown"
    severity = (interaction.get("severity") or "unknown").lower()
    badge = _SEVERITY_BADGES.get(severity, f"[{severity}]")
    evidence = (interaction.get("evidence") or interaction.get("evidence_level") or "").lower()
    evidence_label = _EVIDENCE_LABELS.get(evidence, evidence.capitalize() if evidence else "")
    mechanism = interaction.get("mechanism") or ""
    description = interaction.get("description") or interaction.get("effect") or ""
    recommendation = interaction.get("recommendation") or ""

    parts: list[str] = [f"- {badge} **{drug}**"]

    if description:
        parts.append(f"  {description}")
    if mechanism:
        parts.append(f"  *Mechanism:* {mechanism}")
    if evidence_label:
        parts.append(f"  *Evidence:* {evidence_label}")
    if recommendation:
        parts.append(f"  *Recommendation:* {recommendation}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Lookup functions
# ---------------------------------------------------------------------------

def _data_is_empty() -> bool:
    """Check whether interaction data is populated."""
    if not INTERACTIONS:
        return True
    if isinstance(INTERACTIONS, (list, dict)) and len(INTERACTIONS) == 0:
        return True
    return False


_EMPTY_MESSAGE = (
    "**Interaction data not yet loaded.** This tool will display herb-drug "
    "interaction information once the interaction database is populated.\n\n"
    "The `data/herbs/interactions.json` file is currently empty or missing. "
    "See `DATA_GENERATION_PROMPT.md` for instructions on generating the "
    "interaction dataset."
)


def _single_herb_lookup(herb_name: str) -> str:
    """Look up interactions for a single herb and return formatted Markdown."""
    if _data_is_empty():
        return _EMPTY_MESSAGE

    if not herb_name:
        return "Please select a herb to check."

    interactions = _get_interactions_for_herb(herb_name)

    if not interactions:
        return (
            f"**{herb_name}:** No interactions found in the database.\n\n"
            f"This may mean the herb has no commonly documented interactions, "
            f"or it has not yet been added to the dataset. Always consult "
            f"current pharmacopeial and clinical references for comprehensive "
            f"interaction data."
        )

    lines: list[str] = [f"### Interactions for {herb_name}\n"]
    for ix in interactions:
        lines.append(_format_interaction(ix))

    lines.append(
        "\n---\n*This information is for educational purposes. Always "
        "consult a qualified healthcare provider for clinical decisions.*"
    )

    return "\n\n".join(lines)


def _multi_herb_lookup(herb_names: list[str] | None) -> str:
    """Look up interactions for multiple herbs and flag combined risks."""
    if _data_is_empty():
        return _EMPTY_MESSAGE

    if not herb_names:
        return "Please select one or more herbs to check."

    all_sections: list[str] = [
        "## Formula Interaction Report\n"
        f"Checking {len(herb_names)} herb(s): {', '.join(herb_names)}\n"
    ]

    # Collect all interactions across herbs for cross-checking
    all_drugs_affected: dict[str, list[str]] = {}  # drug -> list of herbs

    for herb_name in herb_names:
        interactions = _get_interactions_for_herb(herb_name)
        if interactions:
            section_lines = [f"### {herb_name}\n"]
            for ix in interactions:
                section_lines.append(_format_interaction(ix))
                drug = (
                    ix.get("drug")
                    or ix.get("interacts_with")
                    or "Unknown"
                )
                all_drugs_affected.setdefault(drug, []).append(herb_name)
            all_sections.append("\n\n".join(section_lines))
        else:
            all_sections.append(f"### {herb_name}\n\nNo interactions found.\n")

    # Flag drugs affected by multiple herbs in the formula
    combined_risks = {
        drug: herbs
        for drug, herbs in all_drugs_affected.items()
        if len(herbs) > 1
    }
    if combined_risks:
        all_sections.append("---\n### Combined Risk Flags\n")
        all_sections.append(
            "The following drugs are affected by **multiple herbs** in "
            "this formula. Combined effects may be additive or synergistic:\n"
        )
        for drug, herbs in sorted(combined_risks.items()):
            all_sections.append(
                f"- **{drug}** -- affected by: {', '.join(herbs)}"
            )

    all_sections.append(
        "\n---\n*This information is for educational purposes. Always "
        "consult a qualified healthcare provider for clinical decisions.*"
    )

    return "\n\n".join(all_sections)


# ---------------------------------------------------------------------------
# Gradio Tab
# ---------------------------------------------------------------------------

def build_tab() -> gr.Tab:
    """Build and return the Herb-Drug Interaction Checker tab."""
    herb_names = _get_herb_names()

    with gr.Tab("Interaction Checker") as tab:
        gr.Markdown(
            "## Herb-Drug Interaction Checker\n"
            "Look up known interactions for a single herb, or check a "
            "multi-herb formula for combined interaction risks."
        )

        if _data_is_empty():
            gr.Markdown(
                "> **Note:** " + _EMPTY_MESSAGE
            )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Single Herb Lookup")
                herb_select = gr.Dropdown(
                    label="Select herb",
                    choices=herb_names if herb_names else [],
                    allow_custom_value=True,
                    interactive=True,
                )
                single_btn = gr.Button(
                    "Check Interactions", variant="primary"
                )
                single_output = gr.Markdown(value="")

            with gr.Column():
                gr.Markdown("### Multi-Herb Formula Check")
                multi_herb_select = gr.Dropdown(
                    label="Select herbs (multiple)",
                    choices=herb_names if herb_names else [],
                    multiselect=True,
                    allow_custom_value=True,
                    interactive=True,
                )
                multi_btn = gr.Button(
                    "Check Formula Interactions", variant="primary"
                )
                multi_output = gr.Markdown(value="")

        single_btn.click(
            fn=_single_herb_lookup,
            inputs=[herb_select],
            outputs=[single_output],
        )

        multi_btn.click(
            fn=_multi_herb_lookup,
            inputs=[multi_herb_select],
            outputs=[multi_output],
        )

        # Pedagogical accordion
        with gr.Accordion(
            "Understanding interaction severity levels", open=False
        ):
            gr.Markdown("""
Herb-drug interactions are categorized by **severity** and **evidence
level**. Understanding these categories helps you make informed decisions
rather than either ignoring all interactions or avoiding all herbs.

---

#### Severity levels

| Level | Badge | Meaning |
|-------|-------|---------|
| **High** | **[HIGH]** | Clinically significant. May cause serious adverse effects, treatment failure, or require dose adjustment. Combination should generally be avoided or closely monitored by a healthcare provider. |
| **Moderate** | **[MODERATE]** | May alter drug effectiveness or cause noticeable side effects. Clinical monitoring is advisable. The combination may be acceptable with awareness and professional guidance. |
| **Low** | [low] | Minor or unlikely interaction. Generally safe with awareness. May involve subtle changes in absorption or metabolism. |
| **Theoretical** | [theoretical] | Based on pharmacological reasoning (shared metabolic pathway, known constituent activity) but not confirmed in clinical or even case-report data. Worth noting but not a basis for alarm. |

---

#### Evidence levels

| Level | Meaning |
|-------|---------|
| **Clinical evidence** | Demonstrated in human clinical trials or well-documented systematic reviews. |
| **Case report(s)** | Reported in published case reports. Suggests a real interaction but cannot establish frequency or causality. |
| **In vitro / animal** | Observed in laboratory or animal studies. May not translate to human clinical significance. |
| **Traditional caution** | Noted in traditional pharmacopeias or long-standing practice guidelines without formal study. |
| **Theoretical** | Inferred from known pharmacology of the herb's constituents (e.g., "contains coumarins, so may potentiate warfarin"). |

---

#### Important context

- **Most herb-drug interactions are dose-dependent.** A cup of chamomile
  tea is not the same as a concentrated chamomile extract taken daily.
- **Timing matters.** Taking herbs and medications at different times of
  day can sometimes reduce absorption-related interactions.
- **Individual variation** in genetics, gut microbiome, liver enzyme
  activity, and overall health status affects interaction risk.
- **This tool is educational, not clinical.** It flags known and
  theoretical interactions to support learning and awareness. It does
  not replace professional medical advice.

#### Combined risk in formulas

When multiple herbs in a formula affect the same drug or pathway, the
effects may be **additive** (sum of individual effects) or
**synergistic** (greater than the sum). The multi-herb checker flags
these overlaps so you can evaluate combined risk.
            """)

    return tab
