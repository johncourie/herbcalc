"""Constituent x Solvent Affinity Reference Viewer for HerbCalc.

Interactive matrix viewer for exploring which solvents best extract
which classes of plant constituents. Supports browsing by constituent
class or by solvent.

Data sourced from core.data_loader.AFFINITY_MATRIX.
"""

import gradio as gr

from core.data_loader import AFFINITY_MATRIX


def _data_available() -> bool:
    """Check whether affinity matrix data is populated."""
    if isinstance(AFFINITY_MATRIX, dict):
        return bool(AFFINITY_MATRIX.get("matrix") or AFFINITY_MATRIX.get("constituents"))
    if isinstance(AFFINITY_MATRIX, list):
        return len(AFFINITY_MATRIX) > 0
    return False


def _get_constituents() -> list[str]:
    """Extract constituent class names from the affinity matrix."""
    if isinstance(AFFINITY_MATRIX, dict):
        # Try "matrix" key: list of {constituent, solvents: {...}}
        matrix = AFFINITY_MATRIX.get("matrix", [])
        if matrix:
            return sorted(
                entry.get("constituent_class", entry.get("constituent", ""))
                for entry in matrix
                if entry.get("constituent_class") or entry.get("constituent")
            )
        # Try "constituents" key
        constituents = AFFINITY_MATRIX.get("constituents", [])
        if isinstance(constituents, list):
            return sorted(
                c.get("name", c.get("class", ""))
                for c in constituents
                if c.get("name") or c.get("class")
            )
    return []


def _get_solvents() -> list[str]:
    """Extract solvent names from the affinity matrix."""
    if isinstance(AFFINITY_MATRIX, dict):
        matrix = AFFINITY_MATRIX.get("matrix", [])
        if matrix:
            solvent_set: set[str] = set()
            for entry in matrix:
                solvents = entry.get("solvents", {})
                if isinstance(solvents, dict):
                    solvent_set.update(solvents.keys())
                elif isinstance(solvents, list):
                    for s in solvents:
                        if isinstance(s, dict):
                            name = s.get("solvent", s.get("name", ""))
                            if name:
                                solvent_set.add(name)
            return sorted(solvent_set)

        # Try "solvents" key
        solvents = AFFINITY_MATRIX.get("solvents", [])
        if isinstance(solvents, list):
            return sorted(
                s.get("name", s.get("id", ""))
                for s in solvents
                if s.get("name") or s.get("id")
            )
    return []


def _lookup_by_constituent(constituent: str) -> list[list[str]]:
    """Look up extraction efficiencies for a given constituent class.

    Args:
        constituent: Name of the constituent class.

    Returns:
        Rows for the Dataframe: [solvent, efficiency, notes].
    """
    if not constituent or not isinstance(AFFINITY_MATRIX, dict):
        return [["(no data)", "", ""]]

    matrix = AFFINITY_MATRIX.get("matrix", [])
    for entry in matrix:
        name = entry.get("constituent_class", entry.get("constituent", ""))
        if name.lower() == constituent.lower():
            solvents = entry.get("solvents", {})
            rows = []
            if isinstance(solvents, dict):
                for solvent_name, info in sorted(solvents.items()):
                    if isinstance(info, dict):
                        efficiency = info.get("efficiency", info.get("rating", ""))
                        notes = info.get("notes", info.get("note", ""))
                    else:
                        efficiency = str(info)
                        notes = ""
                    rows.append([solvent_name, str(efficiency), str(notes or "")])
            elif isinstance(solvents, list):
                for s in solvents:
                    if isinstance(s, dict):
                        solvent_name = s.get("solvent", s.get("name", ""))
                        efficiency = s.get("efficiency", s.get("rating", ""))
                        notes = s.get("notes", s.get("note", ""))
                        rows.append([
                            str(solvent_name),
                            str(efficiency),
                            str(notes or ""),
                        ])
            if rows:
                return rows
            return [["(no solvent data for this constituent)", "", ""]]

    return [["(constituent not found)", "", ""]]


def _lookup_by_solvent(solvent: str) -> list[list[str]]:
    """Look up what a given solvent extracts and how well.

    Args:
        solvent: Name of the solvent.

    Returns:
        Rows for the Dataframe: [constituent, efficiency, notes].
    """
    if not solvent or not isinstance(AFFINITY_MATRIX, dict):
        return [["(no data)", "", ""]]

    matrix = AFFINITY_MATRIX.get("matrix", [])
    rows = []

    for entry in matrix:
        constituent = entry.get("constituent_class", entry.get("constituent", ""))
        solvents = entry.get("solvents", {})

        if isinstance(solvents, dict):
            if solvent in solvents:
                info = solvents[solvent]
                if isinstance(info, dict):
                    efficiency = info.get("efficiency", info.get("rating", ""))
                    notes = info.get("notes", info.get("note", ""))
                else:
                    efficiency = str(info)
                    notes = ""
                rows.append([
                    str(constituent),
                    str(efficiency),
                    str(notes or ""),
                ])
            else:
                # Check case-insensitive
                for s_name, info in solvents.items():
                    if s_name.lower() == solvent.lower():
                        if isinstance(info, dict):
                            efficiency = info.get("efficiency", info.get("rating", ""))
                            notes = info.get("notes", info.get("note", ""))
                        else:
                            efficiency = str(info)
                            notes = ""
                        rows.append([
                            str(constituent),
                            str(efficiency),
                            str(notes or ""),
                        ])
                        break
        elif isinstance(solvents, list):
            for s in solvents:
                if isinstance(s, dict):
                    s_name = s.get("solvent", s.get("name", ""))
                    if s_name.lower() == solvent.lower():
                        efficiency = s.get("efficiency", s.get("rating", ""))
                        notes = s.get("notes", s.get("note", ""))
                        rows.append([
                            str(constituent),
                            str(efficiency),
                            str(notes or ""),
                        ])
                        break

    if rows:
        return rows
    return [["(no data found for this solvent)", "", ""]]


