"""Herb Monograph Quick Reference for HerbCalc.

Displays structured monograph cards for herbs in the database,
organized into collapsible sections for nomenclature, plant parts,
extraction parameters, constituents, dosage, safety, and energetics.

Data sourced from core.data_loader.MONOGRAPHS.
"""

import gradio as gr

from core.data_loader import MONOGRAPHS


def _monographs_available() -> bool:
    """Check whether monograph data is populated."""
    return isinstance(MONOGRAPHS, list) and len(MONOGRAPHS) > 0


def _get_herb_names() -> list[str]:
    """Extract herb names for the dropdown selector."""
    if not _monographs_available():
        return []
    names = []
    for m in MONOGRAPHS:
        common = m.get("common_name", "")
        latin = m.get("latin_name", "")
        if common and latin:
            names.append(f"{common} ({latin})")
        elif common:
            names.append(common)
        elif latin:
            names.append(latin)
    return sorted(names)


def _find_monograph(selection: str) -> dict | None:
    """Find a monograph by the dropdown selection string.

    The selection may be "Common Name (Latin Name)" or just a name.

    Args:
        selection: The selected herb string from the dropdown.

    Returns:
        The matching monograph dict, or None.
    """
    if not selection or not _monographs_available():
        return None

    selection_lower = selection.lower()

    for m in MONOGRAPHS:
        common = m.get("common_name", "")
        latin = m.get("latin_name", "")
        # Match full display string
        display = f"{common} ({latin})".lower() if common and latin else ""
        if display == selection_lower:
            return m
        # Match common name alone
        if common.lower() == selection_lower:
            return m
        # Match latin name alone
        if latin.lower() == selection_lower:
            return m

    return None


def _render_section(title: str, content: str) -> str:
    """Render a monograph section as Markdown.

    Args:
        title: Section heading.
        content: Section body text.

    Returns:
        Formatted Markdown string, or empty string if no content.
    """
    if not content or content.strip() == "":
        return ""
    return f"### {title}\n\n{content}\n\n"


def _render_list_section(title: str, items: list) -> str:
    """Render a list of items as a bulleted Markdown section.

    Args:
        title: Section heading.
        items: List of strings or dicts to render.

    Returns:
        Formatted Markdown string, or empty string if no items.
    """
    if not items:
        return ""
    lines = [f"### {title}\n"]
    for item in items:
        if isinstance(item, dict):
            # Render dict as "key: value" pairs
            parts = []
            for k, v in item.items():
                if v is not None and v != "":
                    parts.append(f"**{k}:** {v}")
            lines.append(f"- {'; '.join(parts)}")
        else:
            lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _render_dict_section(title: str, data: dict) -> str:
    """Render a dict as a key-value table section.

    Args:
        title: Section heading.
        data: Dictionary of key-value pairs.

    Returns:
        Formatted Markdown string, or empty string if no data.
    """
    if not data:
        return ""
    lines = [f"### {title}\n"]
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    for key, value in data.items():
        if value is not None and value != "":
            display_key = key.replace("_", " ").title()
            if isinstance(value, list):
                display_val = ", ".join(str(v) for v in value)
            else:
                display_val = str(value)
            lines.append(f"| {display_key} | {display_val} |")
    lines.append("")
    return "\n".join(lines)


def _render_monograph(selection: str) -> str:
    """Render a full monograph card for the selected herb.

    Args:
        selection: The selected herb from the dropdown.

    Returns:
        Formatted Markdown string with the monograph content.
    """
    if not selection:
        return "*Select a herb from the dropdown to view its monograph.*"

    mono = _find_monograph(selection)
    if mono is None:
        return f"*No monograph found for '{selection}'.*"

    sections: list[str] = []

    # Header
    common = mono.get("common_name", "Unknown")
    latin = mono.get("latin_name", "")
    header = f"# {common}"
    if latin:
        header += f"\n*{latin}*"
    family = mono.get("family", "")
    if family:
        header += f"\n\nFamily: **{family}**"
    sections.append(header)

    # Nomenclature
    nomenclature_parts = []
    for field in ["other_common_names", "synonyms"]:
        val = mono.get(field)
        if val:
            display = val if isinstance(val, str) else ", ".join(val)
            nomenclature_parts.append(
                f"**{field.replace('_', ' ').title()}:** {display}"
            )
    if nomenclature_parts:
        sections.append(
            _render_section("Nomenclature", "\n\n".join(nomenclature_parts))
        )

    # Plant part
    plant_part = mono.get("plant_part") or mono.get("parts_used")
    if plant_part:
        if isinstance(plant_part, list):
            plant_part = ", ".join(plant_part)
        sections.append(_render_section("Plant Part Used", plant_part))

    # Extraction parameters
    extraction = mono.get("extraction") or mono.get("extraction_parameters")
    if isinstance(extraction, dict):
        sections.append(_render_dict_section("Extraction Parameters", extraction))
    elif extraction:
        sections.append(_render_section("Extraction Parameters", str(extraction)))

    # Constituents
    constituents = mono.get("constituents") or mono.get("key_constituents")
    if isinstance(constituents, list):
        sections.append(_render_list_section("Key Constituents", constituents))
    elif isinstance(constituents, dict):
        sections.append(_render_dict_section("Key Constituents", constituents))
    elif constituents:
        sections.append(_render_section("Key Constituents", str(constituents)))

    # Actions / therapeutic uses
    actions = mono.get("actions") or mono.get("therapeutic_actions")
    if isinstance(actions, list):
        sections.append(_render_list_section("Therapeutic Actions", actions))
    elif actions:
        sections.append(_render_section("Therapeutic Actions", str(actions)))

    # Dosage
    dosage = mono.get("dosage") or mono.get("dose")
    if isinstance(dosage, dict):
        sections.append(_render_dict_section("Dosage", dosage))
    elif isinstance(dosage, list):
        sections.append(_render_list_section("Dosage", dosage))
    elif dosage:
        sections.append(_render_section("Dosage", str(dosage)))

    # Safety / contraindications
    safety_parts = []
    for field in ["safety", "contraindications", "cautions", "pregnancy",
                   "drug_interactions", "side_effects"]:
        val = mono.get(field)
        if val:
            display = val if isinstance(val, str) else ", ".join(str(v) for v in val)
            safety_parts.append(
                f"**{field.replace('_', ' ').title()}:** {display}"
            )
    if safety_parts:
        sections.append(
            _render_section("Safety & Contraindications", "\n\n".join(safety_parts))
        )

    # Energetics
    energetics = mono.get("energetics")
    if isinstance(energetics, dict):
        sections.append(_render_dict_section("Energetics", energetics))
    elif isinstance(energetics, list):
        sections.append(
            _render_section("Energetics", ", ".join(str(e) for e in energetics))
        )
    elif energetics:
        sections.append(_render_section("Energetics", str(energetics)))

    # Notes
    notes = mono.get("notes") or mono.get("additional_notes")
    if notes:
        sections.append(_render_section("Notes", str(notes)))

    if len(sections) <= 1:
        sections.append(
            "\n*This monograph entry has minimal data. "
            "More detail will be added as the database grows.*"
        )

    return "\n\n---\n\n".join(sections)


