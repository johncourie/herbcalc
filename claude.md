# HerbCalc: A Comprehensive Toolkit for Herbalists

## Project Overview

HerbCalc is a suite of web-based tools for herbalism students and serious hobbyists. It takes a user from zero (imperial measurements, no solvent theory, no formulation experience) to confidently formulating multi-herb extractions from monograph specifications.

The project originated as a single PHP tincture menstruum calculator (2016) and is being expanded into a full-stack herbal formulation workbench. It is an open-source pedagogical tool (CC BY 4.0) developed in the context of herbalism education at SOIH (School of Integrative Health).

## Design Philosophy

- **Metric-first, imperial-tolerant.** All internal computation is metric. Imperial/apothecary/historical inputs are converted at the boundary.
- **Pedagogical by default.** Tools don't just output numbers — they expose the reasoning. Expandable sections explain the math and the herbalism logic.
- **Data-driven.** Conversion constants, monograph data, solvent affinities, and interaction flags live in structured JSON data files, not hardcoded in tool logic.
- **Progressive complexity.** A brand-new student should be able to use the simplest tools immediately. Advanced tools (multi-herb formulation, interaction checking) are available but not overwhelming.
- **LLM-assisted development.** The codebase is structured so that individual tools can be scaffolded and iterated with LLM pair-programming. Each tool is a self-contained module with a predictable interface.

## Architecture

### Tech Stack

- **Framework:** Gradio (pin version in requirements.txt — do not chase updates)
- **Language:** Python 3.10+
- **Data layer:** Static JSON files loaded at startup into Python dicts/dataclasses. No database. No external API.
- **Deployment:** HuggingFace Spaces (free tier) as primary. Also runnable locally via `python app.py` or `gradio app.py`.
- **Styling:** Gradio's built-in theming + optional custom CSS via `gr.Blocks(css=...)`. No external CSS frameworks.
- **Legacy:** Original PHP tools remain functional at their existing URLs on potlatchdiscordian.net. New toolkit is a parallel deployment.

### Known Tradeoffs (Gradio vs SPA)

- **No offline capability.** Every interaction requires server round-trip. Acceptable because the complex tools (formula builder, interaction checker) are desk tasks, not bench tasks. For bench work, the batch log generator can produce printable output.
- **Limited UI customization.** Gradio's component library is the boundary. No drag-and-drop, no custom canvas visualizations without escape-hatching to `gr.HTML()`. Acceptable for calculator/reference tools.
- **Server dependency.** HuggingFace Spaces has cold starts and occasional downtime. For classroom reliability, also support local deployment.

### File Structure

