"""Multi-Herb Formula Builder for HerbCalc.

Allows users to define a multi-herb formula using parts notation,
individual extraction ratios, and alcohol percentages. Calculates
per-herb weights, menstruum volumes, and a compromise alcohol
percentage for the combined formula.

Computation delegated to core.formulation.build_formula().
"""

import gradio as gr

from core.data_loader import MONOGRAPHS
from core.formulation import build_formula, HerbEntry


def _get_herb_names() -> list[str]:
    """Extract herb names from monograph data for dropdown suggestions."""
    if isinstance(MONOGRAPHS, list) and MONOGRAPHS:
        return sorted(
            m.get("common_name", m.get("latin_name", "Unknown"))
            for m in MONOGRAPHS
            if m.get("common_name") or m.get("latin_name")
        )
    return []


def _monographs_available() -> bool:
    """Check whether monograph data is populated."""
    return isinstance(MONOGRAPHS, list) and len(MONOGRAPHS) > 0


def _calculate_formula(
    target_volume: float,
    herb_data: list[list],
) -> tuple[list[list[str]], str]:
    """Run the formula calculation from herb table data.

    Args:
        target_volume: Target total menstruum volume in mL.
        herb_data: Rows from the interactive Dataframe.
            Each row: [herb_name, parts, ratio, alcohol_pct]

    Returns:
        Tuple of (results_table_rows, summary_text).
    """
    if not herb_data:
        return [["(no herbs entered)", "", "", ""]], "Enter at least one herb."

    # Parse herb entries from the table
    entries: list[HerbEntry] = []
    parse_errors: list[str] = []

    for i, row in enumerate(herb_data):
        if not row or len(row) < 4:
            continue

        name = str(row[0]).strip() if row[0] else ""
        if not name:
            continue

        try:
            parts = float(row[1]) if row[1] else 0
        except (ValueError, TypeError):
            parse_errors.append(
                f"Row {i + 1}: '{row[1]}' is not a valid number for Parts."
            )
            continue

        try:
            ratio = float(row[2]) if row[2] else 5.0
        except (ValueError, TypeError):
            parse_errors.append(
                f"Row {i + 1}: '{row[2]}' is not a valid number for Ratio."
            )
            continue

        try:
            alc_pct = float(row[3]) if row[3] else 45.0
        except (ValueError, TypeError):
            parse_errors.append(
                f"Row {i + 1}: '{row[3]}' is not a valid number for Alcohol %."
            )
            continue

        if parts <= 0:
            parse_errors.append(
                f"Row {i + 1} ({name}): Parts must be greater than zero."
            )
            continue

        if ratio <= 0:
            parse_errors.append(
                f"Row {i + 1} ({name}): Ratio must be greater than zero."
            )
            continue

        entries.append(HerbEntry(
            name=name,
            parts=parts,
            ratio=ratio,
            alcohol_pct=alc_pct,
        ))

    if parse_errors and not entries:
        error_text = "**Input errors:**\n" + "\n".join(f"- {e}" for e in parse_errors)
        return [["(input errors)", "", "", ""]], error_text

    if not entries:
        return [["(no valid herbs)", "", "", ""]], "Enter at least one herb with valid parameters."

    # Validate target volume
    if target_volume is None or target_volume <= 0:
        target_volume = 100.0

    # Run formula calculation
    result = build_formula(
        herbs=entries,
        target_volume_ml=target_volume,
    )

    # Build results table
    results_rows = []
    for herb in result.herbs:
        results_rows.append([
            herb.name,
            f"{herb.weight_g:.2f}",
            f"{herb.menstruum_ml:.2f}",
            f"1:{herb.ratio:.0f} @ {herb.alcohol_pct:.0f}%",
        ])

    # Build summary text
    summary_lines = [
        f"**Total herb weight:** {result.total_herb_weight_g:.2f} g",
        f"**Total menstruum volume:** {result.total_menstruum_ml:.2f} mL",
        f"**Compromise alcohol %:** {result.compromise_alcohol_pct:.1f}%",
    ]

    if result.warnings:
        summary_lines.append("")
        summary_lines.append("**Warnings:**")
        for w in result.warnings:
            summary_lines.append(f"- {w}")

    if parse_errors:
        summary_lines.append("")
        summary_lines.append("**Skipped rows (input errors):**")
        for e in parse_errors:
            summary_lines.append(f"- {e}")

    summary_text = "\n\n".join(summary_lines)

    return results_rows, summary_text