def build_tab() -> gr.Tab:
    """Build and return the Monograph Viewer tab."""
    with gr.Tab("Monograph Viewer") as tab:
        gr.Markdown(
            "## Herb Monograph Quick Reference\n\n"
            "Browse structured monograph cards for herbs in the database. "
            "Each monograph includes nomenclature, extraction parameters, "
            "key constituents, dosage, safety information, and energetics."
        )

        if not _monographs_available():
            gr.Markdown(
                "> **Monograph data not yet loaded.** This tool will display "
                "detailed herb information once the monograph database is "
                "populated. Monographs are being built incrementally and "
                "will include 50-100 herbs with structured data for each."
            )
            herb_selector = gr.Dropdown(
                label="Select herb",
                choices=[],
                interactive=False,
                info="No monographs available yet.",
            )
        else:
            herb_names = _get_herb_names()
            herb_selector = gr.Dropdown(
                label="Select herb",
                choices=herb_names,
                value=herb_names[0] if herb_names else None,
                allow_custom_value=False,
                info=f"{len(herb_names)} herbs in database.",
            )

        monograph_output = gr.Markdown(
            value=(
                "*Select a herb to view its monograph.*"
                if _monographs_available()
                else "*Awaiting monograph data.*"
            )
        )

        # Pedagogical accordion
        with gr.Accordion("About herbal monographs", open=False):
            gr.Markdown("""
**What is a monograph?**

A herbal monograph is a structured reference document for a single
medicinal plant. It collects the key information a practitioner needs
to safely and effectively use that herb. Think of it as the herb's
"specification sheet."

**Standard monograph sections:**

- **Nomenclature:** Common name, Latin binomial, family, and synonyms.
  Precise identification prevents dangerous plant mix-ups.
- **Plant part used:** Root, leaf, flower, bark, etc. Different parts
  of the same plant can have very different properties.
- **Extraction parameters:** Recommended ratio (e.g., 1:5), alcohol
  percentage, and solvent type. These are calibrated to extract the
  herb's active constituents optimally.
- **Key constituents:** The chemical compounds responsible for the
  herb's therapeutic activity. Understanding these helps explain why
  specific solvents and methods are recommended.
- **Therapeutic actions:** What the herb does (e.g., nervine,
  anti-inflammatory, bitter tonic). Uses standardized herbal
  action terminology.
- **Dosage:** Recommended amounts for various preparation types.
  Usually given as a range for dried herb equivalent.
- **Safety:** Contraindications, drug interactions, pregnancy
  considerations, and cautions. This section is critical.
- **Energetics:** The herb's qualities in traditional frameworks
  (warming/cooling, drying/moistening, taste). Used in holistic
  assessment and formula balancing.

**Where do monographs come from?**

Published monographs draw from pharmacopeial standards (USP, BP, EP),
clinical research, traditional use documentation, and expert
consensus. Key references include the American Herbal Pharmacopoeia
(AHP), German Commission E, and the European Medicines Agency (EMA)
herbal monograph series.

**HerbCalc monographs** are structured for educational use. They are
not a substitute for comprehensive pharmacopeial references or
clinical guidance.
""")

        # Event handler
        if _monographs_available():
            herb_selector.change(
                fn=_render_monograph,
                inputs=[herb_selector],
                outputs=[monograph_output],
            )

    return tab
