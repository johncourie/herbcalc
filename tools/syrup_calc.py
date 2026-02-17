"""Syrup Calculator.

Calculates sugar quantities, total yield, and shelf stability for
herbal syrups in Simple (1:1) and Rich (2:1) modes, with support
for both sucrose and honey.

Calculation notes:
  - Simple 1:1 syrup: equal parts sugar to liquid by weight.
  - Rich 2:1 syrup: 2 parts sugar to 1 part liquid by weight.
  - Honey density: ~1.42 g/mL, already ~80% sugar -- adjusted so the
    total sugar-to-water ratio matches the target syrup type.
  - Total yield approximated as liquid volume + sugar volume contribution.
"""

from dataclasses import dataclass

import gradio as gr


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Sucrose bulk density is irrelevant here; we work by weight.
# What matters for yield estimation is the volume that dissolved sugar adds.
# Dissolved sucrose adds roughly 0.63 mL per gram at room temperature.
SUCROSE_VOLUME_PER_GRAM_ML: float = 0.63

# Honey
HONEY_DENSITY_G_PER_ML: float = 1.42
HONEY_SUGAR_FRACTION: float = 0.80  # ~80% sugars, ~17% water, rest minor


# ---------------------------------------------------------------------------
# Structured result
# ---------------------------------------------------------------------------

@dataclass
class SyrupResult:
    """Holds computed syrup values."""

    sugar_quantity_g: float
    sugar_quantity_description: str
    total_yield_ml: float
    shelf_stability: str
    notes: str


# ---------------------------------------------------------------------------
# Calculation
# ---------------------------------------------------------------------------

def _calculate_syrup(
    mode: str,
    decoction_volume_ml: float,
    sugar_type: str,
) -> SyrupResult:
    """Compute syrup quantities.

    Args:
        mode: "Simple 1:1" or "Rich 2:1".
        decoction_volume_ml: Volume of herbal decoction/infusion in mL.
        sugar_type: "Sucrose" or "Honey".

    Returns:
        SyrupResult with all computed values.
    """
    # Water weighs ~1 g/mL -- decoctions are close enough to water density.
    liquid_weight_g = decoction_volume_ml * 1.0

    if mode == "Simple 1:1":
        target_sugar_g = liquid_weight_g * 1.0  # 1:1 by weight
    else:  # Rich 2:1
        target_sugar_g = liquid_weight_g * 2.0  # 2:1 by weight

    if sugar_type == "Sucrose":
        sugar_g = target_sugar_g
        sugar_volume_ml = sugar_g * SUCROSE_VOLUME_PER_GRAM_ML
        total_yield_ml = decoction_volume_ml + sugar_volume_ml

        description = (
            f"{sugar_g:.0f} g of granulated sugar "
            f"(approximately {sugar_g / 200:.1f} cups / "
            f"{sugar_g / 12.5:.0f} tablespoons)"
        )

        if mode == "Simple 1:1":
            shelf = (
                "**~1 month refrigerated.** Simple syrup has a lower sugar "
                "concentration that does not fully inhibit microbial growth. "
                "Always refrigerate and watch for cloudiness, off-odors, or "
                "fermentation bubbles. Adding 10-20% alcohol (by volume) as "
                "a preservative can extend shelf life to 3-6 months."
            )
        else:
            shelf = (
                "**~6 months refrigerated.** The high sugar concentration "
                "in a rich syrup acts as a preservative by reducing water "
                "activity. Refrigeration is still recommended. Contamination "
                "from unclean utensils remains the primary spoilage risk."
            )

        notes = (
            f"**Method:** Gently heat the decoction ({decoction_volume_ml:.0f} mL) "
            f"until warm (not boiling). Gradually stir in {sugar_g:.0f} g sugar "
            f"until fully dissolved. Avoid boiling, which can caramelize the "
            f"sugar and degrade herbal constituents.\n\n"
            f"**Yield:** approximately {total_yield_ml:.0f} mL of finished syrup."
        )

    else:  # Honey
        # Honey is ~80% sugar. To reach the same sugar ratio as a sucrose
        # syrup we need: honey_weight = target_sugar_g / HONEY_SUGAR_FRACTION.
        # However, honey also contributes ~17% water, which shifts the ratio.
        # For practical herbal syrups, the standard approach is to substitute
        # honey by weight at the same ratio (1:1 or 2:1 honey-to-liquid).
        # We note the effective sugar content for accuracy.
        honey_weight_g = target_sugar_g  # Same weight ratio as sucrose version
        honey_volume_ml = honey_weight_g / HONEY_DENSITY_G_PER_ML
        actual_sugar_g = honey_weight_g * HONEY_SUGAR_FRACTION
        honey_water_g = honey_weight_g * 0.17
        total_yield_ml = decoction_volume_ml + honey_volume_ml

        description = (
            f"{honey_weight_g:.0f} g of honey "
            f"(approximately {honey_volume_ml:.0f} mL / "
            f"{honey_volume_ml / 15:.1f} tablespoons)\n\n"
            f"*Note:* This honey contributes {actual_sugar_g:.0f} g of actual "
            f"sugars and {honey_water_g:.0f} g of additional water. The "
            f"effective sugar concentration is lower than a sucrose syrup "
            f"at the same weight ratio."
        )

        sugar_g = honey_weight_g

        if mode == "Simple 1:1":
            shelf = (
                "**~2-3 months refrigerated.** Honey has natural "
                "antimicrobial properties (low water activity, hydrogen "
                "peroxide production, low pH) that modestly extend shelf "
                "life beyond plain sucrose simple syrup. However, dilution "
                "with the herbal liquid reduces these effects. Refrigerate."
            )
        else:
            shelf = (
                "**~3-6 months refrigerated.** The high honey content "
                "provides both preservative sugar concentration and honey's "
                "inherent antimicrobial compounds. Still refrigerate and "
                "use clean utensils."
            )

        notes = (
            f"**Method:** Warm the decoction ({decoction_volume_ml:.0f} mL) gently. "
            f"**Do not boil** -- excessive heat destroys honey's beneficial "
            f"enzymes and antimicrobial compounds. Stir in {honey_weight_g:.0f} g "
            f"({honey_volume_ml:.0f} mL) of honey until fully incorporated.\n\n"
            f"**Important:** Never give honey-based preparations to children "
            f"under 1 year of age (botulism risk).\n\n"
            f"**Yield:** approximately {total_yield_ml:.0f} mL of finished syrup."
        )

    return SyrupResult(
        sugar_quantity_g=round(sugar_g, 1),
        sugar_quantity_description=description,
        total_yield_ml=round(total_yield_ml, 0),
        shelf_stability=shelf,
        notes=notes,
    )


