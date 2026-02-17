"""Reverse Lookup -- "What Can I Make?" tool.

Given the solvents and equipment a user has on hand, this tool filters
the available preparation types and shows what is feasible. Uses
PREPARATION_TYPES from the shared data layer when populated, and falls
back to a built-in reference table when the data file is empty.
"""

import gradio as gr

try:
    from core.data_loader import PREPARATION_TYPES as _LOADED_PREP_TYPES
except Exception:
    _LOADED_PREP_TYPES: list | dict = []


# ---------------------------------------------------------------------------
# Built-in fallback preparation data
# ---------------------------------------------------------------------------
# Used when data/formulation/preparation_types.json is empty or missing.
# Each entry defines required solvents, required equipment, and a
# description for the user.

_BUILTIN_PREPARATIONS: list[dict] = [
    {
        "name": "Tincture (hydroethanolic)",
        "description": (
            "An alcohol-and-water extraction of dried or fresh herbs. "
            "The most common and versatile herbal preparation. Typical "
            "maceration time: 4-6 weeks."
        ),
        "required_solvents": ["Ethanol/alcohol", "Water"],
        "required_equipment": ["Glass jars", "Scale", "Strainer"],
        "optional_equipment": ["Graduated cylinder", "Press", "Bottles"],
    },
    {
        "name": "Glycerite",
        "description": (
            "A glycerin-based extraction. Alcohol-free, sweet taste, "
            "good for children and those avoiding alcohol. Lower "
            "extraction power than alcohol for most constituents."
        ),
        "required_solvents": ["Glycerin", "Water"],
        "required_equipment": ["Glass jars", "Scale", "Strainer"],
        "optional_equipment": ["Graduated cylinder", "Bottles"],
    },
    {
        "name": "Acetum (herbal vinegar)",
        "description": (
            "A vinegar-based extraction. Good for mineral-rich herbs "
            "and culinary applications. Apple cider vinegar is the "
            "traditional choice."
        ),
        "required_solvents": ["Vinegar"],
        "required_equipment": ["Glass jars", "Strainer"],
        "optional_equipment": ["Scale", "Bottles"],
    },
    {
        "name": "Standard infusion (tea)",
        "description": (
            "A hot water extraction of leaves, flowers, and other "
            "delicate plant parts. Steeped 10-15 minutes. The simplest "
            "herbal preparation."
        ),
        "required_solvents": ["Water"],
        "required_equipment": ["Stove/heat source"],
        "optional_equipment": ["Scale", "Strainer"],
    },
    {
        "name": "Cold infusion",
        "description": (
            "A room-temperature or cold water extraction. Ideal for "
            "mucilaginous herbs (marshmallow, slippery elm) and "
            "heat-sensitive constituents. Steep 4-8 hours."
        ),
        "required_solvents": ["Water"],
        "required_equipment": ["Glass jars"],
        "optional_equipment": ["Scale", "Strainer"],
    },
    {
        "name": "Decoction",
        "description": (
            "A simmered water extraction of roots, bark, seeds, and "
            "other tough plant material. 20-40 minutes of gentle "
            "simmering. Liquid reduces significantly."
        ),
        "required_solvents": ["Water"],
        "required_equipment": ["Stove/heat source"],
        "optional_equipment": ["Scale", "Strainer"],
    },
    {
        "name": "Syrup",
        "description": (
            "A sweetened herbal decoction or infusion. Sugar (or honey) "
            "acts as both sweetener and preservative. Excellent for "
            "cough remedies and children's preparations."
        ),
        "required_solvents": ["Water"],
        "required_equipment": ["Stove/heat source", "Scale"],
        "optional_equipment": ["Graduated cylinder", "Bottles", "Strainer"],
    },
    {
        "name": "Oil infusion (cold method)",
        "description": (
            "Herb steeped in carrier oil at room temperature for 4-6 "
            "weeks. Used directly as a topical oil or as a base for "
            "salves and balms. Best for dried herbs (fresh herbs risk "
            "introducing water and causing spoilage)."
        ),
        "required_solvents": ["Oil"],
        "required_equipment": ["Glass jars", "Strainer"],
        "optional_equipment": ["Scale"],
    },
    {
        "name": "Oil infusion (warm method)",
        "description": (
            "Herb infused in carrier oil using gentle heat (double "
            "boiler or low oven, 2-4 hours). Faster than the cold "
            "method but requires temperature monitoring to avoid "
            "overheating."
        ),
        "required_solvents": ["Oil"],
        "required_equipment": ["Double boiler", "Strainer"],
        "optional_equipment": ["Scale", "Glass jars"],
    },
    {
        "name": "Salve / balm",
        "description": (
            "Infused oil thickened with beeswax to a semi-solid "
            "consistency. Requires an already-prepared infused oil "
            "as the starting point."
        ),
        "required_solvents": ["Oil"],
        "required_equipment": ["Double boiler", "Scale"],
        "optional_equipment": ["Glass jars"],
    },
    {
        "name": "Compress / fomentation",
        "description": (
            "A cloth soaked in hot herbal infusion or decoction and "
            "applied topically. No special equipment beyond a towel "
            "or cloth and hot water."
        ),
        "required_solvents": ["Water"],
        "required_equipment": ["Stove/heat source"],
        "optional_equipment": [],
    },
    {
        "name": "Poultice",
        "description": (
            "Fresh or moistened dried herb applied directly to the skin, "
            "often held in place with cloth. The simplest topical "
            "application -- requires only the herb and water."
        ),
        "required_solvents": ["Water"],
        "required_equipment": [],
        "optional_equipment": [],
    },
    {
        "name": "Elixir",
        "description": (
            "A tincture sweetened with honey or syrup. Combines the "
            "extraction power of alcohol with the palatability of a "
            "syrup. Requires both alcohol and a sweetener."
        ),
        "required_solvents": ["Ethanol/alcohol", "Water"],
        "required_equipment": ["Glass jars", "Scale", "Strainer"],
        "optional_equipment": ["Graduated cylinder", "Bottles"],
    },
    {
        "name": "Oxymel",
        "description": (
            "A traditional combination of honey and vinegar infused "
            "with herbs. The name comes from Latin: oxy (acid) + mel "
            "(honey). Good for respiratory herbs."
        ),
        "required_solvents": ["Vinegar"],
        "required_equipment": ["Glass jars", "Strainer"],
        "optional_equipment": ["Scale"],
    },
]


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _get_preparations() -> list[dict]:
    """Return the preparation types list, using loaded data or fallback."""
    if _LOADED_PREP_TYPES and isinstance(_LOADED_PREP_TYPES, list) and len(_LOADED_PREP_TYPES) > 0:
        return _LOADED_PREP_TYPES
    if isinstance(_LOADED_PREP_TYPES, dict) and len(_LOADED_PREP_TYPES) > 0:
        # Convert dict format to list format
        result = []
        for name, data in _LOADED_PREP_TYPES.items():
            entry = dict(data) if isinstance(data, dict) else {"description": str(data)}
            entry.setdefault("name", name)
            result.append(entry)
        return result
    return _BUILTIN_PREPARATIONS


