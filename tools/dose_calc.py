"""Dosage Scaler for HerbCalc.

Bidirectional tool for converting between tincture volumes and
dried herb equivalents, plus calculating doses-per-bottle counts
for common bottle sizes.

Computation delegated to core.formulation.dry_equivalent() and
core.formulation.tincture_from_dose().
"""

import gradio as gr

from core.formulation import dry_equivalent, tincture_from_dose


def _calculate_dose(
    mode: str,
    tincture_ml: float,
    herb_dose_mg: float,
    ratio: float,
    bottle_size: str,
    custom_size: float,
) -> tuple[str, str]:
    """Perform dosage calculation based on selected mode.

    Args:
        mode: Calculation direction.
        tincture_ml: Tincture volume input (mL).
        herb_dose_mg: Herb dose input (mg).
        ratio: Extraction ratio (e.g., 5 for 1:5).
        bottle_size: Selected bottle size preset or "Custom".
        custom_size: Custom bottle size in mL.

    Returns:
        Tuple of (result_text, doses_per_bottle_text).
    """
    # Validate ratio
    if ratio is None or ratio <= 0:
        return (
            "**Error:** Extraction ratio must be greater than zero. "
            "A ratio of 5 means 1:5 (1 g herb per 5 mL menstruum).",
            "",
        )

    # Determine effective bottle size
    bottle_sizes = {"30 mL": 30, "60 mL": 60, "120 mL": 120}
    if bottle_size == "Custom":
        effective_bottle = custom_size if custom_size and custom_size > 0 else None
    else:
        effective_bottle = bottle_sizes.get(bottle_size, 30)

    if mode == "Tincture -> Herb equivalent":
        # Tincture volume -> dried herb weight
        if tincture_ml is None or tincture_ml <= 0:
            return (
                "**Error:** Enter a positive tincture volume in mL.",
                "",
            )

        try:
            herb_g = dry_equivalent(tincture_ml, ratio)
        except ValueError as e:
            return f"**Error:** {e}", ""

        herb_mg = herb_g * 1000

        result = (
            f"### Result\n\n"
            f"**{tincture_ml:.2f} mL** of a 1:{ratio:.0f} tincture "
            f"contains the equivalent of:\n\n"
            f"- **{herb_g:.4f} g** ({herb_mg:.1f} mg) dried herb\n\n"
            f"*Calculation: {tincture_ml} mL / {ratio:.0f} = "
            f"{herb_g:.4f} g*"
        )

        # Doses per bottle
        if effective_bottle and effective_bottle > 0:
            doses = effective_bottle / tincture_ml
            bottle_label = (
                f"{effective_bottle:.0f} mL"
                if bottle_size == "Custom"
                else bottle_size
            )
            doses_text = (
                f"### Doses per Bottle\n\n"
                f"At **{tincture_ml:.2f} mL per dose** in a "
                f"**{bottle_label}** bottle:\n\n"
                f"- **{doses:.1f} doses** per bottle\n"
                f"- Total herb equivalent per bottle: "
                f"**{dry_equivalent(effective_bottle, ratio) * 1000:.1f} mg** "
                f"({dry_equivalent(effective_bottle, ratio):.2f} g)"
            )
        else:
            doses_text = ""

        return result, doses_text

    else:
        # Herb dose -> tincture volume
        if herb_dose_mg is None or herb_dose_mg <= 0:
            return (
                "**Error:** Enter a positive herb dose in mg.",
                "",
            )

        try:
            volume_ml = tincture_from_dose(herb_dose_mg, ratio)
        except ValueError as e:
            return f"**Error:** {e}", ""

        result = (
            f"### Result\n\n"
            f"To deliver **{herb_dose_mg:.1f} mg** "
            f"({herb_dose_mg / 1000:.4f} g) of dried herb equivalent "
            f"from a 1:{ratio:.0f} tincture, you need:\n\n"
            f"- **{volume_ml:.2f} mL** of tincture\n\n"
            f"*Calculation: ({herb_dose_mg} mg / 1000) x {ratio:.0f} = "
            f"{volume_ml:.2f} mL*"
        )

        # Doses per bottle
        if effective_bottle and effective_bottle > 0 and volume_ml > 0:
            doses = effective_bottle / volume_ml
            bottle_label = (
                f"{effective_bottle:.0f} mL"
                if bottle_size == "Custom"
                else bottle_size
            )
            doses_text = (
                f"### Doses per Bottle\n\n"
                f"At **{volume_ml:.2f} mL per dose** in a "
                f"**{bottle_label}** bottle:\n\n"
                f"- **{doses:.1f} doses** per bottle\n"
                f"- Total herb equivalent per bottle: "
                f"**{dry_equivalent(effective_bottle, ratio) * 1000:.1f} mg** "
                f"({dry_equivalent(effective_bottle, ratio):.2f} g)"
            )
        else:
            doses_text = ""

        return result, doses_text


