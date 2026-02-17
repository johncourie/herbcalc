"""Dry Equivalent <-> Extract Converter for HerbCalc.

Bidirectional converter between dried herb weight and tincture volume
at a given extraction ratio. A simple but frequently confusing
calculation for herbalism students.

Computation delegated to core.formulation.dry_equivalent() and
core.formulation.tincture_from_dose().
"""

import gradio as gr

from core.formulation import dry_equivalent, tincture_from_dose


def _convert(
    mode: str,
    value: float,
    ratio: float,
) -> str:
    """Perform the dry-extract conversion.

    Args:
        mode: Direction of conversion.
        value: Input value (grams of herb or mL of tincture).
        ratio: Extraction ratio (e.g., 5 for 1:5).

    Returns:
        Formatted result string with explanation.
    """
    # Validate inputs
    if ratio is None or ratio <= 0:
        return (
            "**Error:** Extraction ratio must be greater than zero.\n\n"
            "The ratio is the second number in the extraction notation. "
            "For a 1:5 tincture, enter 5. For a 1:2 fresh-plant tincture, "
            "enter 2. For a 1:1 fluid extract, enter 1."
        )

    if value is None or value <= 0:
        return "**Error:** Please enter a positive value."

    if mode == "Dried herb -> Tincture volume":
        # Herb weight in grams -> tincture volume in mL
        # tincture_from_dose expects mg, so convert g -> mg
        herb_mg = value * 1000
        try:
            volume_ml = tincture_from_dose(herb_mg, ratio)
        except ValueError as e:
            return f"**Error:** {e}"

        return (
            f"### Result\n\n"
            f"**{value:.2f} g** of dried herb at a **1:{ratio:.0f}** "
            f"extraction ratio is equivalent to:\n\n"
            f"## {volume_ml:.2f} mL of tincture\n\n"
            f"---\n\n"
            f"**Step-by-step:**\n\n"
            f"1. You have {value:.2f} g of dried herb.\n"
            f"2. At a 1:{ratio:.0f} ratio, each gram of herb produces "
            f"{ratio:.0f} mL of tincture.\n"
            f"3. {value:.2f} g x {ratio:.0f} = **{volume_ml:.2f} mL**\n\n"
            f"This means {volume_ml:.2f} mL of a properly prepared "
            f"1:{ratio:.0f} tincture contains the extractable constituents "
            f"from {value:.2f} g of the dried herb."
        )

    else:
        # Tincture volume in mL -> dried herb weight in grams
        try:
            herb_g = dry_equivalent(value, ratio)
        except ValueError as e:
            return f"**Error:** {e}"

        herb_mg = herb_g * 1000

        return (
            f"### Result\n\n"
            f"**{value:.2f} mL** of a **1:{ratio:.0f}** tincture "
            f"is equivalent to:\n\n"
            f"## {herb_g:.4f} g ({herb_mg:.1f} mg) of dried herb\n\n"
            f"---\n\n"
            f"**Step-by-step:**\n\n"
            f"1. You have {value:.2f} mL of tincture.\n"
            f"2. At a 1:{ratio:.0f} ratio, each {ratio:.0f} mL of "
            f"tincture was made from 1 g of dried herb.\n"
            f"3. {value:.2f} mL / {ratio:.0f} = **{herb_g:.4f} g** "
            f"({herb_mg:.1f} mg)\n\n"
            f"This is the weight of dried herb material whose extractable "
            f"constituents are present in {value:.2f} mL of tincture."
        )


def build_tab() -> gr.Tab:
    """Build and return the Dry <-> Extract Converter tab."""
    with gr.Tab("Dry/Extract Converter") as tab:
        gr.Markdown(
            "## Dry Equivalent <-> Extract Converter\n\n"
            "Convert between dried herb weight and tincture volume "
            "using the extraction ratio. Essential for comparing doses "
            "across different preparation forms."
        )

        mode = gr.Radio(
            label="Conversion direction",
            choices=[
                "Dried herb -> Tincture volume",
                "Tincture -> Dried herb equivalent",
            ],
            value="Dried herb -> Tincture volume",
        )

        with gr.Row():
            with gr.Column():
                value_input = gr.Number(
                    label="Value",
                    value=1.0,
                    minimum=0,
                    info=(
                        "Grams of dried herb (first mode) "
                        "or mL of tincture (second mode)."
                    ),
                )
            with gr.Column():
                ratio_input = gr.Number(
                    label="Extraction ratio",
                    value=5,
                    minimum=0.1,
                    info="The second number in the ratio (e.g., 5 for 1:5).",
                )

        convert_btn = gr.Button("Convert", variant="primary")

        result_output = gr.Markdown(
            value="*Select a mode, enter a value, and click Convert.*"
        )

        # Quick reference table
        with gr.Accordion("Quick reference: common ratios", open=False):
            gr.Markdown("""
| Ratio | Type | Per mL of Tincture | 5 mL Dose = |
|-------|------|--------------------|-------------|
| 1:1 | Fluid extract | 1,000 mg (1 g) | 5,000 mg (5 g) |
| 1:2 | Fresh plant tincture | 500 mg | 2,500 mg |
| 1:3 | Strong tincture | 333 mg | 1,667 mg |
| 1:5 | Standard dry tincture | 200 mg | 1,000 mg (1 g) |
| 1:10 | Weak tincture | 100 mg | 500 mg |
""")

        # Pedagogical accordion
        with gr.Accordion("Why this conversion matters", open=False):
            gr.Markdown("""
**The most common confusion in herbal dosing** is comparing doses
across different preparation types. A monograph might recommend
"3 g of dried herb daily" -- but if you are using a tincture, how
much tincture is that?

**The extraction ratio is the key.**

A 1:5 tincture means that 1 gram of dried herb was macerated in
5 mL of menstruum (the liquid solvent). After straining, those 5 mL
contain the extracted constituents of that 1 gram of herb.

So to get the equivalent of 3 g of dried herb from a 1:5 tincture:
- 3 g x 5 = 15 mL of tincture

**Important caveats:**

- This is an *equivalence*, not an exact substitution. Not all
  constituents extract equally into every solvent. A water infusion
  of the same herb extracts different compounds than an alcohol
  tincture.
- Fresh plant tinctures (typically 1:2) use the fresh weight, which
  includes water content. The actual dried-herb equivalent is higher
  per mL than the ratio suggests.
- Fluid extracts (1:1) are the most concentrated standard preparation
  and serve as the pharmacopeial reference for dosing.

**When in doubt:** Use the ratio specified in the monograph for the
specific preparation type, and confirm with a qualified practitioner.
""")

        # Event handler
        convert_btn.click(
            fn=_convert,
            inputs=[mode, value_input, ratio_input],
            outputs=[result_output],
        )

    return tab
