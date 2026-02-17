"""Drop/mL Calibration Tool for HerbCalc.

Provides approximate drops-per-milliliter values for different
dropper types and solvents, with confidence ranges and pedagogical
emphasis on the imprecision of drop dosing.
"""

import gradio as gr


# Calibration lookup data: (dropper_type, solvent) -> (drops_per_ml, range_low, range_high)
# Sources: USP guidelines, published dropper calibration studies, and
# bench experience. These are presentation-layer reference values, not
# computed from core/ functions.
_CALIBRATION_DATA: dict[tuple[str, str], tuple[float, float, float]] = {
    # Standard glass dropper (USP-style, vertical delivery)
    ("standard glass", "water"):            (20.0, 18.0, 22.0),
    ("standard glass", "ethanol 40%"):      (28.0, 25.0, 32.0),
    ("standard glass", "ethanol 60%"):      (32.0, 28.0, 36.0),
    ("standard glass", "ethanol 95%"):      (40.0, 35.0, 46.0),
    ("standard glass", "glycerin"):         (15.0, 12.0, 18.0),
    ("standard glass", "tincture"):         (25.0, 20.0, 32.0),
    # Commercial dropper (rubber-bulb, common in tincture bottles)
    ("commercial dropper", "water"):        (20.0, 15.0, 25.0),
    ("commercial dropper", "ethanol 40%"):  (25.0, 20.0, 30.0),
    ("commercial dropper", "ethanol 60%"):  (30.0, 25.0, 35.0),
    ("commercial dropper", "ethanol 95%"):  (38.0, 32.0, 44.0),
    ("commercial dropper", "glycerin"):     (12.0, 10.0, 16.0),
    ("commercial dropper", "tincture"):     (22.0, 18.0, 28.0),
    # Pipette (graduated glass or plastic transfer pipette)
    ("pipette", "water"):                   (20.0, 19.0, 21.0),
    ("pipette", "ethanol 40%"):             (26.0, 24.0, 28.0),
    ("pipette", "ethanol 60%"):             (30.0, 28.0, 33.0),
    ("pipette", "ethanol 95%"):             (38.0, 35.0, 42.0),
    ("pipette", "glycerin"):                (14.0, 12.0, 16.0),
    ("pipette", "tincture"):               (23.0, 20.0, 26.0),
}

_DROPPER_TYPES = ["standard glass", "commercial dropper", "pipette"]
_SOLVENTS = [
    "water",
    "ethanol 40%",
    "ethanol 60%",
    "ethanol 95%",
    "glycerin",
    "tincture",
]


def _compute(
    dropper_type: str,
    solvent: str,
) -> tuple[float, float, float, str]:
    """Look up calibration data for the given dropper/solvent combination.

    Returns:
        Tuple of (drops_per_ml, range_low, range_high, warning_text).
    """
    if not dropper_type or not solvent:
        return (
            0.0, 0.0, 0.0,
            "Please select both a dropper type and a solvent.",
        )

    key = (dropper_type, solvent)
    data = _CALIBRATION_DATA.get(key)

    if data is None:
        return (
            0.0, 0.0, 0.0,
            f"**No calibration data** for '{dropper_type}' with '{solvent}'. "
            "Try a different combination.",
        )

    drops, low, high = data

    warning = (
        "**These values are approximate.** Drop size varies with dropper "
        "angle, squeeze speed, temperature, solvent surface tension, and "
        "individual dropper construction. For precise dosing, calibrate "
        "your own dropper by counting drops to fill a measured 1 mL volume."
    )

    return drops, low, high, warning


def build_tab() -> gr.Tab:
    """Build and return the Drop/mL Calibration Tool tab."""
    with gr.Tab("Drop Calibration") as tab:
        gr.Markdown(
            "## Drop/mL Calibration Tool\n"
            "Look up approximate drops per milliliter for your dropper "
            "type and solvent. Always verify with your own equipment."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input")
                dropper_type = gr.Dropdown(
                    label="Dropper type",
                    choices=_DROPPER_TYPES,
                    value="standard glass",
                )
                solvent = gr.Dropdown(
                    label="Solvent",
                    choices=_SOLVENTS,
                    value="water",
                )
                lookup_btn = gr.Button("Look Up", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                drops_per_ml = gr.Number(
                    label="Approximate drops per mL",
                    interactive=False,
                )
                range_low = gr.Number(
                    label="Range low (drops/mL)",
                    interactive=False,
                )
                range_high = gr.Number(
                    label="Range high (drops/mL)",
                    interactive=False,
                )
                warning_text = gr.Markdown(value="")

        lookup_btn.click(
            fn=_compute,
            inputs=[dropper_type, solvent],
            outputs=[drops_per_ml, range_low, range_high, warning_text],
        )

        with gr.Accordion("Why are drops imprecise?", open=False):
            gr.Markdown("""
A "drop" is not a standardized unit of measure. The volume of a single
drop depends on many factors:

**Physical factors:**
- **Surface tension** of the liquid -- ethanol has lower surface tension
  than water, producing smaller drops (more drops per mL).
- **Viscosity** -- glycerin is thick and forms large drops (fewer per mL).
- **Temperature** -- warmer liquids have lower surface tension.
- **Density** -- heavier liquids form larger drops.

**Equipment factors:**
- **Dropper orifice diameter** -- the single largest variable. A 1 mm
  difference in orifice size can change drop volume by 50%.
- **Dropper angle** -- vertical delivery produces different drops than
  angled delivery.
- **Squeeze speed** -- fast squeezing produces irregular drops.

**The USP (United States Pharmacopeia) nominal value is 20 drops per mL
of water from a standard calibrated dropper.** But real-world conditions
routinely produce 15-25 drops/mL for water and 25-45 drops/mL for
ethanol-based tinctures.

**Best practice:** If a dose matters (and herbal doses do), calibrate
your own dropper with the specific tincture you are dispensing. Count
how many drops from YOUR dropper fill a measured 1 mL. Use that number
for dosing calculations.
            """)

    return tab
