"""Salve/Balm Calculator.

Calculates the amount of beeswax (and optional butter adjustments) needed
to achieve a target consistency from infused oil, ranging from liquid oil
to firm lip balm.

Beeswax ratios are expressed as a percentage of beeswax weight relative to
oil weight. Oil density is assumed ~0.91 g/mL for converting volume inputs
to weight.

Consistency presets:
  - Liquid Oil: 0% beeswax
  - Soft Salve: ~9% beeswax to oil ratio
  - Medium Salve: ~11%
  - Firm Salve: ~17%
  - Lip Balm: ~25%

Butters (shea, cocoa) contribute firmness and allow reducing beeswax.
"""

from dataclasses import dataclass

import gradio as gr


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OIL_DENSITY_G_PER_ML: float = 0.91  # Typical for olive, sweet almond, jojoba

# Beeswax ratio = beeswax weight / oil weight
BEESWAX_RATIOS: dict[str, float] = {
    "Liquid Oil": 0.00,
    "Soft Salve": 0.09,
    "Medium Salve": 0.11,
    "Firm Salve": 0.17,
    "Lip Balm": 0.25,
}

# Butter firmness contribution factors.
# These represent how much each gram of butter "replaces" in beeswax
# firmness. Cocoa butter is firmer than shea at room temperature.
SHEA_BEESWAX_EQUIVALENCE: float = 0.30  # 1g shea ~ 0.30g beeswax in firmness
COCOA_BEESWAX_EQUIVALENCE: float = 0.50  # 1g cocoa ~ 0.50g beeswax in firmness

BEESWAX_DENSITY_G_PER_ML: float = 0.96


# ---------------------------------------------------------------------------
# Structured result
# ---------------------------------------------------------------------------

@dataclass
class SalveResult:
    """Computed salve/balm values."""

    beeswax_g: float
    beeswax_g_before_adjustment: float
    total_yield_ml: float
    oil_weight_g: float
    notes: str


# ---------------------------------------------------------------------------
# Calculation
# ---------------------------------------------------------------------------