def build_tab() -> gr.Tab:
    """Build and return the Dosage Scaler tab."""
    with gr.Tab("Dosage Scaler") as tab:
        gr.Markdown(
            "## Dosage Scaler\n\n"
            "Convert between tincture volumes and dried herb equivalents. "
            "Calculate how many doses fit in a standard bottle size."
        )

        mode = gr.Radio(
            label="Calculation mode",
            choices=[
                "Tincture -> Herb equivalent",
                "Herb dose -> Tincture volume",
            ],
            value="Tincture -> Herb equivalent",
        )

        with gr.Row():
            with gr.Column():
                tincture_ml = gr.Number(
                    label="Tincture volume (mL)",
                    value=5,
                    minimum=0,
                    info="Volume of tincture per dose.",
                )
                herb_dose_mg = gr.Number(
                    label="Herb dose (mg)",
                    value=500,
                    minimum=0,
                    info="Target dried herb equivalent per dose.",
                )
            with gr.Column():
                ratio = gr.Number(
                    label="Extraction ratio",
                    value=5,
                    minimum=0.1,
                    info="The second number in the ratio (e.g., 5 for 1:5).",
                )

        with gr.Row():
            bottle_size = gr.Radio(
                label="Bottle size",
                choices=["30 mL", "60 mL", "120 mL", "Custom"],
                value="30 mL",
            )
            custom_size = gr.Number(
                label="Custom bottle size (mL)",
                value=50,
                minimum=1,
                visible=True,
                info="Enter a custom bottle size if 'Custom' is selected.",
            )

        calculate_btn = gr.Button("Calculate", variant="primary")

        result_output = gr.Markdown(
            value="*Select a mode and enter values, then click Calculate.*"
        )
        doses_output = gr.Markdown(value="")

        # Pedagogical accordion
        with gr.Accordion("Understanding extraction ratios and dosing", open=False):
            gr.Markdown("""
**Extraction ratios** describe the concentration of an herbal tincture
as a ratio of herb weight to menstruum volume.

- **1:5** means 1 gram of dried herb was extracted in 5 mL of menstruum.
  Each mL of finished tincture contains the equivalent of 0.2 g (200 mg)
  of dried herb.
- **1:2** (often used for fresh plant tinctures) means 1 gram of herb
  per 2 mL. Each mL contains 0.5 g (500 mg) equivalent.
- **1:1** (fluid extract) means 1 gram per 1 mL -- the most
  concentrated standard preparation.

**Converting doses:**

If a monograph recommends "500 mg dried herb equivalent three times
daily" and you have a 1:5 tincture:
- 500 mg = 0.5 g
- 0.5 g x 5 = 2.5 mL per dose
- 3 doses/day = 7.5 mL daily

**Doses per bottle** helps you estimate:
- How long a bottle will last at a given dose
- How many bottles to prepare for a course of treatment
- Whether your bottle size is practical for the prescribed regimen

**Common bottle sizes:**
- **30 mL (1 oz):** 1-2 week supply at typical dosing
- **60 mL (2 oz):** 2-4 week supply; most common retail size
- **120 mL (4 oz):** 1-2 month supply; bulk/clinical size
""")

        # Event handler
        calculate_btn.click(
            fn=_calculate_dose,
            inputs=[mode, tincture_ml, herb_dose_mg, ratio, bottle_size, custom_size],
            outputs=[result_output, doses_output],
        )

    return tab