```
herbcalc/
├── claude.md                       # This file
├── app.py                          # Main Gradio app — assembles tabs, launches
├── requirements.txt                # Pinned dependencies
├── README.md                       # User-facing project description
│
├── core/                           # Shared computation modules
│   ├── __init__.py
│   ├── units.py                    # Unit conversion engine
│   ├── solvents.py                 # Solvent system calculations
│   ├── formulation.py              # Multi-herb formula logic
│   ├── validation.py               # Input validation + pedagogical error messages
│   └── data_loader.py              # Load and cache JSON data files
│
├── tools/                          # One module per tool, each exports a build_tab() function
│   ├── __init__.py
│   ├── menstruum_calc.py           # Tincture menstruum calculator (herbcalc successor)
│   ├── unit_converter.py           # Universal unit converter
│   ├── apothecary.py               # Historical unit translator
│   ├── pearson_square.py           # Alcohol dilution calculator
│   ├── drop_calibration.py         # Drop/mL calibration tool
│   ├── percentage_expr.py          # w/w, w/v, v/v translator
│   ├── formula_builder.py          # Multi-herb formula builder
│   ├── dose_calc.py                # Dosage scaling calculator
│   ├── dry_extract.py              # Dry equivalent ↔ extract converter
│   ├── infusion_calc.py            # Infusion/decoction calculator
│   ├── syrup_calc.py               # Syrup calculator
│   ├── salve_calc.py               # Salve/balm calculator
│   ├── reverse_lookup.py           # "What can I make?" reverse calculator
│   ├── interaction_check.py        # Herb-drug interaction checker
│   ├── batch_log.py                # Batch logging template generator
│   ├── monograph_viewer.py         # Herb monograph quick reference
│   ├── pharmacy_shorthand.py       # Rx/Latin abbreviation decoder
│   └── solvent_affinity.py         # Constituent × solvent reference viewer
│
├── data/                           # Static JSON — the single source of truth
│   ├── units/
│   │   ├── metric.json
│   │   ├── apothecary.json
│   │   ├── avoirdupois.json
│   │   ├── household.json
│   │   ├── historical.json
│   │   └── pharmacy_abbrev.json
│   ├── solvents/
│   │   ├── solvents.json
│   │   └── affinity_matrix.json
│   ├── herbs/
│   │   ├── monographs.json
│   │   └── interactions.json
│   ├── formulation/
│   │   ├── preparation_types.json
│   │   └── excipients.json
│   └── pedagogy/
│       └── glossary.json
│
├── legacy/                         # Original PHP tools (archived reference)
│   ├── herbcalc.php
│   ├── ratio.php
│   ├── herbcalc2.php
│   ├── herbcalc2.1.php
│   ├── herbcalc2fancy.php
│   ├── herbcalc2stripped.php
│   └── Conversion.php
│
└── tests/
    ├── test_units.py
    ├── test_solvents.py
    ├── test_formulation.py
    └── test_validation.py
```

### Module Interface Convention

Every tool module in `tools/` exports a single function:

```python
def build_tab() -> gr.Tab:
    """Build and return a complete Gradio Tab for this tool."""
    with gr.Tab("Tool Name") as tab:
        # Inputs, outputs, callbacks, pedagogical accordions
        ...
    return tab
```

`app.py` assembles tabs:

```python
import gradio as gr
from tools import menstruum_calc, unit_converter, pearson_square, ...

with gr.Blocks(title="HerbCalc", theme=gr.themes.Soft()) as app:
    gr.Markdown("# HerbCalc: Tools for Herbalists")
    
    with gr.Tabs():
        menstruum_calc.build_tab()
        unit_converter.build_tab()
        pearson_square.build_tab()
        # ... all tools
    
    gr.Markdown("*CC BY 4.0 — HerbCalc Project*")

app.launch()
```

### Data Loading Convention

`core/data_loader.py` loads all JSON at import time and exposes as module-level dicts:

```python
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def _load(relative_path: str) -> dict:
    with open(DATA_DIR / relative_path) as f:
        return json.load(f)

METRIC = _load("units/metric.json")
APOTHECARY = _load("units/apothecary.json")
AVOIRDUPOIS = _load("units/avoirdupois.json")
HOUSEHOLD = _load("units/household.json")
HISTORICAL = _load("units/historical.json")
PHARMACY_ABBREV = _load("units/pharmacy_abbrev.json")
SOLVENTS = _load("solvents/solvents.json")
AFFINITY_MATRIX = _load("solvents/affinity_matrix.json")
MONOGRAPHS = _load("herbs/monographs.json")
INTERACTIONS = _load("herbs/interactions.json")
PREPARATION_TYPES = _load("formulation/preparation_types.json")
EXCIPIENTS = _load("formulation/excipients.json")
GLOSSARY = _load("pedagogy/glossary.json")
```

Tools import what they need: `from core.data_loader import SOLVENTS, AFFINITY_MATRIX`

## Tool Inventory

Tools are organized by domain. Each tool is a Gradio Tab built by its own module.

### Domain 1: Unit Translation

