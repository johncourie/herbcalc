# HerbCalc Static Data Generation Prompt

Copy everything below the line into a new conversation. Replace the two bracketed fields at the bottom.

---

## System Context

You are helping me build static JSON data files for **HerbCalc**, an open-source (CC BY 4.0) Gradio-based Python toolkit for herbalism students and serious hobbyists. The toolkit is a suite of calculators and reference tools for herbal formulation — tincture menstruum calculations, unit conversions, solvent selection, multi-herb formulation, dosage scaling, interaction checking, etc.

The data layer is static JSON files loaded at application startup into Python dicts. No database. No API. These JSON files are the single source of truth for all constants, conversion factors, material properties, and reference data used across the toolkit's computation and UI modules.

I am a professor of herbalism at SOIH (School of Integrative Health) with expertise in herbal product design, toxicology, pharmacovigilance, and botanical processing. Treat me as a subject-matter expert reviewer — I will validate your output, but I need you to do the compilation work accurately from authoritative sources.

## Your Task

**Today we are generating: `[FILENAME]`**

*(Replace [FILENAME] with the target, e.g., `data/units/apothecary.json`, `data/solvents/solvents.json`, `data/herbs/monographs.json`, etc.)*

## File Specifications by Path

Use the spec below that matches the filename. If the filename isn't listed, ask me for the spec before proceeding.

---

### `data/units/metric.json`
SI mass and volume conversion factors. Base units: gram (mass), milliliter (volume). All entries expressed as multiplier to base unit.
- **Mass:** microgram, milligram, centigram, decigram, gram, decagram, hectogram, kilogram
- **Volume:** microliter, milliliter, centiliter, deciliter, liter
- **Schema per entry:**
```json
{
  "unit_name": "kilogram",
  "symbol": "kg",
  "system": "metric",
  "type": "mass",
  "to_base": 1000,
  "base_unit": "gram",
  "aliases": ["kg", "kilo", "kilogram", "kilograms"]
}
```
- **The `aliases` array** is used by the unit conversion engine to build a flat lookup registry. Include common abbreviations, plural forms, and any shorthand a student might type into a text field. This field appears on all unit entries across all unit files.
- **Sources:** SI definitional. No ambiguity.

---

### `data/units/avoirdupois.json`
US/UK customary mass units. All entries convert to grams.
- **Units:** grain, dram, ounce, pound, stone, hundredweight (short), ton (short)
- **Schema:** Same as metric.json, with added `"equivalence"` field showing inter-unit relationships.
- **Top-level `"notes"` field:** Embed that avoirdupois grain = apothecary grain (same: 64.79891 mg). Systems diverge at dram/ounce/pound.
- **Sources:** NIST Handbook 44.

---