def _calculate_salve(
    oil_volume_ml: float,
    consistency: str,
    shea_g: float,
    cocoa_g: float,
) -> SalveResult:
    """Compute beeswax quantity and total yield.

    Args:
        oil_volume_ml: Volume of infused oil in mL.
        consistency: Target consistency preset name.
        shea_g: Grams of shea butter to include (0 if not used).
        cocoa_g: Grams of cocoa butter to include (0 if not used).

    Returns:
        SalveResult with computed values.
    """
    oil_weight_g = oil_volume_ml * OIL_DENSITY_G_PER_ML
    beeswax_ratio = BEESWAX_RATIOS.get(consistency, 0.11)

    # Base beeswax from ratio
    beeswax_base_g = oil_weight_g * beeswax_ratio

    # Adjust down for butters
    shea_offset = shea_g * SHEA_BEESWAX_EQUIVALENCE
    cocoa_offset = cocoa_g * COCOA_BEESWAX_EQUIVALENCE
    beeswax_adjusted_g = max(0.0, beeswax_base_g - shea_offset - cocoa_offset)

    # Total yield: oil + beeswax + butters, converted to volume
    total_weight_g = oil_weight_g + beeswax_adjusted_g + shea_g + cocoa_g
    # Approximate total volume (mixed density is close to oil density)
    beeswax_vol = beeswax_adjusted_g / BEESWAX_DENSITY_G_PER_ML if beeswax_adjusted_g > 0 else 0
    butter_vol = (shea_g + cocoa_g) / 0.92  # Approximate butter density
    total_yield_ml = oil_volume_ml + beeswax_vol + butter_vol

    # Build notes
    notes_parts: list[str] = []

    notes_parts.append(
        f"**Oil:** {oil_volume_ml:.0f} mL ({oil_weight_g:.0f} g at "
        f"{OIL_DENSITY_G_PER_ML} g/mL density)"
    )

    if consistency == "Liquid Oil":
        notes_parts.append(
            "**No beeswax needed.** This is a liquid oil infusion with "
            "no thickening agent."
        )
    else:
        notes_parts.append(
            f"**Target consistency:** {consistency} "
            f"(beeswax ratio: {beeswax_ratio * 100:.0f}% of oil weight)"
        )
        notes_parts.append(
            f"**Base beeswax (before butter adjustment):** "
            f"{beeswax_base_g:.1f} g"
        )

    if shea_g > 0 or cocoa_g > 0:
        adj_parts: list[str] = []
        if shea_g > 0:
            adj_parts.append(
                f"{shea_g:.0f} g shea butter (offsets ~{shea_offset:.1f} g beeswax)"
            )
        if cocoa_g > 0:
            adj_parts.append(
                f"{cocoa_g:.0f} g cocoa butter (offsets ~{cocoa_offset:.1f} g beeswax)"
            )
        notes_parts.append(
            "**Butter adjustments:** " + "; ".join(adj_parts)
        )
        if beeswax_adjusted_g < beeswax_base_g:
            notes_parts.append(
                f"**Adjusted beeswax:** {beeswax_adjusted_g:.1f} g "
                f"(reduced from {beeswax_base_g:.1f} g)"
            )

    notes_parts.append(
        f"\n**Total weight:** {total_weight_g:.0f} g | "
        f"**Estimated total volume:** {total_yield_ml:.0f} mL"
    )

    notes_parts.append(
        "\n---\n\n**Method:**\n"
        "1. Measure infused oil into a double boiler or heat-safe container "
        "in a water bath.\n"
        "2. Add grated or pelletized beeswax"
        + (", shea butter" if shea_g > 0 else "")
        + (", and cocoa butter" if cocoa_g > 0 else "")
        + ".\n"
        "3. Heat gently, stirring occasionally, until everything is fully "
        "melted and combined.\n"
        "4. Remove from heat. Optionally add essential oils at this point "
        "(they evaporate at high temperatures).\n"
        "5. Pour into tins or jars. Let cool undisturbed until solidified.\n"
        "6. **Test consistency:** dip a spoon into the warm mixture and "
        "place it in the freezer for 2 minutes. If it is too soft, add "
        "more beeswax (a little at a time). If too firm, add more oil."
    )

    return SalveResult(
        beeswax_g=round(beeswax_adjusted_g, 1),
        beeswax_g_before_adjustment=round(beeswax_base_g, 1),
        total_yield_ml=round(total_yield_ml, 0),
        oil_weight_g=round(oil_weight_g, 1),
        notes="\n\n".join(notes_parts),
    )


def _compute(
    oil_volume_ml: float,
    consistency: str,
    include_shea: bool,
    shea_amount_g: float,
    include_cocoa: bool,
    cocoa_amount_g: float,
) -> tuple[str, str, str]:
    """Wrapper returning display-ready strings.

    Returns:
        Tuple of (beeswax_g_text, total_yield_text, notes_markdown).
    """
    try:
        oil_volume_ml = float(oil_volume_ml)
    except (TypeError, ValueError):
        err = "Please enter a valid number for oil volume."
        return err, err, err

    if oil_volume_ml <= 0:
        msg = "Oil volume must be greater than zero."
        return msg, msg, msg

    shea_g = 0.0
    cocoa_g = 0.0

    if include_shea:
        try:
            shea_g = max(0.0, float(shea_amount_g))
        except (TypeError, ValueError):
            shea_g = 0.0

    if include_cocoa:
        try:
            cocoa_g = max(0.0, float(cocoa_amount_g))
        except (TypeError, ValueError):
            cocoa_g = 0.0

    try:
        result = _calculate_salve(oil_volume_ml, consistency, shea_g, cocoa_g)
    except Exception as exc:
        err = f"**Calculation error:** {exc}"
        return err, err, err

    if consistency == "Liquid Oil":
        beeswax_text = "0 g (no beeswax for liquid oil)"
    else:
        beeswax_text = f"{result.beeswax_g:.1f} g"

    yield_text = f"{result.total_yield_ml:.0f} mL (approximately)"

    return beeswax_text, yield_text, result.notes


# ---------------------------------------------------------------------------
# Gradio Tab
# ---------------------------------------------------------------------------