| Tool | Module | Description |
|------|--------|-------------|
| Universal Converter | `unit_converter.py` | Metric ↔ imperial ↔ apothecary ↔ household, mass and volume. Successor to Conversion.php. Dropdowns for source/target system and unit, numeric input, instant output in all target units. |
| Apothecary Translator | `apothecary.py` | Specialized for historical pharmacy units: grains, scruples, drams, minims. Bidirectional with metric. Includes disambiguation notes (apothecary oz ≠ avoirdupois oz). |
| Pharmacy Shorthand Decoder | `pharmacy_shorthand.py` | Searchable/filterable reference table. Text input for abbreviation → meaning lookup. Renders from `pharmacy_abbrev.json`. Uses `gr.Dataframe` for browsable table + `gr.Textbox` for search. |
| Drop Calibration | `drop_calibration.py` | Dropdown for dropper type × solvent → approximate drops/mL with confidence range. Pedagogical emphasis: drops are imprecise. Output includes a warning about variability. |
| Percentage Expression Translator | `percentage_expr.py` | Numeric input + radio select (w/w, w/v, v/v) → converts to all three conventions with density corrections. Uses ethanol density table from `solvents.json` for ethanol-water mixtures. |

### Domain 2: Solvent Systems

| Tool | Module | Description |
|------|--------|-------------|
| Menstruum Calculator | `menstruum_calc.py` | Core tincture calculator (herbcalc successor). Inputs: herb weight, extraction ratio, ethanol source concentration, target alcohol %, glycerin %. Extended with solvent mode selector: hydroethanolic, glycerite, acetum, oil infusion. Contextual solvent affinity notes from data. |
| Pearson's Square | `pearson_square.py` | Standalone alcohol dilution. Inputs: source concentration, target concentration, desired total volume. Also: reverse mode — "I have X-proof vodka, what's my max achievable menstruum concentration at ratio Y?" |
| Solvent Affinity Reference | `solvent_affinity.py` | Interactive matrix viewer. Dropdown for constituent class → shows extraction efficiency across all solvents with notes. Or: dropdown for solvent → shows what it extracts well/poorly. Renders from `affinity_matrix.json`. Uses `gr.Dataframe` or styled `gr.HTML`. |

### Domain 3: Formulation

| Tool | Module | Description |
|------|--------|-------------|
| Multi-Herb Formula Builder | `formula_builder.py` | Dynamic form: add herbs (dropdown from monographs or freeform), assign parts, each with individual ratio/alcohol % (auto-populated from monograph if available). Calculates compromise menstruum or per-herb extraction + blend volumes. Uses `gr.Dataframe` for herb list with add/remove rows. |
| Dosage Scaler | `dose_calc.py` | Parts notation → absolute weights for target bottle sizes (30/60/120mL presets or custom) and dose volumes. Also: doses-per-bottle count. |
| Dry ↔ Extract Converter | `dry_extract.py` | Bidirectional: dried herb weight ↔ tincture volume at a given ratio. Simple but students struggle with it. |

### Domain 4: Preparation Calculators

| Tool | Module | Description |
|------|--------|-------------|
| Infusion/Decoction | `infusion_calc.py` | Radio select mode (standard/cold/decoction). Inputs: herb weight, water volume. Outputs: steep time, expected yield after reduction (for decoction), concentration. |
| Syrup Calculator | `syrup_calc.py` | Mode: simple (1:1) or rich (2:1). Inputs: volume of herbal decoction, sugar type (sucrose/honey with density correction). Outputs: sugar quantity, total yield, shelf stability notes. |
| Salve/Balm Calculator | `salve_calc.py` | Inputs: infused oil volume, target consistency slider or presets (liquid → soft salve → firm salve → balm → lip balm). Outputs: beeswax quantity. Optional modifiers: shea butter, cocoa butter, lanolin with adjusted beeswax. |

### Domain 5: Quality & Safety

| Tool | Module | Description |
|------|--------|-------------|
| Interaction Checker | `interaction_check.py` | Dropdown for herb (from monographs) → displays all known interactions with severity flags, evidence levels, mechanisms, recommendations. Also: multi-select herbs to check a formula for combined interaction risks. |
| Batch Log Generator | `batch_log.py` | Form inputs for batch details (herb, source, lot, weights, solvents, dates, notes). Button generates a formatted, printable HTML batch record via `gr.HTML()`. Option to download as text/markdown. |

### Domain 6: Reference