def _compute(
    mode: str,
    decoction_volume_ml: float,
    sugar_type: str,
) -> tuple[str, str, str, str]:
    """Wrapper that returns display-ready strings.

    Returns:
        Tuple of (sugar_quantity, total_yield, shelf_stability, notes_md).
    """
    try:
        decoction_volume_ml = float(decoction_volume_ml)
    except (TypeError, ValueError):
        err = "Please enter a valid number for decoction volume."
        return err, err, err, err

    if decoction_volume_ml <= 0:
        msg = "Decoction volume must be greater than zero."
        return msg, msg, msg, msg

    try:
        result = _calculate_syrup(mode, decoction_volume_ml, sugar_type)
    except Exception as exc:
        err = f"**Calculation error:** {exc}"
        return err, err, err, err

    sugar_text = result.sugar_quantity_description
    yield_text = f"{result.total_yield_ml:.0f} mL (approximate)"
    shelf_text = result.shelf_stability
    notes_md = result.notes

    return sugar_text, yield_text, shelf_text, notes_md


# ---------------------------------------------------------------------------
# Gradio Tab
# ---------------------------------------------------------------------------

def build_tab() -> gr.Tab:
    """Build and return the Syrup Calculator tab."""
    with gr.Tab("Syrup Calculator") as tab:
        gr.Markdown(
            "## Herbal Syrup Calculator\n"
            "Calculate sugar quantities and yields for herbal syrups "
            "from your decoction or strong infusion."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Inputs")
                mode = gr.Radio(
                    label="Syrup type",
                    choices=["Simple 1:1", "Rich 2:1"],
                    value="Simple 1:1",
                )
                decoction_volume_ml = gr.Number(
                    label="Decoction / infusion volume (mL)",
                    value=500,
                    minimum=1,
                )
                sugar_type = gr.Radio(
                    label="Sweetener",
                    choices=["Sucrose", "Honey"],
                    value="Sucrose",
                )
                calc_btn = gr.Button("Calculate", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                sugar_quantity = gr.Textbox(
                    label="Sweetener quantity",
                    interactive=False,
                    lines=3,
                )
                total_yield = gr.Textbox(
                    label="Total yield",
                    interactive=False,
                )
                shelf_stability = gr.Markdown(
                    label="Shelf stability",
                    value="",
                )

        notes_md = gr.Markdown(
            value="*Press Calculate to see preparation instructions.*"
        )

        calc_btn.click(
            fn=_compute,
            inputs=[mode, decoction_volume_ml, sugar_type],
            outputs=[sugar_quantity, total_yield, shelf_stability, notes_md],
        )

        # Pedagogical accordion
        with gr.Accordion(
            "Simple vs Rich syrup -- shelf life and sweetness", open=False
        ):
            gr.Markdown("""
**Herbal syrups** are concentrated sugar solutions infused with herbal
decoctions or strong infusions. The sugar serves two purposes: it makes
the medicine palatable (especially for children and for bitter herbs),
and it acts as a **preservative** by lowering water activity.

---

#### Simple syrup (1:1)

- **Ratio:** 1 part sugar to 1 part liquid, by weight.
- **Sweetness:** Moderately sweet. The herbal flavour is still prominent.
- **Shelf life:** About 1 month refrigerated. The sugar concentration is
  not high enough to fully suppress microbial growth.
- **Best for:** Syrups that will be used quickly, or when you want a
  less sweet preparation.

#### Rich syrup (2:1)

- **Ratio:** 2 parts sugar to 1 part liquid, by weight.
- **Sweetness:** Very sweet. Can mask even strongly bitter herbs.
- **Shelf life:** About 6 months refrigerated. The high sugar concentration
  dramatically lowers water activity, inhibiting bacteria and mould.
- **Best for:** Long-term storage, cough syrups, elderberry syrup for
  cold season, and any preparation where you need months of shelf life.

---

#### Why not just add more sugar for longer shelf life?

Beyond the 2:1 ratio, sugar will begin to crystallize out of solution
as the liquid cools. The 2:1 rich syrup is near the practical
saturation limit at room temperature.

#### Honey as a sweetener

Honey brings its own antimicrobial properties (hydrogen peroxide, low
pH, methylglyoxal in Manuka honey) and a more complex flavour profile.
However, honey is only ~80% sugar and ~17% water, so a 1:1 honey
syrup has a lower effective sugar concentration than a 1:1 sucrose
syrup. Honey syrups generally fall between simple and rich syrups in
shelf stability.

**Never give honey-based preparations to children under 1 year old**
due to the risk of infant botulism.

#### Alcohol as preservative

Adding 10-20% alcohol (by volume) to a finished syrup can extend its
shelf life to 6-12 months. Brandy is the traditional choice because
its flavour complements many herbal syrups. Add it after the syrup
has cooled to preserve the alcohol content.
            """)

    return tab