def build_tab() -> gr.Tab:
    """Build and return the Multi-Herb Formula Builder tab."""
    with gr.Tab("Formula Builder") as tab:
        gr.Markdown(
            "## Multi-Herb Formula Builder\n\n"
            "Define a multi-herb formula using parts notation. Each herb "
            "can have its own extraction ratio and alcohol percentage. "
            "The calculator determines per-herb weights, menstruum volumes, "
            "and a compromise alcohol percentage for the blended formula."
        )

        if not _monographs_available():
            gr.Markdown(
                "> **Note:** Monograph data not yet loaded -- enter herb "
                "parameters manually. When the monograph database is populated, "
                "herb selection will auto-fill recommended ratios and alcohol "
                "percentages."
            )

        with gr.Row():
            target_volume = gr.Number(
                label="Target total volume (mL)",
                value=100,
                minimum=1,
                info="Total menstruum volume for the combined formula.",
            )

        gr.Markdown(
            "### Herb Entries\n\n"
            "Enter each herb's name, proportional parts, extraction ratio "
            "(e.g., 5 for 1:5), and target alcohol percentage. "
            "Add or remove rows as needed."
        )

        herb_table = gr.Dataframe(
            value=[
                ["", 1, 5, 45],
                ["", 1, 5, 45],
                ["", 1, 5, 45],
            ],
            headers=["Herb Name", "Parts", "Ratio", "Alcohol %"],
            datatype=["str", "number", "number", "number"],
            col_count=4,
            row_count=3,
            interactive=True,
            label="Formula herbs",
        )

        calculate_btn = gr.Button("Calculate Formula", variant="primary")

        gr.Markdown("### Results")

        results_table = gr.Dataframe(
            value=[],
            headers=["Herb", "Weight (g)", "Menstruum (mL)", "Parameters"],
            datatype=["str", "str", "str", "str"],
            interactive=False,
            label="Per-herb breakdown",
        )

        summary_output = gr.Markdown(
            value="*Enter herbs and click Calculate Formula.*"
        )

        # Pedagogical accordion
        with gr.Accordion("How formula scaling works", open=False):
            gr.Markdown("""
**Parts notation** is a proportional system used in herbal formulation.
Instead of specifying absolute weights, you assign each herb a relative
number of "parts." The calculator then scales these proportions to your
target volume.

**Example:** A formula with three herbs at 3:2:1 parts means:
- Herb A gets 3/6 (50%) of the total volume
- Herb B gets 2/6 (33.3%) of the total volume
- Herb C gets 1/6 (16.7%) of the total volume

For a 120 mL target volume, that yields 60 mL, 40 mL, and 20 mL
of menstruum allocated to each herb respectively.

**Herb weight** for each herb is derived from its allocated menstruum
volume divided by its extraction ratio. A herb allocated 60 mL at a
1:5 ratio needs 60 / 5 = 12 g of dried herb.

**Compromise alcohol percentage** is a weighted average of each herb's
ideal alcohol percentage, weighted by its proportion in the formula.
This is the single concentration you would use if making a combined
menstruum rather than individual tinctures blended afterward.

**When to use combined vs. individual extraction:**
- **Combined menstruum** is simpler (one jar) but uses a compromise
  solvent that may not be ideal for every herb.
- **Individual extraction + blending** gives each herb its optimal
  solvent but requires more containers and a final blending step.

Most teaching programs recommend individual extraction for formulas
where herbs have very different alcohol requirements (e.g., one needs
25% and another needs 70%).
""")

        # Event handler
        calculate_btn.click(
            fn=_calculate_formula,
            inputs=[target_volume, herb_table],
            outputs=[results_table, summary_output],
        )

    return tab