def _handle_query(
    mode: str,
    selector_value: str,
) -> list[list[str]]:
    """Route the query based on selected mode.

    Args:
        mode: "By constituent" or "By solvent".
        selector_value: The selected constituent or solvent name.

    Returns:
        Rows for the Dataframe output.
    """
    if not selector_value:
        return [["(select an item from the dropdown)", "", ""]]

    if mode == "By constituent":
        return _lookup_by_constituent(selector_value)
    else:
        return _lookup_by_solvent(selector_value)


def _update_selector_choices(mode: str) -> gr.Dropdown:
    """Update the selector dropdown choices based on mode.

    Args:
        mode: "By constituent" or "By solvent".

    Returns:
        Updated Dropdown component.
    """
    if mode == "By constituent":
        choices = _get_constituents()
        label = "Select constituent class"
    else:
        choices = _get_solvents()
        label = "Select solvent"

    return gr.Dropdown(
        choices=choices,
        value=choices[0] if choices else None,
        label=label,
    )


def build_tab() -> gr.Tab:
    """Build and return the Solvent Affinity Reference tab."""
    with gr.Tab("Solvent Affinity") as tab:
        gr.Markdown(
            "## Constituent x Solvent Affinity Reference\n\n"
            "Explore which solvents are most effective for extracting "
            "different classes of plant constituents. Browse by "
            "constituent class or by solvent."
        )

        if not _data_available():
            gr.Markdown(
                "> **Affinity matrix data not yet loaded.** This tool will "
                "display an interactive extraction efficiency matrix once the "
                "affinity data is populated. The matrix covers approximately "
                "18 constituent classes across 8 solvent categories."
            )

        mode = gr.Radio(
            label="Browse by",
            choices=["By constituent", "By solvent"],
            value="By constituent",
        )

        # Build initial choices based on default mode
        initial_constituents = _get_constituents()
        initial_solvents = _get_solvents()
        initial_choices = initial_constituents if initial_constituents else initial_solvents

        selector = gr.Dropdown(
            label="Select constituent class",
            choices=initial_choices,
            value=initial_choices[0] if initial_choices else None,
            allow_custom_value=False,
        )

        query_btn = gr.Button("Look Up", variant="primary")

        # Column headers change by mode, but Dataframe shows the generalized version
        results_table = gr.Dataframe(
            value=[],
            headers=["Item", "Efficiency", "Notes"],
            datatype=["str", "str", "str"],
            interactive=False,
            label="Extraction efficiencies",
        )

        # Pedagogical accordion
        with gr.Accordion("Understanding solvent affinity", open=False):
            gr.Markdown("""
**Why does solvent choice matter?**

Different plant constituents dissolve in different solvents. Choosing
the right solvent (or solvent mixture) is the single most important
decision in herbal extraction. It determines which therapeutic
compounds end up in your finished preparation.

**The basic principle: "like dissolves like"**

- **Water** extracts polar compounds: mucilage, tannins (partially),
  some alkaloids, minerals, water-soluble vitamins, polysaccharides.
- **Ethanol (alcohol)** extracts moderately polar to non-polar
  compounds: alkaloids, glycosides, essential oils, resins, some
  tannins. Higher alcohol percentages extract less polar compounds.
- **Glycerin** extracts a subset of what water and low-alcohol
  solutions extract. Less effective than ethanol for most constituents
  but useful for alcohol-free preparations.
- **Vinegar (acetic acid)** extracts alkaloids particularly well
  and some minerals. Traditional medium for certain preparations.
- **Oil** extracts non-polar, lipophilic compounds: essential oils
  (partially), fat-soluble vitamins, carotenoids, some resins.

**Alcohol percentage matters:**

The target alcohol percentage in a tincture is not arbitrary. It is
chosen to match the solubility profile of the herb's key constituents:

| Alcohol % | Best For |
|-----------|----------|
| 25-40% | Mucilaginous herbs, tannin-rich herbs |
| 40-60% | Most herbs (general-purpose range) |
| 60-70% | Alkaloid-rich herbs, some glycosides |
| 70-90% | Resins, gums, volatile oils |
| 90-95% | Pure resins (e.g., myrrh, propolis) |

**The affinity matrix** in this tool summarizes these relationships.
Use it to understand why a monograph recommends a specific solvent
percentage, or to make informed choices when formulating your own
extractions.
""")

        # Event handlers
        mode.change(
            fn=_update_selector_choices,
            inputs=[mode],
            outputs=[selector],
        )

        query_btn.click(
            fn=_handle_query,
            inputs=[mode, selector],
            outputs=[results_table],
        )

        # Also trigger on selector change for convenience
        selector.change(
            fn=_handle_query,
            inputs=[mode, selector],
            outputs=[results_table],
        )

    return tab
