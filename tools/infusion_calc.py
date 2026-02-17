"""Infusion/Decoction Calculator.

Calculates steep time, expected yield, and concentration for standard
infusions, cold infusions, and decoctions based on herb weight and
water volume.

Preparation parameters are hardcoded based on standard herbalism practice:
  - Standard infusion: 10-15 min steep, ~90% yield
  - Cold infusion: 4-8 hours steep, ~95% yield
  - Decoction: 20-40 min simmer, ~60-75% yield (reduction)
"""

from dataclasses import dataclass

import gradio as gr


# ---------------------------------------------------------------------------
# Preparation parameter constants
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PreparationParams:
    """Parameters for a single preparation mode."""

    mode: str
    steep_time_min: str
    yield_fraction_low: float
    yield_fraction_high: float
    temperature: str
    plant_parts: str
    instructions: str


PREPARATIONS: dict[str, PreparationParams] = {
    "Standard Infusion": PreparationParams(
        mode="Standard Infusion",
        steep_time_min="10 - 15 minutes",
        yield_fraction_low=0.88,
        yield_fraction_high=0.92,
        temperature="Just off the boil (~95-100 C / 200-212 F)",
        plant_parts="Leaves, flowers, and other delicate aerial parts",
        instructions=(
            "1. Bring water to a rolling boil, then remove from heat.\n"
            "2. Place herb material in a heat-safe vessel (teapot, mason jar, "
            "French press).\n"
            "3. Pour hot water over the herb. Cover immediately to retain "
            "volatile oils.\n"
            "4. Steep for **10 to 15 minutes**.\n"
            "5. Strain through a fine mesh strainer or cheesecloth.\n"
            "6. Press or squeeze the marc (spent herb) gently to recover "
            "residual liquid.\n"
            "7. Use or refrigerate promptly. Best consumed within 24 hours."
        ),
    ),
    "Cold Infusion": PreparationParams(
        mode="Cold Infusion",
        steep_time_min="4 - 8 hours (overnight)",
        yield_fraction_low=0.93,
        yield_fraction_high=0.97,
        temperature="Room temperature or refrigerated",
        plant_parts="Mucilaginous herbs (marshmallow root, slippery elm), "
        "delicate aromatics, or any herb where heat would damage "
        "desired constituents",
        instructions=(
            "1. Place herb material in a glass jar.\n"
            "2. Pour **room-temperature or cold water** over the herb.\n"
            "3. Stir gently, cover, and let sit for **4 to 8 hours** "
            "(overnight is convenient).\n"
            "4. Strain through a fine mesh strainer or cheesecloth.\n"
            "5. Press or squeeze the marc gently.\n"
            "6. Refrigerate and use within 24 - 48 hours."
        ),
    ),
    "Decoction": PreparationParams(
        mode="Decoction",
        steep_time_min="20 - 40 minutes (simmering)",
        yield_fraction_low=0.60,
        yield_fraction_high=0.75,
        temperature="Gentle simmer (~85-95 C / 185-200 F)",
        plant_parts="Roots, bark, seeds, dried berries, and other tough or "
        "woody plant parts",
        instructions=(
            "1. Place herb material and **cold** water together in a "
            "saucepan. Starting cold allows tougher material to begin "
            "softening before heat is applied.\n"
            "2. Bring slowly to a **gentle simmer** (small bubbles, not a "
            "rolling boil).\n"
            "3. **Partially cover** the pot and maintain the simmer for "
            "**20 to 40 minutes**.\n"
            "4. The liquid will reduce substantially -- this is expected "
            "and desirable.\n"
            "5. Remove from heat. Strain through a fine mesh strainer.\n"
            "6. Press the marc firmly -- decoction marc retains significant "
            "liquid.\n"
            "7. Use promptly, or refrigerate and use within 48 hours.\n\n"
            "*Tip:* Some practitioners add back water to restore the "
            "original volume after straining. This is fine for drinking "
            "teas but lowers concentration for syrups or other downstream "
            "preparations."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Calculation
# ---------------------------------------------------------------------------

def _calculate(
    mode: str,
    herb_weight_g: float,
    water_volume_ml: float,
) -> tuple[str, str, str, str]:
    """Compute infusion/decoction outputs.

    Args:
        mode: One of "Standard Infusion", "Cold Infusion", "Decoction".
        herb_weight_g: Weight of dried herb in grams.
        water_volume_ml: Starting water volume in millilitres.

    Returns:
        Tuple of (steep_time, expected_yield_ml, concentration_text,
                  process_instructions_markdown).
    """
    try:
        herb_weight_g = float(herb_weight_g)
        water_volume_ml = float(water_volume_ml)
    except (TypeError, ValueError):
        error = "Please enter valid numeric values for herb weight and water volume."
        return error, error, error, error

    if herb_weight_g <= 0:
        msg = "Herb weight must be greater than zero."
        return msg, msg, msg, msg

    if water_volume_ml <= 0:
        msg = "Water volume must be greater than zero."
        return msg, msg, msg, msg

    params = PREPARATIONS.get(mode)
    if params is None:
        msg = f"Unknown preparation mode: {mode}"
        return msg, msg, msg, msg

    # Expected yield as a range
    yield_low = water_volume_ml * params.yield_fraction_low
    yield_high = water_volume_ml * params.yield_fraction_high
    yield_avg = (yield_low + yield_high) / 2

    # Concentration: grams of herb per mL of finished liquid (using avg yield)
    conc_g_per_ml = herb_weight_g / yield_avg if yield_avg > 0 else 0
    # Also express as a ratio (1:X)
    ratio_x = yield_avg / herb_weight_g if herb_weight_g > 0 else 0

    # Format outputs
    steep_time = params.steep_time_min

    expected_yield = (
        f"{yield_low:.0f} - {yield_high:.0f} mL "
        f"(from {water_volume_ml:.0f} mL starting water)"
    )

    concentration_text = (
        f"{conc_g_per_ml:.3f} g/mL "
        f"(approximately 1:{ratio_x:.1f} herb-to-liquid ratio)\n\n"
        f"That is {herb_weight_g:.1f} g herb extracted into "
        f"~{yield_avg:.0f} mL of finished liquid."
    )

    # Process instructions with contextual info
    instructions_md = (
        f"### {params.mode}\n\n"
        f"**Temperature:** {params.temperature}\n\n"
        f"**Best for:** {params.plant_parts}\n\n"
        f"**Steep / simmer time:** {params.steep_time_min}\n\n"
        f"---\n\n"
        f"#### Step-by-step\n\n"
        f"{params.instructions}\n\n"
        f"---\n\n"
        f"**Your batch:** {herb_weight_g:.1f} g herb + "
        f"{water_volume_ml:.0f} mL water "
        f"-> expect **{yield_low:.0f} - {yield_high:.0f} mL** finished "
        f"liquid."
    )

    return steep_time, expected_yield, concentration_text, instructions_md


# ---------------------------------------------------------------------------
# Gradio Tab
# ---------------------------------------------------------------------------

def build_tab() -> gr.Tab:
    """Build and return the Infusion/Decoction Calculator tab."""
    with gr.Tab("Infusion / Decoction") as tab:
        gr.Markdown(
            "## Infusion & Decoction Calculator\n"
            "Calculate steep times, expected yield, and concentration for "
            "water-based herbal preparations."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Inputs")
                mode = gr.Radio(
                    label="Preparation mode",
                    choices=[
                        "Standard Infusion",
                        "Cold Infusion",
                        "Decoction",
                    ],
                    value="Standard Infusion",
                )
                herb_weight_g = gr.Number(
                    label="Herb weight (grams)",
                    value=30,
                    minimum=0.1,
                )
                water_volume_ml = gr.Number(
                    label="Water volume (mL)",
                    value=500,
                    minimum=1,
                )
                calc_btn = gr.Button("Calculate", variant="primary")

            with gr.Column():
                gr.Markdown("### Results")
                steep_time = gr.Textbox(
                    label="Steep / simmer time",
                    interactive=False,
                )
                expected_yield = gr.Textbox(
                    label="Expected yield (mL)",
                    interactive=False,
                )
                concentration = gr.Textbox(
                    label="Concentration",
                    interactive=False,
                )

        process_instructions = gr.Markdown(
            label="Process instructions",
            value="*Press Calculate to see step-by-step instructions.*",
        )

        calc_btn.click(
            fn=_calculate,
            inputs=[mode, herb_weight_g, water_volume_ml],
            outputs=[
                steep_time,
                expected_yield,
                concentration,
                process_instructions,
            ],
        )

        # Pedagogical accordion
        with gr.Accordion(
            "Infusion vs Decoction -- when to use which", open=False
        ):
            gr.Markdown("""
**Infusion** and **decoction** are both water extractions, but they suit
different plant materials and extract different constituents.

---

#### Standard (hot) infusion

- **Best for:** Leaves, flowers, and other delicate aerial parts.
- **Why:** The volatile oils, flavonoids, and other heat-sensitive
  compounds in soft tissue extract readily in hot water within minutes.
  Prolonged boiling would drive off volatiles (think of the aroma
  escaping a pot of chamomile left boiling).
- **Method:** Pour just-boiled water over the herb and **cover** to
  trap steam and volatile oils. Steep 10-15 minutes, then strain.
- **Yield:** Roughly 88-92% of your starting water volume -- the herb
  absorbs some liquid.

#### Cold infusion

- **Best for:** Mucilaginous herbs (marshmallow root, slippery elm,
  linden) and situations where heat would damage desired constituents.
- **Why:** Mucilage dissolves well in cold or room-temperature water.
  Heat can actually break down mucilage or extract unwanted tannins
  from the same plant material.
- **Method:** Combine herb and room-temperature water, cover, and let
  sit 4-8 hours (overnight). Strain.
- **Yield:** Roughly 93-97% -- less absorption because the herb is not
  swelling from heat.

#### Decoction

- **Best for:** Roots, bark, seeds, dried berries -- tough, dense, or
  woody plant material.
- **Why:** The desired compounds (alkaloids, bitter principles, mineral
  salts) are locked in rigid cell walls that need sustained heat to
  break down. A quick steep will not extract them adequately.
- **Method:** Start with cold water and herb together, bring to a
  simmer, and maintain for 20-40 minutes. The liquid reduces
  substantially.
- **Yield:** Roughly 60-75% of starting volume -- significant water
  evaporates during simmering. This is expected and results in a more
  concentrated extract.

---

**Rule of thumb:** If the plant part is soft and aromatic, infuse.
If it is hard and woody, decoct. When in doubt, check the monograph
for the specific herb.

**Combination approach:** Some formulas call for decocting the roots
and bark first, then removing from heat and adding the leaves/flowers
to infuse in the hot decoction liquid for 10 minutes. This extracts
both types of material without overheating the delicate parts.
            """)

    return tab
