"""HerbCalc: Tools for Herbalists.

Main Gradio application — assembles all tool tabs and launches the app.
CC BY 4.0 International — HerbCalc Project.
"""

import gradio as gr

from tools import (
    menstruum_calc,
    unit_converter,
    pearson_square,
    percentage_expr,
    drop_calibration,
    apothecary,
    pharmacy_shorthand,
    formula_builder,
    dose_calc,
    dry_extract,
    monograph_viewer,
    solvent_affinity,
    infusion_calc,
    syrup_calc,
    salve_calc,
    interaction_check,
    batch_log,
    reverse_lookup,
)

with gr.Blocks(
    title="HerbCalc: Tools for Herbalists",
    theme=gr.themes.Soft(),
) as app:
    gr.Markdown(
        "# HerbCalc: Tools for Herbalists\n"
        "*Open-source calculators, converters, and reference tools "
        "for herbal formulation.*"
    )

    with gr.Tabs():
        with gr.Tab("Unit Translation"):
            with gr.Tabs():
                unit_converter.build_tab()
                apothecary.build_tab()
                pharmacy_shorthand.build_tab()
                drop_calibration.build_tab()
                percentage_expr.build_tab()

        with gr.Tab("Solvent Systems"):
            with gr.Tabs():
                menstruum_calc.build_tab()
                pearson_square.build_tab()
                solvent_affinity.build_tab()

        with gr.Tab("Formulation"):
            with gr.Tabs():
                formula_builder.build_tab()
                dose_calc.build_tab()
                dry_extract.build_tab()

        with gr.Tab("Preparation"):
            with gr.Tabs():
                infusion_calc.build_tab()
                syrup_calc.build_tab()
                salve_calc.build_tab()

        with gr.Tab("Quality & Safety"):
            with gr.Tabs():
                interaction_check.build_tab()
                batch_log.build_tab()

        with gr.Tab("Reference"):
            with gr.Tabs():
                monograph_viewer.build_tab()
                reverse_lookup.build_tab()

    gr.Markdown(
        "*CC BY 4.0 International — "
        "[HerbCalc Project](https://github.com/potlatchdiscordian/herbcalc)*"
    )

if __name__ == "__main__":
    app.launch()