| Tool | Module | Description |
|------|--------|-------------|
| Monograph Viewer | `monograph_viewer.py` | Dropdown for herb → renders structured monograph card: nomenclature, plant part, extraction parameters, constituents, dosage, safety, energetics. Uses `gr.Accordion` sections for information density. |
| Reverse Lookup | `reverse_lookup.py` | Checkbox/multi-select inputs: what solvents do you have, what equipment do you have. Outputs: feasible preparation types from `preparation_types.json` filtered by available resources. |
| Glossary | (embedded) | Not a standalone tab. Glossary terms surface as `gr.Accordion` or `gr.Markdown` info blocks within individual tools where the terms are used. |

## Data File Specifications

All data lives in `data/` as static JSON. Schemas are defined in full in `STATIC_DATA_MANIFEST.md` and the `DATA_GENERATION_PROMPT.md` used for LLM-assisted data authoring. The brief summary:

| File | Contents | Size Estimate |
|------|----------|---------------|
| `units/metric.json` | SI conversion factors | ~10 entries |
| `units/avoirdupois.json` | US/UK customary mass | ~7 entries |
| `units/apothecary.json` | Full apothecary system + disambiguation | ~15 entries |
| `units/household.json` | Kitchen measures + precision flags | ~15 entries |
| `units/historical.json` | TCM, Ayurvedic, Unani units | ~25 entries |
| `units/pharmacy_abbrev.json` | Rx/Latin abbreviation decoder | ~60 entries |
| `solvents/solvents.json` | Solvent properties + ethanol density table | ~12 solvents + 21-row density table |
| `solvents/affinity_matrix.json` | Constituent × solvent efficiency | ~18 constituent classes × 8 solvent categories |
| `formulation/preparation_types.json` | Preparation parameters and defaults | ~18 preparation types |
| `formulation/excipients.json` | Topical/syrup ingredient properties | ~10 materials |
| `herbs/monographs.json` | Structured herb monographs | 50-100 herbs (built incrementally) |
| `herbs/interactions.json` | Herb-drug interaction flags | Parallel to monographs |
| `pedagogy/glossary.json` | Term definitions | ~100-150 terms (built incrementally) |

## Computation Module Specifications

### core/units.py

```python
def convert(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """Convert between any two registered units of the same type (mass or volume).
    
    Conversion path: source unit → base unit (gram or mL) → target unit.
    Works across systems (apothecary drams → metric grams → household teaspoons).
    
    Returns ConversionResult with value, unit, precision flag, and warnings list.
    Warnings flag imprecise conversions (e.g., household cups, drops).
    """

def convert_all(value: float, from_unit: str, target_system: str = None) -> list[ConversionResult]:
    """Convert to all units of the same type, optionally filtered to a target system."""

def get_unit_info(unit_name: str) -> UnitInfo:
    """Return metadata for a unit: symbol, system, type, equivalences, disambiguation."""
```

Unit registry built at import time from all `data/units/*.json` files. Flat lookup dict keyed by unit name with aliases (e.g., "oz" → "ounce_avoirdupois", "℥" → "ounce_apothecary").

### core/solvents.py

```python
def calculate_menstruum(
    herb_weight_g: float,
    ratio: float,
    ethanol_source_pct: float,
    target_alcohol_pct: float,
    glycerin_pct: float = 0,
    solvent_mode: str = "hydroethanolic"
) -> MenstruumResult:
    """Core menstruum calculation. Returns total volume and per-solvent breakdown."""

def pearson_square(
    source_concentration: float,
    target_concentration: float,
    total_volume_ml: float
) -> DilutionResult:
    """Alcohol dilution via Pearson's square method."""

def density_correct(volume_ml: float, substance: str) -> float:
    """Convert volume to weight using substance density from solvents.json."""

def lookup_ethanol_density(ethanol_pct_vv: float) -> float:
    """Interpolate ethanol-water mixture density from density table."""

def convert_percentage(value: float, from_convention: str, to_convention: str, 
                       substance: str = "ethanol") -> float:
    """Convert between w/w, w/v, v/v percentage expressions with density correction."""
```

### core/formulation.py