def _filter_preparations(
    available_solvents: list[str] | None,
    available_equipment: list[str] | None,
) -> str:
    """Filter preparations by available resources and return Markdown.

    Args:
        available_solvents: List of solvent names the user has.
        available_equipment: List of equipment names the user has.

    Returns:
        Formatted Markdown string with feasible preparations.
    """
    if not available_solvents:
        available_solvents = []
    if not available_equipment:
        available_equipment = []

    solvents_set = set(available_solvents)
    equipment_set = set(available_equipment)

    preparations = _get_preparations()

    feasible: list[dict] = []
    partial: list[tuple[dict, list[str], list[str]]] = []  # (prep, missing_solvents, missing_equipment)

    for prep in preparations:
        req_solvents = set(prep.get("required_solvents", []))
        req_equipment = set(prep.get("required_equipment", []))

        missing_solvents = req_solvents - solvents_set
        missing_equipment = req_equipment - equipment_set

        if not missing_solvents and not missing_equipment:
            feasible.append(prep)
        elif not missing_solvents and missing_equipment:
            # Has the solvents but missing some equipment
            partial.append((prep, [], sorted(missing_equipment)))
        elif len(missing_solvents) <= 1 and not missing_equipment:
            # Close -- missing only one solvent
            partial.append((prep, sorted(missing_solvents), []))

    # Build output
    sections: list[str] = []

    if not available_solvents and not available_equipment:
        sections.append(
            "Select your available solvents and equipment above, then "
            "press **Find Preparations** to see what you can make."
        )
        return "\n\n".join(sections)

    sections.append(
        f"**Your supplies:** {', '.join(available_solvents) if available_solvents else '(none)'} "
        f"| **Equipment:** {', '.join(available_equipment) if available_equipment else '(none)'}"
    )

    if feasible:
        sections.append(f"## You can make ({len(feasible)} preparations)\n")
        for prep in feasible:
            name = prep.get("name", "Unknown")
            desc = prep.get("description", "")
            opt_equip = prep.get("optional_equipment", [])
            opt_text = ""
            if opt_equip:
                missing_opt = set(opt_equip) - equipment_set
                if missing_opt:
                    opt_text = (
                        f"\n  *Optional (you do not have):* "
                        f"{', '.join(sorted(missing_opt))}"
                    )
            sections.append(f"### {name}\n{desc}{opt_text}\n")
    else:
        sections.append(
            "## No fully matching preparations found\n\n"
            "With your current supplies, no preparation type has all "
            "requirements met. See the **Almost feasible** section "
            "below for preparations that are close."
        )

    if partial:
        sections.append(f"---\n## Almost feasible ({len(partial)} preparations)\n")
        sections.append(
            "*These preparations are close to your available supplies. "
            "You would need to acquire the listed items.*\n"
        )
        for prep, miss_sol, miss_eq in partial:
            name = prep.get("name", "Unknown")
            desc = prep.get("description", "")
            missing_parts: list[str] = []
            if miss_sol:
                missing_parts.append(f"Solvents needed: {', '.join(miss_sol)}")
            if miss_eq:
                missing_parts.append(f"Equipment needed: {', '.join(miss_eq)}")
            missing_text = " | ".join(missing_parts)
            sections.append(f"### {name}\n{desc}\n*Missing: {missing_text}*\n")

    if not feasible and not partial:
        sections.append(
            "\n---\n\nNo preparations matched your available supplies. "
            "Try selecting additional solvents or equipment."
        )

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Gradio Tab
# ---------------------------------------------------------------------------

