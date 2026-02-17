"""Historical Unit Translator (Apothecary focus) for HerbCalc.

Specialized converter for apothecary units (grains, scruples, drams,
minims, apothecary ounces) with bidirectional metric conversion and
clear disambiguation from avoirdupois units.
"""

import gradio as gr

from core.units import convert_all, list_units, get_unit_info


def _get_apothecary_choices() -> list[str]:
    """Build a list of apothecary unit names for the dropdown.

    Includes all apothecary units and a few common metric units
    so users can convert in either direction.
    """
    apothecary_units = list_units(system="apothecary")
    metric_units = list_units(system="metric")
    names = sorted(set(
        u.unit_name for u in apothecary_units + metric_units
    ))
    return names if names else ["grain", "scruple", "dram", "ounce_apothecary", "gram", "milligram"]


def _compute(
    value: float,
    unit: str,
) -> list[list[str]]:
    """Convert to metric and apothecary systems and return tabular data.

    Returns:
        List of rows [unit_name, symbol, value, system] for gr.Dataframe.
    """
    if not unit:
        return [["(select a unit)", "", "", ""]]

    rows = []

    # Get conversions to metric
    try:
        metric_results = convert_all(value, unit, target_system="metric")
        for r in metric_results:
            formatted = _format_value(r.value)
            rows.append([r.unit, r.symbol, formatted, r.system])
    except ValueError as exc:
        rows.append([f"Metric error: {exc}", "", "", ""])
    except Exception as exc:
        rows.append([f"Error: {exc}", "", "", ""])

    # Get conversions to apothecary
    try:
        apothecary_results = convert_all(value, unit, target_system="apothecary")
        for r in apothecary_results:
            formatted = _format_value(r.value)
            rows.append([r.unit, r.symbol, formatted, r.system])
    except ValueError:
        pass  # May fail if unit type mismatch; metric results are enough
    except Exception:
        pass

    if not rows:
        return [["No conversions found for this unit.", "", "", ""]]

    # Add disambiguation note if relevant
    info = get_unit_info(unit)
    if info and info.disambiguation:
        rows.append(["Note", "", info.disambiguation, ""])

    return rows


def _format_value(val: float) -> str:
    """Format a numeric value with adaptive precision."""
    if val == 0:
        return "0"
    elif abs(val) >= 100:
        return f"{val:,.4f}"
    elif abs(val) >= 1:
        return f"{val:,.6f}"
    else:
        return f"{val:.8g}"


def build_tab() -> gr.Tab:
    """Build and return the Apothecary Translator tab."""
    with gr.Tab("Apothecary Translator") as tab:
        gr.Markdown(
            "## Historical Unit Translator (Apothecary)\n"
            "Convert between apothecary units (grains, scruples, drams, "
            "minims) and metric units. Includes disambiguation notes "
            "for commonly confused units."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input")
                value = gr.Number(
                    label="Value",
                    value=1,
                    minimum=0,
                )
                unit = gr.Dropdown(
                    label="Unit",
                    choices=_get_apothecary_choices(),
                    value=None,
                    allow_custom_value=True,
                )
                convert_btn = gr.Button("Convert", variant="primary")

            with gr.Column():
                gr.Markdown("### Results (Metric + Apothecary)")
                results_table = gr.Dataframe(
                    headers=["Unit", "Symbol", "Value", "System"],
                    interactive=False,
                    row_count=1,
                )

        convert_btn.click(
            fn=_compute,
            inputs=[value, unit],
            outputs=[results_table],
        )

        with gr.Accordion("Apothecary vs Avoirdupois", open=False):
            gr.Markdown("""
The apothecary and avoirdupois systems **share some unit names but
use different weights.** This has caused real dispensing errors
throughout the history of pharmacy.

**Key differences:**

| Unit | Apothecary | Avoirdupois |
|------|-----------|-------------|
| Ounce | 31.1035 g (= Troy ounce) | 28.3495 g |
| Pound | 373.242 g (12 oz) | 453.592 g (16 oz) |
| Dram | 3.8879 g | 1.7718 g |

**The grain is the same in both systems** (64.79891 mg) -- it is
the one unit where the two systems agree.

**Apothecary subdivisions:**
- 1 scruple = 20 grains = 1.296 g
- 1 dram (apothecary) = 3 scruples = 60 grains = 3.888 g
- 1 ounce (apothecary) = 8 drams = 31.104 g
- 1 pound (apothecary) = 12 ounces = 373.242 g

**Volume (apothecary):**
- 1 minim ~ 0.0616 mL (approximately 1 drop)
- 1 fluid dram = 60 minims = 3.6967 mL
- 1 fluid ounce = 8 fluid drams = 29.5735 mL

**When reading historical texts:** Always check which system the
author is using. Apothecary symbols (like the ounce sign) can help
disambiguate, but the safest approach is to convert to metric and
verify the dose makes clinical sense.
            """)

    return tab
