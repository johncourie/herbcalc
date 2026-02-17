"""Percentage Expression Translator for HerbCalc.

Converts between w/w (weight-by-weight), w/v (weight-by-volume),
and v/v (volume-by-volume) percentage conventions using density
corrections for ethanol-water and glycerin-water systems.
"""

import gradio as gr

from core.solvents import convert_percentage


def _compute(
    value: float,
    from_convention: str,
    substance: str,
) -> tuple[float, float, float, str]:
    """Convert a percentage value to all three conventions.

    Returns:
        Tuple of (vv_value, wv_value, ww_value, warnings_markdown).
    """
    # Map display labels to internal convention codes
    convention_map = {
        "v/v": "vv",
        "w/v": "wv",
        "w/w": "ww",
    }
    from_code = convention_map.get(from_convention)
    if from_code is None:
        return 0.0, 0.0, 0.0, f"**Error:** Unknown convention '{from_convention}'."

    try:
        vv_val = convert_percentage(
            value=value,
            from_convention=from_code,
            to_convention="vv",
            substance=substance,
        )
        wv_val = convert_percentage(
            value=value,
            from_convention=from_code,
            to_convention="wv",
            substance=substance,
        )
        ww_val = convert_percentage(
            value=value,
            from_convention=from_code,
            to_convention="ww",
            substance=substance,
        )
    except ValueError as exc:
        return 0.0, 0.0, 0.0, f"**Error:** {exc}"
    except Exception as exc:
        return 0.0, 0.0, 0.0, f"**Calculation error:** {exc}"

    return (
        round(vv_val, 4),
        round(wv_val, 4),
        round(ww_val, 4),
        "",
    )


def build_tab() -> gr.Tab:
    """Build and return the Percentage Expression Translator tab."""
    with gr.Tab("Percentage Expressions") as tab:
        gr.Markdown(
            "## Percentage Expression Translator\n"
            "Convert between v/v, w/v, and w/w percentage conventions. "
            "Density corrections are applied automatically for the selected substance."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input")
                value = gr.Number(
                    label="Percentage value",
                    value=40,
                    minimum=0,
                    maximum=100,
                )
                from_convention = gr.Radio(
                    label="This value is expressed as",
                    choices=["v/v", "w/v", "w/w"],
                    value="v/v",
                )
                substance = gr.Radio(
                    label="Substance",
                    choices=["ethanol", "glycerin"],
                    value="ethanol",
                )
                calc_btn = gr.Button("Convert", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                vv_output = gr.Number(
                    label="v/v (volume/volume) %",
                    interactive=False,
                )
                wv_output = gr.Number(
                    label="w/v (weight/volume) %",
                    interactive=False,
                )
                ww_output = gr.Number(
                    label="w/w (weight/weight) %",
                    interactive=False,
                )
                warnings_md = gr.Markdown(label="Warnings", value="")

        calc_btn.click(
            fn=_compute,
            inputs=[value, from_convention, substance],
            outputs=[vv_output, wv_output, ww_output, warnings_md],
        )

        with gr.Accordion("What do w/w, w/v, and v/v mean?", open=False):
            gr.Markdown("""
Percentage concentration can be expressed three different ways,
and they are **not interchangeable** unless density corrections
are applied. This matters because ethanol is lighter than water
(density ~0.789 g/mL) and glycerin is heavier (density ~1.261 g/mL).

**v/v (volume by volume):** The most common convention for alcohol
in herbalism. "40% v/v" means 40 mL of pure ethanol in every 100 mL
of solution. This is the standard in the US and most herbal texts.

**w/v (weight by volume):** Used in some pharmaceutical references.
"40% w/v" means 40 grams of solute per 100 mL of solution.

**w/w (weight by weight):** Common in European pharmacopoeias and
industrial chemistry. "40% w/w" means 40 grams of solute per
100 grams of solution.

**Why does this matter for herbalists?**

A monograph that specifies "45% alcohol" almost always means 45% v/v.
But if you encounter a European pharmaceutical reference using w/w,
a direct number substitution would give the wrong concentration.
For ethanol at 40% v/v:
- w/v = 40 x 0.789 = 31.56%
- w/w = (40 x 0.789) / mixture_density

The difference is significant enough to affect extraction quality.
This tool handles the density math so you can convert between
conventions confidently.
            """)

    return tab