def build_tab() -> gr.Tab:
    """Build and return the Salve/Balm Calculator tab."""
    with gr.Tab("Salve / Balm Calculator") as tab:
        gr.Markdown(
            "## Salve & Balm Calculator\n"
            "Calculate beeswax and butter quantities for your desired "
            "salve or balm consistency from infused oil."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Inputs")
                oil_volume_ml = gr.Number(
                    label="Infused oil volume (mL)",
                    value=250,
                    minimum=1,
                )
                consistency = gr.Radio(
                    label="Target consistency",
                    choices=[
                        "Liquid Oil",
                        "Soft Salve",
                        "Medium Salve",
                        "Firm Salve",
                        "Lip Balm",
                    ],
                    value="Medium Salve",
                )

                gr.Markdown("#### Optional butter additions")
                include_shea = gr.Checkbox(
                    label="Include shea butter",
                    value=False,
                )
                shea_amount_g = gr.Number(
                    label="Shea butter amount (grams)",
                    value=0,
                    minimum=0,
                    visible=True,
                )
                include_cocoa = gr.Checkbox(
                    label="Include cocoa butter",
                    value=False,
                )
                cocoa_amount_g = gr.Number(
                    label="Cocoa butter amount (grams)",
                    value=0,
                    minimum=0,
                    visible=True,
                )

                calc_btn = gr.Button("Calculate", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                beeswax_g = gr.Textbox(
                    label="Beeswax needed",
                    interactive=False,
                )
                total_yield = gr.Textbox(
                    label="Estimated total yield",
                    interactive=False,
                )

        notes_md = gr.Markdown(
            value="*Press Calculate to see detailed notes and instructions.*"
        )

        calc_btn.click(
            fn=_compute,
            inputs=[
                oil_volume_ml,
                consistency,
                include_shea,
                shea_amount_g,
                include_cocoa,
                cocoa_amount_g,
            ],
            outputs=[beeswax_g, total_yield, notes_md],
        )

        # Pedagogical accordion
        with gr.Accordion("Adjusting salve consistency", open=False):
            gr.Markdown("""
The consistency of a salve or balm is determined by the **ratio of
beeswax to oil**. More beeswax = firmer product. The relationship is
roughly linear within the practical range.

---

#### Beeswax-to-oil ratios (by weight)

| Consistency | Beeswax % of oil weight | Description |
|-------------|------------------------|-------------|
| Liquid Oil | 0% | No beeswax. Pourable oil infusion. |
| Soft Salve | ~9% | Scoopable, melts on contact with skin. Good for body butters. |
| Medium Salve | ~11% | The "classic" salve. Holds shape but spreads easily. |
| Firm Salve | ~17% | Holds shape well. Good for travel tins, healing salves. |
| Lip Balm | ~25% | Firm enough to push up in a tube. Stays solid in a pocket. |

---

#### How butters affect consistency

**Shea butter** and **cocoa butter** are solid at room temperature and
contribute their own firmness to a salve. When you add them, you can
reduce the beeswax proportionally:

- **Shea butter** is softer (melts at ~32-36 C). Each gram of shea
  offsets roughly 0.3 g of beeswax.
- **Cocoa butter** is firmer (melts at ~34-38 C). Each gram of cocoa
  butter offsets roughly 0.5 g of beeswax.

These are approximations. The exact interaction depends on your specific
oils and the temperature of your environment. Always do a **spoon test**:
dip a spoon in the melted mixture, freeze it for 2 minutes, and check
the consistency before pouring your full batch.

---

#### Oil density

The calculator converts oil volume (mL) to weight (grams) using a
density of **0.91 g/mL**, which is typical for common carrier oils
(olive, sweet almond, jojoba, coconut when liquid). If you are
working with a significantly different oil, adjust accordingly or
measure your oil by weight.

---

#### Beeswax form

Beeswax pellets (pastilles) are strongly recommended over block beeswax
because they melt faster and more evenly. If you have block beeswax,
grate it finely before use.

**White (refined) vs yellow (raw) beeswax:** Both work identically for
consistency. Yellow beeswax has a mild honey scent and golden colour.
White beeswax is deodorized and bleached (usually by filtration, not
chemicals) -- better when you want a neutral-coloured product or when
the beeswax scent would clash with essential oils.
            """)

    return tab
