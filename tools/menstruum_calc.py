"""Tincture Menstruum Calculator — the flagship HerbCalc tool.

Calculates the volumes of ethanol source, water, and glycerin needed
for an herbal extraction based on herb weight, extraction ratio,
ethanol source concentration, target alcohol percentage, and optional
glycerin percentage.

Defaults match the original herbcalc.php for continuity:
100g herb, 1:5 ratio, 94% ethanol source, 40% target alcohol, 0% glycerin.
"""

import gradio as gr

from core.solvents import calculate_menstruum
from core.validation import validate_menstruum_inputs


def _compute(
    herb_weight: float,
    ratio: float,
    ethanol_source_pct: float,
    target_alcohol_pct: float,
    glycerin_pct: float,
    solvent_mode: str,
) -> tuple[float, float, float, float, str]:
    """Run validation then calculation, returning display values.

    Returns:
        Tuple of (total_volume, ethanol_source_volume, water_volume,
                  glycerin_volume, warnings_markdown).
    """
    # Validate inputs
    try:
        validations = validate_menstruum_inputs(
            herb_g=herb_weight,
            ratio=ratio,
            ethanol_source=ethanol_source_pct,
            target_alc=target_alcohol_pct,
            glycerin_pct=glycerin_pct,
        )
    except Exception as exc:
        return 0.0, 0.0, 0.0, 0.0, f"**Validation error:** {exc}"

    # Collect errors and warnings
    errors = [v for v in validations if not v.valid]
    warnings = [v for v in validations if v.valid and v.message]

    if errors:
        error_text = "\n\n".join(
            f"**{e.field_name}:** {e.message}" for e in errors
        )
        return 0.0, 0.0, 0.0, 0.0, error_text

    # Calculate
    try:
        result = calculate_menstruum(
            herb_weight_g=herb_weight,
            ratio=ratio,
            ethanol_source_pct=ethanol_source_pct,
            target_alcohol_pct=target_alcohol_pct,
            glycerin_pct=glycerin_pct,
            solvent_mode=solvent_mode,
        )
    except Exception as exc:
        return 0.0, 0.0, 0.0, 0.0, f"**Calculation error:** {exc}"

    # Build warnings markdown
    warning_lines = []
    for w in warnings:
        warning_lines.append(f"**{w.field_name}:** {w.message}")
    for w in result.warnings:
        warning_lines.append(f"**Note:** {w}")

    warnings_md = "\n\n".join(warning_lines) if warning_lines else ""

    return (
        round(result.total_volume_ml, 2),
        round(result.ethanol_source_ml, 2),
        round(result.added_water_ml, 2),
        round(result.glycerin_ml, 2),
        warnings_md,
    )


def build_tab() -> gr.Tab:
    """Build and return the Tincture Menstruum Calculator tab."""
    with gr.Tab("Menstruum Calculator") as tab:
        gr.Markdown(
            "## Tincture Menstruum Calculator\n"
            "Calculate the volumes of ethanol source, water, and glycerin "
            "needed for your herbal extraction."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Inputs")
                herb_weight = gr.Number(
                    label="Herb weight (grams)",
                    value=100,
                    minimum=0.01,
                )
                ratio = gr.Number(
                    label="Extraction ratio (e.g., 5 for 1:5)",
                    value=5,
                    minimum=1,
                )
                ethanol_source_pct = gr.Number(
                    label="Ethanol source concentration (%)",
                    value=94,
                    minimum=0,
                    maximum=100,
                )
                target_alcohol_pct = gr.Number(
                    label="Target alcohol in menstruum (%)",
                    value=40,
                    minimum=0,
                    maximum=100,
                )
                glycerin_pct = gr.Number(
                    label="Glycerin in menstruum (%)",
                    value=0,
                    minimum=0,
                    maximum=100,
                )
                solvent_mode = gr.Radio(
                    label="Solvent mode",
                    choices=["hydroethanolic", "glycerite", "acetum"],
                    value="hydroethanolic",
                )
                calc_btn = gr.Button("Calculate", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                total_volume = gr.Number(
                    label="Total menstruum volume (mL)",
                    interactive=False,
                )
                ethanol_source_volume = gr.Number(
                    label="Ethanol source volume (mL)",
                    interactive=False,
                )
                water_volume = gr.Number(
                    label="Water to add (mL)",
                    interactive=False,
                )
                glycerin_volume = gr.Number(
                    label="Glycerin volume (mL)",
                    interactive=False,
                )
                warnings_md = gr.Markdown(label="Warnings", value="")

        calc_btn.click(
            fn=_compute,
            inputs=[
                herb_weight,
                ratio,
                ethanol_source_pct,
                target_alcohol_pct,
                glycerin_pct,
                solvent_mode,
            ],
            outputs=[
                total_volume,
                ethanol_source_volume,
                water_volume,
                glycerin_volume,
                warnings_md,
            ],
        )

        with gr.Accordion("How is the menstruum calculated?", open=False):
            gr.Markdown("""
**Total menstruum** = herb weight x extraction ratio

The ratio (e.g., 1:5) means 1 gram of herb to 5 mL of menstruum.
A 1:5 tincture of 100 g herb needs 500 mL total liquid.

**Solvent breakdown:**

1. **Glycerin volume** = total menstruum x (glycerin % / 100)
2. **Pure ethanol volume** = total menstruum x (target alcohol % / 100)
3. **Water volume** = total menstruum - glycerin - pure ethanol

Because your ethanol source is not 100% pure (e.g., 94% Everclear
contains 6% water), the calculator tells you how much *source alcohol*
to measure out and how much *additional water* to add:

- **Ethanol source volume** = pure ethanol needed / (source concentration / 100)
- **Water to add** = total water needed - water already present in the ethanol source

For example, with 100 g herb at 1:5 ratio, 94% ethanol source, and 40% target:
- Total menstruum = 500 mL
- Pure ethanol needed = 200 mL
- Ethanol source to measure = 200 / 0.94 = 212.77 mL
- Water in that source = 212.77 - 200 = 12.77 mL
- Total water needed = 300 mL
- Additional water to add = 300 - 12.77 = 287.23 mL

**Note:** "Ethanol source volume" is the amount of your actual alcohol
(Everclear, vodka, etc.) to measure out -- not the volume of pure ethanol.
            """)

    return tab