### `data/units/apothecary.json`
Full apothecary system, mass and volume, with Unicode symbols and inter-unit equivalences.
- **Mass:** grain (gr), scruple (℈), dram (ʒ), ounce (℥), pound (lb ap)
- **Volume:** minim (♏), fluid scruple, fluid dram (ƒʒ), fluid ounce (ƒ℥), pint (O), gallon (C)
- **Schema per entry:**
```json
{
  "unit_name": "scruple",
  "symbol": "℈",
  "unicode_codepoint": "U+2108",
  "system": "apothecary",
  "type": "mass",
  "to_base": 1.2959782,
  "base_unit": "gram",
  "equivalence": "20 grains = 1 scruple",
  "disambiguation": null,
  "aliases": ["scruple", "scruples", "℈"]
}
```
- **Required top-level `"disambiguation_notes"` array** with entries for: ounce (apothecary vs avoirdupois — 9.7% difference), pound (apothecary 12oz vs avoirdupois 16oz — 21.5% difference), dram (apothecary vs avoirdupois — 119.4% difference, the most dangerous confusion), and grain (same in both systems — the one that doesn't diverge).
- **Sources:** Remington's Pharmaceutical Sciences, USP historical appendices, British Pharmacopoeia.

---

### `data/units/household.json`
Kitchen/household measurements, primarily volume. US defaults with regional variants noted.
- **Units:** drop, smidgen, pinch, dash, teaspoon, dessertspoon, tablespoon, fluid ounce, cup, pint, quart, gallon, dropperful
- **Schema per entry:** Same base schema plus:
```json
{
  "precise": false,
  "variance_note": "Drops vary by viscosity, dropper geometry, temperature. Range: 0.03-0.07 mL.",
  "regional_variants": [
    { "region": "AU", "name": "Australian tablespoon", "to_base": 20.0 },
    { "region": "metric", "name": "Metric cup", "to_base": 250.0 },
    { "region": "imperial", "name": "Imperial pint", "to_base": 568.261 }
  ]
}
```
- **The `precise` flag** is consumed by the unit converter to append warnings when imprecise units are involved. Drops, dropperfuls, pinches, smidgens, dashes = `false`. Everything else = `true`.
- **Sources:** NIST, USDA, FDA labeling guidelines.

---

### `data/units/historical.json`
Non-Western and historical measurement systems encountered in herbal/medical literature.
- **Systems:** Chinese/TCM (modern standardized post-1949 + classical with dynasty-specific notes), Ayurvedic, Unani
- **Schema per entry:** Same base schema plus:
```json
{
  "system": "tcm_modern",
  "era": "post-1949 standardized",
  "region": "China",
  "confidence": "standardized",
  "historical_note": "Classical Han dynasty liang ≈ 15.6g, not modern 50g. Do not convert classical text doses using modern values without scholarly context."
}
```
- **Confidence levels:** `"standardized"` (modern official value), `"approximate"` (generally agreed), `"variable"` (changed over time/region, use with caution)
- **Top-level `"system_warning"` string:** "Historical units varied by region and era. Use for interpretive reference, not precision formulation. Always verify against the specific text and historical context."
- **Sources:** WHO Traditional Medicine references, Bensky's Materia Medica, Dash & Sharma, academic pharmacognosy.

---

### `data/units/pharmacy_abbrev.json`
Latin/Rx abbreviations and symbols. A decoder/lookup reference, NOT a conversion table.
- **Categories:** quantity/measurement, frequency/timing, form/preparation, instructions
- **Schema per entry:**
```json
{
  "abbreviation": "q.s.",
  "latin": "quantum sufficit",
  "meaning": "a sufficient quantity",
  "category": "quantity",
  "usage_example": "q.s. ad 100 mL = add enough [solvent] to bring total volume to 100 mL",
  "notes": null
}
```
- **Top-level `"roman_numeral_convention"` object:**
```json
"roman_numeral_convention": {
  "description": "Quantities written as lowercase Roman numerals after unit symbol",
  "examples": ["℥iv = 4 ounces", "gr x = 10 grains", "gtt iii = 3 drops", "℥ss = half an ounce"],
  "values": { "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10, "xii": 12, "xv": 15, "xx": 20, "xxx": 30 }
}
```
- **Sources:** Remington's, any dispensing pharmacy textbook.

---

### `data/solvents/solvents.json`
Physical and extraction properties of solvents used in herbal preparation.
- **Solvents:** ethanol, water, glycerin, acetic_acid, olive_oil, coconut_oil, jojoba_oil, sweet_almond_oil, grapeseed_oil, sunflower_oil, sesame_oil, honey
- **Schema per solvent:**
```json
{
  "id": "ethanol",
  "name": "Ethanol",
  "density_g_ml": 0.789,
  "density_note": "Anhydrous at 20°C. See ethanol_water_density_table for mixture densities.",
  "polarity": "medium-high",
  "miscible_with": ["water", "glycerin"],
  "immiscible_with": ["fixed_oils"],
  "common_sources": [
    { "name": "Everclear 190 proof", "concentration_pct": 95, "notes": "US, varies by state" },
    { "name": "Everclear 151 proof", "concentration_pct": 75.5, "notes": "Available in states restricting 190" },
    { "name": "Vodka (80 proof)", "concentration_pct": 40, "notes": "Widely available" },
    { "name": "Brandy (80 proof)", "concentration_pct": 40, "notes": "Adds flavor" },
    { "name": "Lab-grade ethanol", "concentration_pct": 95, "notes": "Not denatured" }
  ],
  "extracts_well": ["alkaloids", "volatile_oils", "resins", "some_flavonoids", "some_glycosides"],
  "extracts_moderately": ["tannins", "coumarins", "phenolic_acids"],
  "extracts_poorly": ["polysaccharides", "minerals", "mucilage"],
  "shelf_life_contribution": "Preservative above ~20% in final preparation",
  "safety_notes": "Flammable. Not suitable for individuals avoiding alcohol.",
  "notes": "Primary solvent for most tinctures. Higher concentrations favor resins and volatile oils; lower concentrations favor water-soluble constituents."
}
```
- **Critical sub-dataset — top-level key `"ethanol_water_density_table"`:**
  Density of ethanol-water mixtures at 20°C, every 5% v/v from 0-100%. 21 data points. This is the single most important reference table in the project — it enables accurate w/v ↔ v/v conversions and density-corrected calculations.
  ```json
  "ethanol_water_density_table": [
    { "ethanol_pct_vv": 0, "density_g_ml": 1.0000 },
    { "ethanol_pct_vv": 5, "density_g_ml": 0.9900 },
    ...
    { "ethanol_pct_vv": 100, "density_g_ml": 0.7893 }
  ]
  ```
  Data source: International Alcoholometric Tables (OIML R 22), CRC Handbook, Perry's Chemical Engineers' Handbook. Verify each value against source — this table is used in every solvent calculation.
- **Sources:** CRC Handbook of Chemistry and Physics, Merck Index, OIML R 22, USP/NF excipient monographs.

---

### `data/solvents/affinity_matrix.json`
Constituent class × solvent extraction efficiency matrix.
- **Constituent classes (18 rows):** alkaloids, flavonoids, tannins_hydrolyzable, tannins_condensed, saponins, volatile_oils, fixed_oils, polysaccharides, minerals, resins, glycosides_cardiac, glycosides_anthraquinone, glycosides_cyanogenic, mucilage, bitter_compounds, phenolic_acids, coumarins, lignans
- **Solvent categories (8 columns):** ethanol_high (>60%), ethanol_medium (40-60%), ethanol_low (20-40%), water_hot, water_cold, glycerin, acetic_acid, fixed_oil
- **Efficiency ratings:** `"good"`, `"moderate"`, `"poor"`, `"none"`, `"variable"` (requires explanatory note)
- **Schema per entry:**
```json
{
  "constituent_class": "alkaloids",
  "display_name": "Alkaloids",
  "description": "Nitrogen-containing organic compounds with pharmacological activity. Examples: berberine, caffeine, morphine, nicotine.",
  "solvent_affinity": {
    "ethanol_high": "good",
    "ethanol_medium": "good",
    "ethanol_low": "moderate",
    "water_hot": "moderate",
    "water_cold": "poor",
    "glycerin": "poor",
    "acetic_acid": "good",
    "fixed_oil": "poor"
  },
  "notes": "Extraction depends on salt form vs free base. Acidic solvents convert alkaloids to salts, improving aqueous solubility."
}
```
- **This file requires my review before finalization.** Flag uncertain ratings with an additional `"confidence": "needs_review"` field on the entry and explain why after the JSON output.
- **Sources:** Trease & Evans Pharmacognosy, Bruneton Pharmacognosy Phytochemistry Medicinal Plants, Bone & Mills Principles and Practice of Phytotherapy.

---

### `data/formulation/preparation_types.json`
Parameters and defaults for each preparation type.
- **Preparations:** tincture, glycerite, acetum, oxymel, standard_infusion, cold_infusion, decoction, simple_syrup, rich_syrup, herbal_syrup, oil_infusion_cold, oil_infusion_hot, salve, balm, lip_balm, poultice, compress, electuary, capsule, pastille
- **Schema per preparation:**
```json
{
  "id": "tincture",
  "display_name": "Tincture (Hydroethanolic Extract)",
  "solvent_system": "hydroethanolic",
  "typical_ratios": {
    "dried": ["1:4", "1:5"],
    "fresh": ["1:1", "1:2"]
  },
  "alcohol_range_pct": { "min": 25, "max": 90 },
  "maceration_time": { "min_days": 14, "typical_days": 28, "max_days": 42 },
  "shelf_life": { "min_years": 3, "typical_years": 5, "notes": "Indefinite if properly stored and >20% alcohol" },
  "storage": "Amber glass, cool, dark, tightly sealed",
  "equipment": [
    "glass jar with lid",
    "scale (0.1g precision minimum)",
    "graduated cylinder or measuring cup",
    "fine mesh strainer or cheesecloth",
    "press (potato ricer or tincture press)",
    "amber glass bottles with dropper caps",
    "labels"
  ],
  "process_summary": "Weigh herb, calculate menstruum, combine in jar, macerate with daily agitation, press and filter, bottle and label.",
  "common_mistakes": [
    "Using kitchen scale without 0.1g precision",
    "Not accounting for ethanol concentration of source alcohol",
    "Insufficient maceration time",
    "Squeezing cheesecloth instead of pressing (low yield)"
  ],
  "required_solvents": ["ethanol", "water"],
  "optional_solvents": ["glycerin"],
  "calculator_tool": "menstruum_calc",
  "pedagogical_notes": "The standard starting point for herbal extraction."
}
```
- **The `required_solvents` and `calculator_tool` fields** enable the reverse lookup tool to filter by available materials and link to the appropriate calculator.
- **Sources:** Easley & Horne, Green, Gladstar, Hardin.

---

### `data/formulation/excipients.json`
Non-solvent formulation ingredients for topicals and syrups.
- **Materials:** beeswax, candelilla_wax, shea_butter, cocoa_butter, mango_butter, lanolin, emulsifying_wax, stearic_acid, vitamin_e_tocopherol, benzoin_tincture, rosemary_oleoresin_extract, sucrose
- **Schema per material:**
```json
{
  "id": "beeswax",
  "name": "Beeswax",
  "type": "thickener",
  "density_g_ml": 0.96,
  "melting_point_c": { "low": 62, "high": 65 },
  "usage_guidelines": {
    "salve_soft": { "ratio": "1 oz per 10 oz oil", "beeswax_pct": 9.1 },
    "salve_medium": { "ratio": "1 oz per 8 oz oil", "beeswax_pct": 11.1 },
    "salve_firm": { "ratio": "1 oz per 5 oz oil", "beeswax_pct": 16.7 },
    "lip_balm": { "ratio": "1 oz per 3 oz oil", "beeswax_pct": 25.0 }
  },
  "vegan_alternative": { "name": "candelilla wax", "ratio_adjustment": "use approximately half the amount", "notes": "Higher melting point (68-73°C)" },
  "safety": "Generally safe. Rare contact allergy possible.",
  "sourcing_notes": "Cosmetic-grade or food-grade. Yellow retains some propolis and aroma. White is neutral.",
  "notes": "Standard thickener for oil-based preparations."
}
```
- **Sources:** Poucher's Perfumes Cosmetics and Soaps, cosmetic chemistry references, formulary guides.

---

### `data/herbs/monographs.json`
Structured monograph data. **This is the big one.**
- **Target:** 50 herbs minimum. See priority list in STATIC_DATA_MANIFEST.md.
- **Workflow:** Do NOT try to generate all 50 in one session. Work in batches of 5-10 herbs. I will specify which herbs to generate each session.
- **Today's batch:** `[LIST HERBS HERE, e.g., "Valerian, Passionflower, Skullcap, Chamomile, Lemon balm"]`
- **Schema per herb:**
```json
{
  "id": "valerian",
  "common_name": "Valerian",
  "latin_name": "Valeriana officinalis",
  "family": "Caprifoliaceae",
  "plant_part": "root",
  "habitat": "temperate regions, moist soil",
  "key_constituents": [
    { "class": "volatile_oils", "compounds": ["valerenic acid", "isovaleric acid"] },
    { "class": "alkaloids", "compounds": ["actinidine", "chatinine"] },
    { "class": "flavonoids", "compounds": ["linarin", "hesperidin"] }
  ],
  "extraction": {
    "tincture": {
      "herb_state": "fresh or dried",
      "ratio_fresh": "1:2",
      "ratio_dried": "1:5",
      "alcohol_pct": 70,
      "menstruum_notes": "Higher alcohol for volatile oil content"
    },
    "glycerite": {
      "ratio": "1:5",
      "glycerin_pct": 60,
      "notes": "Less effective for volatile oils than ethanol"
    },
    "infusion": {
      "suitable": false,
      "notes": "Volatile oils lost to evaporation in hot infusion. Cold infusion possible but slow."
    },
    "decoction": {
      "suitable": false,
      "notes": "Degrades volatile constituents"
    }
  },
  "dosage": {
    "tincture_ml": { "low": 2, "mid": 3, "high": 5, "frequency": "2-3x daily" },
    "dried_herb_g": { "low": 2, "mid": 4, "high": 6 },
    "notes": "Best taken 30-60 minutes before bed for sleep support"
  },
  "safety": {
    "generally_recognized_as_safe": true,
    "pregnancy": "avoid",
    "lactation": "insufficient data",
    "children": "reduced dose, consult practitioner",
    "interactions": ["CNS_depressants", "benzodiazepines", "barbiturates"],
    "interaction_severity": "moderate",
    "contraindications": ["scheduled_surgery_2_weeks"],
    "notes": "May potentiate sedative medications"
  },
  "energetics": {
    "taste": ["bitter", "pungent"],
    "temperature": "warming",
    "moisture": "drying",
    "tcm_actions": ["calms shen", "moves qi"],
    "ayurvedic_actions": ["vata-pacifying"]
  },
  "tags": ["nervine", "sedative", "antispasmodic", "carminative"]
}
```
- **Sources per herb — cross-reference minimum 2:** WHO Monographs, EMA/HMPC Community Herbal Monographs, AHP monographs, German Commission E, Bone & Mills, Hoffmann, PDR for Herbal Medicines, Mills & Bone Essential Guide to Herbal Safety.
- **Confidence flags:** If unsure about a value (especially extraction ratios, interaction severity, or energetics), add `"confidence": "needs_review"` as a field on that specific object and note why after the JSON output.

---

### `data/herbs/interactions.json`
Herb-drug interaction data.
- **Scope:** One entry per herb with known or theoretical interactions.
- **Work in parallel with monographs.json** — generate for the same batch of herbs.
- **Schema per herb:**
```json
{
  "herb": "St. John's Wort",
  "latin_name": "Hypericum perforatum",
  "interactions": [
    {
      "drug_class": "SSRIs",
      "specific_drugs": ["fluoxetine", "sertraline", "paroxetine", "citalopram"],
      "mechanism": "Additive serotonergic activity — risk of serotonin syndrome",
      "direction": "potentiation",
      "severity": "major",
      "evidence_level": "clinical_reports",
      "recommendation": "Contraindicated. Do not combine.",
      "references": ["Mills & Bone 2005", "EMA/HMPC assessment"]
    }
  ],
  "cyp_interactions": {
    "CYP3A4": "strong_inducer",
    "CYP2C9": "inducer",
    "CYP1A2": "inducer",
    "P_glycoprotein": "inducer"
  },
  "general_notes": "Potent CYP3A4 and P-glycoprotein inducer. Affects metabolism of ~50% of pharmaceutical drugs."
}
```
- **Severity:** `"major"` (clinically significant, avoid), `"moderate"` (monitor, may need adjustment), `"minor"` (unlikely clinical significance), `"theoretical"` (mechanistic plausibility, no clinical reports)
- **Evidence:** `"clinical_trials"`, `"clinical_reports"`, `"in_vitro"`, `"traditional_caution"`, `"theoretical"`
- **`cyp_interactions` object:** Optional per herb. Include for any herb with documented CYP450 or P-glycoprotein activity. Values: `"strong_inducer"`, `"inducer"`, `"inhibitor"`, `"strong_inhibitor"`, `"substrate"`, `"none_known"`.
- **Sources:** Natural Medicines Comprehensive Database, Stockley's Herbal Medicines Interactions, EMA assessments, Mills & Bone Essential Guide to Herbal Safety.

---

### `data/pedagogy/glossary.json`
Term definitions for contextual help tooltips.
- **Schema per term:**
```json
{
  "term": "menstruum",
  "definition": "The liquid solvent or solvent mixture used to extract constituents from plant material. From Latin 'menstruum' (solvent). In tincture-making, the menstruum is typically a combination of ethanol and water, but can also include glycerin, vinegar, or oil depending on the preparation type.",
  "related_terms": ["marc", "maceration", "extraction_ratio"],
  "used_in_tools": ["menstruum_calc", "formula_builder"]
}
```
- **Build incrementally.** Generate terms relevant to whichever tools/data files we're working on this session.
- **Tone:** Clear, precise, no dumbing down, but accessible to someone who hasn't taken a pharmacognosy course.

---

## Output Requirements

1. **Output valid JSON.** I will be dropping your output directly into files. No trailing commas, no comments (JSON doesn't support them), proper escaping of special characters (especially in Unicode symbols like ℈, ʒ, ℥, ♏). Validate structure before outputting.

2. **Use the exact schema specified above.** Do not invent additional fields without asking. Do not omit specified fields — use `null` if data is unavailable.

3. **Cite your sources.** After the JSON output, include a brief "Sources Used" section listing what you referenced for each major data point. This is for my audit trail, not for the file.

4. **Flag uncertainty.** If unsure about a specific value, include `"confidence": "needs_review"` on that entry and note why after the JSON output. I'd rather review a flagged value than silently accept a wrong one.

5. **One file per session.** Don't generate multiple data files in one conversation. Exception: monographs.json and interactions.json can be co-generated for the same herb batch since the data overlaps.

6. **For herbs/monographs.json:** Work in batches of 5-10 herbs per session. I'll tell you which herbs at the bottom of this prompt.

7. **Wrap the JSON in a code block.** Makes it easy for me to copy-paste into the file.

## Let's Go

**Today's target file:** `[PASTE FILENAME HERE]`

**Additional context for this session (if any):** `[OPTIONAL: specific herbs for monograph batches, specific concerns, regional variants to prioritize, etc.]`

Generate the complete JSON file contents now.