```python
def build_formula(
    herbs: list[HerbEntry],
    target_volume_ml: float = None,
    bottle_size_ml: float = None
) -> FormulaResult:
    """Multi-herb formula calculation.
    
    Each HerbEntry has: name, parts, ratio, alcohol_pct (from monograph or manual).
    Returns per-herb weights, combined menstruum, and compromise solvent composition.
    """

def scale_parts(parts: list[PartEntry], target_total_g: float) -> list[ScaledEntry]:
    """Convert parts notation to absolute weights."""

def dry_equivalent(tincture_ml: float, ratio: float) -> float:
    """Tincture volume → equivalent dried herb weight."""

def tincture_from_dose(target_herb_mg: float, ratio: float) -> float:
    """Target dried herb dose → required tincture volume."""
```

### core/validation.py

```python
def validate_range(value: float, min_val: float, max_val: float, 
                   field_name: str) -> ValidationResult:
    """Range check with pedagogical error message."""

def validate_menstruum_inputs(herb_g, ratio, ethanol_source, target_alc, 
                               glycerin_pct) -> list[ValidationResult]:
    """Full validation suite for menstruum calculator.
    
    Checks:
    - Positive herb weight
    - Ratio >= 1
    - Target alcohol % <= ethanol source %
    - Glycerin + alcohol don't exceed total menstruum
    - Warns if alcohol % is unusually high/low for typical tinctures
    
    Error messages are pedagogical:
    'Target alcohol (70%) exceeds your ethanol source (40% — vodka). 
     You cannot concentrate alcohol by dilution. Use a higher-proof source 
     or lower your target percentage.'
    """
```

## Gradio-Specific UI Conventions

### Layout Patterns

- **Tool tabs:** Each tool is a `gr.Tab` inside the top-level `gr.Tabs`. Group related tools with `gr.TabItem` nesting if Gradio version supports it, otherwise flat tabs ordered by domain.
- **Input → Output flow:** Left column (or top) for inputs, right column (or bottom) for outputs. Use `gr.Row` and `gr.Column` for side-by-side on desktop; Gradio handles mobile stacking automatically.
- **Defaults:** All inputs have sensible defaults that produce a recognizable result. The menstruum calculator defaults (100g herb, 1:5 ratio, 94% ethanol source, 40% target) should be identical to the original herbcalc.php defaults for continuity.

### Component Selection Guide

| Need | Gradio Component |
|------|-----------------|
| Numeric input | `gr.Number(label=..., value=default, minimum=..., maximum=...)` |
| Unit/mode selection | `gr.Radio` (≤5 options) or `gr.Dropdown` (>5 options) |
| Multi-select (herbs, solvents) | `gr.CheckboxGroup` or `gr.Dropdown(multiselect=True)` |
| Herb selection from monographs | `gr.Dropdown(choices=herb_names, allow_custom_value=True)` |
| Calculated output (single values) | `gr.Textbox(label=..., interactive=False)` or `gr.Number(interactive=False)` |
| Tabular output (batch results, conversions) | `gr.Dataframe(interactive=False)` |
| Formatted output (monograph cards, batch logs) | `gr.Markdown` or `gr.HTML` |
| Pedagogical explanations | `gr.Accordion("Why does this matter?", open=False)` containing `gr.Markdown` |
| Warnings | `gr.Markdown` with bold/color. Or `gr.Info()` / `gr.Warning()` popups for critical validation errors. |
| Printable output | `gr.HTML` with print-friendly CSS + `gr.File` for download |
| Dynamic herb list (formula builder) | `gr.Dataframe(interactive=True)` with add/remove functionality |

### Pedagogical Accordions

Every tool should include at least one `gr.Accordion` section with expandable explanations, continuing the pattern from Conversion.php. Examples:

```python
with gr.Accordion("How is the menstruum calculated?", open=False):
    gr.Markdown("""
    **Total menstruum** = herb weight × extraction ratio
    
    The ratio (e.g., 1:5) means 1 gram of herb to 5 mL of menstruum. 
    A 1:5 tincture of 100g herb needs 500mL total liquid.
    
    The alcohol percentage in the final tincture is achieved by diluting 
    your ethanol source (e.g., 95% Everclear) with water. The calculator 
    uses this proportion to determine how much of your source alcohol 
    and how much water to combine.
    """)
```

