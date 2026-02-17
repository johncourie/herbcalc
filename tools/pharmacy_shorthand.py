"""Rx/Latin Abbreviation Decoder for HerbCalc.

Provides a searchable, filterable reference table of pharmacy and
Latin abbreviations commonly found in historical and modern herbal
prescriptions. Data sourced from core.data_loader.PHARMACY_ABBREV.
"""

import gradio as gr

from core.data_loader import PHARMACY_ABBREV


def _get_abbreviations() -> list[dict]:
    """Extract the abbreviations list from loaded data."""
    if isinstance(PHARMACY_ABBREV, dict):
        return PHARMACY_ABBREV.get("abbreviations", [])
    if isinstance(PHARMACY_ABBREV, list):
        return PHARMACY_ABBREV
    return []


def _get_categories() -> list[str]:
    """Extract unique categories from abbreviation data."""
    abbrevs = _get_abbreviations()
    categories = sorted({a.get("category", "unknown") for a in abbrevs})
    return categories


def _get_roman_numeral_section() -> str:
    """Build a Markdown string for the roman numeral convention section."""
    if not isinstance(PHARMACY_ABBREV, dict):
        return ""
    roman = PHARMACY_ABBREV.get("roman_numeral_convention")
    if not roman:
        return ""

    desc = roman.get("description", "")
    examples = roman.get("examples", [])
    values = roman.get("values", {})

    lines = [f"### Roman Numeral Convention\n\n{desc}\n"]

    if examples:
        lines.append("**Examples:**")
        for ex in examples:
            lines.append(f"- {ex}")
        lines.append("")

    if values:
        lines.append("**Values:**\n")
        lines.append("| Numeral | Value |")
        lines.append("|---------|-------|")
        for numeral, val in values.items():
            lines.append(f"| {numeral} | {val} |")

    return "\n".join(lines)


def _search_abbreviations(
    search_text: str,
    category_filter: str,
) -> list[list[str]]:
    """Filter abbreviations by search text and category.

    Args:
        search_text: Text to match against abbreviation, latin, or meaning.
        category_filter: Category to filter by, or "All" for no filter.

    Returns:
        List of rows for the Dataframe output.
    """
    abbrevs = _get_abbreviations()
    results = []

    search_lower = (search_text or "").strip().lower()

    for entry in abbrevs:
        # Category filter
        if category_filter and category_filter != "All":
            if entry.get("category", "").lower() != category_filter.lower():
                continue

        # Text search across multiple fields
        if search_lower:
            searchable = " ".join([
                entry.get("abbreviation", ""),
                entry.get("latin", ""),
                entry.get("meaning", ""),
                entry.get("usage_example", ""),
                entry.get("notes", "") or "",
            ]).lower()
            if search_lower not in searchable:
                continue

        results.append([
            entry.get("abbreviation", ""),
            entry.get("latin", ""),
            entry.get("meaning", ""),
            entry.get("category", ""),
            entry.get("usage_example", ""),
        ])

    if not results:
        results.append(["(no matches)", "", "", "", ""])

    return results


def build_tab() -> gr.Tab:
    """Build and return the Pharmacy Shorthand Decoder tab."""
    with gr.Tab("Pharmacy Shorthand") as tab:
        gr.Markdown(
            "## Rx / Latin Abbreviation Decoder\n\n"
            "Search and browse pharmacy abbreviations and Latin terms "
            "commonly found in herbal prescriptions, historical formularies, "
            "and pharmacopeial texts."
        )

        categories = _get_categories()
        category_choices = ["All"] + categories

        with gr.Row():
            with gr.Column(scale=2):
                search_box = gr.Textbox(
                    label="Search",
                    placeholder="Type an abbreviation, Latin term, or keyword...",
                    value="",
                )
            with gr.Column(scale=1):
                category_filter = gr.Dropdown(
                    label="Category",
                    choices=category_choices,
                    value="All",
                )

        # Initial data load
        initial_data = _search_abbreviations("", "All")

        results_table = gr.Dataframe(
            value=initial_data,
            headers=["Abbreviation", "Latin", "Meaning", "Category", "Usage Example"],
            datatype=["str", "str", "str", "str", "str"],
            interactive=False,
            label="Abbreviations",
        )

        # Roman numeral convention section
        roman_md = _get_roman_numeral_section()
        if roman_md:
            gr.Markdown("---")
            gr.Markdown(roman_md)

        # Pedagogical accordion
        with gr.Accordion("Reading historical prescriptions", open=False):
            gr.Markdown("""
**Why learn pharmacy Latin?**

Historical herbal texts, pharmacopeial references, and even modern
clinical herbalism use a shorthand system rooted in Latin. Understanding
these abbreviations lets you:

- **Read historical formularies** from the Eclectic, Thomsonian, and
  Physiomedical traditions without guesswork.
- **Interpret monograph dosing instructions** that use terms like
  "t.i.d." (three times daily) or "q.s." (a sufficient quantity).
- **Communicate precisely** with other herbalists and pharmacists using
  standardized notation.

**How prescriptions are structured:**

A traditional herbal prescription follows this pattern:

1. **Rx** (recipe / "take") -- header, followed by the formula
2. **Ingredients** with quantities in apothecary notation
3. **Sig.** (signa / "label") -- directions for the patient
4. **Disp.** (dispensa / "dispense") -- quantity to prepare

**Example:**
```
Rx:
  Tr. Valerianae         ℥ii
  Tr. Passiflorae        ℥ii
  Tr. Scutellariae       ℥i
Sig: 30 gtt t.i.d. in water, and 60 gtt h.s.
Disp: ℥v
```

This reads: "Combine 2 oz tincture of Valerian, 2 oz tincture of
Passionflower, and 1 oz tincture of Skullcap. Directions: Take 30
drops three times daily in water, and 60 drops at bedtime.
Dispense 5 ounces."
""")

        # Event handlers
        search_box.change(
            fn=_search_abbreviations,
            inputs=[search_box, category_filter],
            outputs=[results_table],
        )
        category_filter.change(
            fn=_search_abbreviations,
            inputs=[search_box, category_filter],
            outputs=[results_table],
        )

    return tab
