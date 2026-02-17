"""Universal Unit Converter tool for HerbCalc.

Converts between metric, avoirdupois, apothecary, household, and
historical measurement units. All conversions route through
core.units which uses a base-unit intermediary (gram / milliliter).
"""

import gradio as gr

from core.units import convert_all, list_units


def _get_unit_choices() -> list[str]:
    """Build a sorted list of canonical unit names for the dropdown."""
    all_units = list_units()
    return sorted(set(u.unit_name for u in all_units))


def _compute(
    value: float,
    from_unit: str,
    target_system: str,
) -> list[list[str]]:
    """Convert value to all matching units and return tabular data.

    Returns:
        List of rows [unit_name, symbol, value, system] for gr.Dataframe.
    """
    if not from_unit:
        return [["(select a unit)", "", "", ""]]

    system_filter = None if target_system == "All" else target_system

    try:
        results = convert_all(value, from_unit, target_system=system_filter)
    except ValueError as exc:
        return [[str(exc), "", "", ""]]
    except Exception as exc:
        return [[f"Error: {exc}", "", "", ""]]

    if not results:
        return [["No matching conversions found.", "", "", ""]]

    rows = []
    for r in results:
        # Adaptive formatting
        if r.value == 0:
            formatted = "0"
        elif abs(r.value) >= 100:
            formatted = f"{r.value:,.4f}"
        elif abs(r.value) >= 1:
            formatted = f"{r.value:,.6f}"
        else:
            formatted = f"{r.value:.8g}"

        rows.append([r.unit, r.symbol, formatted, r.system])

    return rows


def build_tab() -> gr.Tab:
    """Build and return the Universal Unit Converter tab."""
    with gr.Tab("Unit Converter") as tab:
        gr.Markdown(
            "## Universal Unit Converter\n"
            "Convert between metric, avoirdupois, apothecary, household, "
            "and historical measurement systems."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input")
                value = gr.Number(
                    label="Value",
                    value=1,
                    minimum=0,
                )
                from_unit = gr.Dropdown(
                    label="From unit",
                    choices=_get_unit_choices(),
                    value=None,
                    allow_custom_value=True,
                )
                target_system = gr.Radio(
                    label="Target system",
                    choices=[
                        "All",
                        "metric",
                        "avoirdupois",
                        "apothecary",
                        "household",
                        "historical",
                    ],
                    value="All",
                )
                convert_btn = gr.Button("Convert", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                results_table = gr.Dataframe(
                    headers=["Unit", "Symbol", "Value", "System"],
                    interactive=False,
                    row_count=1,
                )

        convert_btn.click(
            fn=_compute,
            inputs=[value, from_unit, target_system],
            outputs=[results_table],
        )

        with gr.Accordion("About unit systems", open=False):
            gr.Markdown("""
**Metric (SI):** The international standard. Grams, kilograms, milligrams
for mass; milliliters and liters for volume. Used in scientific and
pharmaceutical contexts worldwide.

**Avoirdupois:** The everyday weight system in the US and UK.
Ounces (oz), pounds (lb). One avoirdupois ounce = 28.3495 g.

**Apothecary:** A historical pharmaceutical system still referenced in
older texts. Grains, scruples, drams, and apothecary ounces.
One apothecary ounce = 31.1035 g -- *not the same as an avoirdupois ounce*.
This difference has caused real dispensing errors; always specify which
ounce you mean.

**Household:** Kitchen measures -- teaspoons, tablespoons, cups.
These are volume measures and inherently imprecise for solids. The
converter provides approximate values with warnings where appropriate.

**Historical:** Traditional measures from various herbal traditions
including TCM (Traditional Chinese Medicine), Ayurvedic, and Unani
systems. Conversions are approximate and may vary by source.
            """)

    return tab