# Solvent and equipment choices
_SOLVENT_CHOICES: list[str] = [
    "Ethanol/alcohol",
    "Water",
    "Glycerin",
    "Vinegar",
    "Oil",
]

_EQUIPMENT_CHOICES: list[str] = [
    "Glass jars",
    "Scale",
    "Graduated cylinder",
    "Strainer",
    "Press",
    "Stove/heat source",
    "Double boiler",
    "Bottles",
]


def build_tab() -> gr.Tab:
    """Build and return the Reverse Lookup tab."""
    with gr.Tab("What Can I Make?") as tab:
        gr.Markdown(
            "## What Can I Make?\n"
            "Select the solvents and equipment you have on hand, and "
            "this tool will show you which herbal preparations are "
            "feasible with your current supplies."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### What do you have?")
                available_solvents = gr.CheckboxGroup(
                    label="Available solvents",
                    choices=_SOLVENT_CHOICES,
                    value=["Water"],
                )
                available_equipment = gr.CheckboxGroup(
                    label="Available equipment",
                    choices=_EQUIPMENT_CHOICES,
                    value=["Glass jars", "Stove/heat source"],
                )
                find_btn = gr.Button(
                    "Find Preparations", variant="primary"
                )

            with gr.Column():
                gr.Markdown("### Feasible preparations")
                results_md = gr.Markdown(
                    value=(
                        "Select your supplies and press **Find "
                        "Preparations** to see results."
                    )
                )

        find_btn.click(
            fn=_filter_preparations,
            inputs=[available_solvents, available_equipment],
            outputs=[results_md],
        )

        # Pedagogical accordion
        with gr.Accordion(
            "Matching preparations to your supplies", open=False
        ):
            gr.Markdown("""
Not every herbal preparation requires expensive equipment or exotic
solvents. This tool helps you work with what you have -- and shows
you what would become possible with a small addition to your toolkit.

---

#### Solvents -- what each one extracts

| Solvent | Extracts well | Notes |
|---------|--------------|-------|
| **Water** | Mucilage, some tannins, minerals, water-soluble vitamins, some alkaloids | The universal solvent. Every herbalist has it. Limited for resins, essential oils, and many alkaloids. |
| **Ethanol (alcohol)** | Alkaloids, glycosides, essential oils, resins, tannins, some polysaccharides | The most versatile extraction solvent. Different alcohol percentages target different constituents. |
| **Glycerin** | Some glycosides, tannins, mucilage | Weaker than alcohol for most constituents. Alcohol-free, sweet taste. Good for children. |
| **Vinegar** | Alkaloids, minerals, some glycosides | Acetic acid is a decent solvent for minerals. Traditional in oxymels and herbal vinegars. |
| **Oil** | Essential oils, fat-soluble vitamins, some alkaloids, carotenoids | Only for topical preparations (salves, balms, massage oils). Not suitable for internal extracts of most herbs. |

#### Equipment -- what you really need

The **minimum viable toolkit** for most herbal preparations:

1. **Glass jars** (mason jars work perfectly) -- for maceration
2. **A kitchen scale** (digital, reads to 1g) -- for weighing herbs
3. **A strainer** (fine mesh or cheesecloth) -- for pressing marc
4. **A stove or heat source** -- for decoctions and syrups

With just these four items plus water, you can make infusions,
decoctions, syrups, compresses, and poultices.

**Adding alcohol** opens up tinctures (the most potent and shelf-stable
preparations) and elixirs.

**Adding a double boiler** (or a makeshift one: a heat-safe bowl over
a pot of simmering water) opens up oil infusions and salves.

A **graduated cylinder** or measuring cup improves precision but is not
strictly required for most preparations -- you can measure liquids by
weight on your scale (1 mL of water = 1 g).

A **press** (tincture press or potato ricer) extracts significantly
more liquid from the marc than hand-squeezing, improving yield by
10-20%.

---

#### Start simple, build up

If you are just beginning, start with water-based preparations
(infusions, decoctions) and work your way up to alcohol extractions
and topical preparations as you acquire supplies and confidence.
            """)

    return tab