### Theming

Use `gr.themes.Soft()` as base. Override with custom CSS if needed for:
- Warning/error text colors (yellow for caution, red for error)
- Output section background differentiation
- Print stylesheet for batch log output

## Coding Conventions

- Python 3.10+. Type hints on all function signatures.
- Docstrings on all public functions (Google style).
- `dataclasses` or `NamedTuple` for structured return types (ConversionResult, MenstruumResult, etc.) — not raw dicts.
- All magic numbers extracted to data files or module-level named constants.
- No computation in tool UI modules — tool modules call `core/` functions and format results for display. Separation of computation from presentation.
- JSON data files use underscores in filenames (not hyphens) to match Python import conventions.

## Testing Strategy

- `pytest` for all `core/` modules.
- Test cases with known inputs → expected outputs from published pharmacopeial formulas.
- Apothecary conversion tests against Remington's tables.
- Edge cases: zero glycerin, 100% alcohol, 1:1 ratio (fresh herb), very large ratios (1:50), imperial inputs with fractions.
- Menstruum calculator regression tests using original herbcalc.php outputs as reference (same inputs → same results).
- No UI tests — Gradio's own testing handles component rendering. Test the computation layer.

## Deployment

### HuggingFace Spaces (Primary)

```
# requirements.txt
gradio==4.x.x  # Pin specific version
```

Push repo to HF Space. `app.py` is the entry point. Gradio auto-detected.

### Local Development

```bash
pip install -r requirements.txt
python app.py
# or
gradio app.py
```

Runs on `localhost:7860` by default.

### SOIH / Classroom Deployment

For reliability in classroom settings where HF Spaces cold starts are unacceptable:
- Run on any machine with Python 3.10+: `python app.py --server-name 0.0.0.0 --server-port 7860`
- Share via LAN. Students connect to instructor's IP.
- Or: deploy on a cheap VPS (DigitalOcean $6/mo, Fly.io free tier).

## Versioning & Migration

- Original PHP tools remain at potlatchdiscordian.net/Herbalism/ — no breaking changes.
- New toolkit is HerbCalc 2.0, parallel deployment.
- Semantic versioning from 2.0.0 onward.
- Git repository. Tag releases.

## License

CC BY 4.0 International, consistent with all prior versions.

## Priority Order for Implementation

1. **Data files first.** Unit conversion tables, solvent properties, and affinity matrix. (Use DATA_GENERATION_PROMPT.md for LLM-assisted authoring.)
2. **`core/data_loader.py` + `core/units.py`** — foundational infrastructure.
3. **`tools/unit_converter.py`** — first working Gradio tab, replaces Conversion.php. Proves the architecture.
4. **`core/solvents.py` + `tools/menstruum_calc.py`** — replaces herbcalc.php with multi-solvent support.
5. **`tools/pearson_square.py`** — standalone, small, high-value.
6. **`tools/percentage_expr.py`** — foundational for understanding the rest.
7. **`tools/drop_calibration.py`** — small tool, high pedagogical value.
8. **`tools/apothecary.py` + `tools/pharmacy_shorthand.py`** — reference tools.
9. **`tools/monograph_viewer.py`** — requires `herbs/monographs.json` to be populated.
10. **`core/formulation.py` + `tools/formula_builder.py`** — capstone tool.
11. **`tools/dose_calc.py` + `tools/dry_extract.py`** — formula support tools.
12. **`tools/infusion_calc.py`, `tools/syrup_calc.py`, `tools/salve_calc.py`** — preparation-specific.
13. **`tools/interaction_check.py`** — requires `interactions.json`.
14. **`tools/reverse_lookup.py` + `tools/batch_log.py`** — quality-of-life tools.
15. **`tools/solvent_affinity.py`** — reference viewer, can ship whenever affinity data is ready.
