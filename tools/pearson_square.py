"""Pearson's Square Alcohol Dilution Calculator for HerbCalc.

Calculates how much of a source alcohol and how much water to combine
to achieve a target concentration at a desired total volume.
"""

import gradio as gr

from core.solvents import pearson_square


def _compute(
    source_concentration: float,
    target_concentration: float,
    total_volume: float,
) -> tuple[float, float, str]:
    """Run the Pearson's square calculation.

    Returns:
        Tuple of (source_volume, diluent_volume, warnings_markdown).
    """
    try:
        result = pearson_square(
            source_concentration=source_concentration,
            target_concentration=target_concentration,
            total_volume_ml=total_volume,
        )
    except ValueError as exc:
        return 0.0, 0.0, f"**Error:** {exc}"
    except Exception as exc:
        return 0.0, 0.0, f"**Calculation error:** {exc}"

    warnings_md = ""
    if result.warnings:
        warnings_md = "\n\n".join(
            f"**Note:** {w}" for w in result.warnings
        )

    return (
        round(result.source_volume_ml, 2),
        round(result.diluent_volume_ml, 2),
        warnings_md,
    )


def build_tab() -> gr.Tab:
    """Build and return the Pearson's Square tab."""
    with gr.Tab("Pearson's Square") as tab:
        gr.Markdown(
            "## Alcohol Dilution Calculator (Pearson's Square)\n"
            "Calculate how much of your alcohol source and how much water "
            "to combine to reach a target concentration."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Inputs")
                source_concentration = gr.Number(
                    label="Source alcohol concentration (%)",
                    value=95,
                    minimum=0.1,
                    maximum=100,
                )
                target_concentration = gr.Number(
                    label="Target alcohol concentration (%)",
                    value=40,
                    minimum=0,
                    maximum=100,
                )
                total_volume = gr.Number(
                    label="Desired total volume (mL)",
                    value=500,
                    minimum=0.1,
                )
                calc_btn = gr.Button("Calculate", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                source_volume = gr.Number(
                    label="Source alcohol to measure (mL)",
                    interactive=False,
                )
                diluent_volume = gr.Number(
                    label="Water to add (mL)",
                    interactive=False,
                )
                warnings_md = gr.Markdown(label="Warnings", value="")

        calc_btn.click(
            fn=_compute,
            inputs=[source_concentration, target_concentration, total_volume],
            outputs=[source_volume, diluent_volume, warnings_md],
        )

        with gr.Accordion("What is Pearson's Square?", open=False):
            gr.Markdown("""
**Pearson's Square** (also called the rectangle or box method) is a
visual shortcut for solving dilution problems. It determines the ratio
of two solutions needed to achieve a target concentration.

**How it works:**

Write the source concentration (high) and the diluent concentration
(low, usually 0 for water) on the left side. Write the target
concentration in the center. Then cross-subtract:

```
Source (S)           |           Target (T) - Diluent (D) = parts Source
                Target (T)
Diluent (D)          |           Source (S) - Target (T) = parts Diluent
```

For alcohol dilution where the diluent is water (0%):
- Parts source = target concentration
- Parts diluent = source concentration - target concentration

**Example:** Diluting 95% ethanol to 40%, total 500 mL:
- Parts source = 40
- Parts diluent = 95 - 40 = 55
- Total parts = 40 + 55 = 95
- Source volume = 500 x (40/95) = 210.53 mL
- Water volume = 500 x (55/95) = 289.47 mL

**Important caveat:** This calculation assumes volumes are additive.
In reality, mixing ethanol and water produces a slight volume
contraction (about 3-4% at 50/50). For bench-level herbalism this
is negligible, but pharmaceutical labs use more precise methods.
            """)

    return tab
