# Static Data Generation Manifest

This document lists every data file the HerbCalc toolkit requires, what goes in it, where to source it, and the level of effort involved.

All data files are static JSON loaded at application startup by `core/data_loader.py` into Python dicts. They are consumed by the `core/` computation modules and `tools/` UI modules. No data is fetched at runtime — everything is in memory after startup.

**Filename convention:** Underscores, not hyphens (matches Python import conventions). All filenames lowercase.

---

## Tier 1: Math Constants (Generate Immediately — Prerequisite for Everything)

These are fixed conversion factors. No editorial judgment needed. Can be compiled from standard references in an afternoon.

### `data/units/metric.json`
**Contents:** SI unit conversion factors for mass and volume. Base units: gram (mass), milliliter (volume). All entries expressed as multiplier to base unit.
**Scope:**
- Mass: microgram, milligram, centigram, decigram, gram, decagram, hectogram, kilogram
- Volume: microliter, milliliter, centiliter, deciliter, liter
**Schema per entry:**
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
**Note on `aliases`:** The `aliases` array is used by `core/units.py` to build the flat lookup registry. Include common abbreviations, plural forms, and any shorthand students might type. This field appears on all unit entries across all unit files.
**Sources:** SI definitional. No ambiguity.
**Effort:** Trivial. ~12 entries.

---

### `data/units/avoirdupois.json`
**Contents:** US/UK customary mass units → grams.
**Scope:**
- Grain (av): 0.06479891 g
- Dram (av): 1.7718452 g (= 27.344 grains)
- Ounce (av): 28.349523 g (= 16 drams = 437.5 grains)
- Pound (av): 453.59237 g (= 16 ounces = 7000 grains)
- Stone: 6350.29318 g (= 14 pounds)
- Hundredweight (short): 45359.237 g (= 100 pounds)
- Ton (short): 907184.74 g (= 2000 pounds)
**Schema:** Same as metric.json, with added `"equivalence"` field showing inter-unit relationships.
**Key metadata to embed as top-level `"notes"`:** Avoirdupois grain = apothecary grain (same: 64.79891 mg). Systems diverge at dram/ounce/pound.
**Sources:** NIST Handbook 44.
**Effort:** Trivial. ~7 entries.

---

### `data/units/apothecary.json`
**Contents:** Full apothecary system, mass and volume, with Unicode symbols and inter-unit equivalences.
**Mass:**
- Grain (gr): 0.06479891 g (same as avoirdupois)
- Scruple (℈): 1.2959782 g = 20 grains
- Dram apothecary (ʒ): 3.8879346 g = 3 scruples = 60 grains
- Ounce apothecary (℥): 31.1034768 g = 8 drams = 480 grains
- Pound apothecary (lb ap): 373.2417216 g = 12 ounces = 5760 grains
**Volume:**
- Minim (♏ or min): 0.06161152 mL
- Fluid scruple: 1.2322304 mL = 20 minims
- Fluid dram (ƒʒ): 3.6966912 mL = 60 minims = 3 fluid scruples
- Fluid ounce apothecary (ƒ℥): 29.5735296 mL = 8 fluid drams = 480 minims
- Pint apothecary (O): 473.176473 mL = 16 fluid ounces
- Gallon apothecary (C): 3785.41178 mL = 8 pints
**Schema per entry:**
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
**Required top-level `"disambiguation_notes"` array:**
```json
"disambiguation_notes": [
  {
    "issue": "ounce",
    "apothecary": "31.1035 g (480 grains, symbol ℥)",
    "avoirdupois": "28.3495 g (437.5 grains, symbol oz)",
    "difference_pct": 9.7,
    "note": "Apothecary ounce is ~10% heavier. Using the wrong ounce in a formula can cause clinically significant dosing errors."
  },
  {
    "issue": "pound",
    "apothecary": "373.24 g (12 ounces, 5760 grains)",
    "avoirdupois": "453.59 g (16 ounces, 7000 grains)",
    "difference_pct": 21.5,
    "note": "Apothecary pound has 12 ounces; avoirdupois has 16. A 'pound' of herb means very different things depending on system."
  },
  {
    "issue": "dram",
    "apothecary": "3.888 g (60 grains)",
    "avoirdupois": "1.772 g (27.344 grains)",
    "difference_pct": 119.4,
    "note": "Apothecary dram is more than double the avoirdupois dram. This is the most dangerous unit confusion."
  },
  {
    "issue": "grain",
    "note": "Grain is the SAME in both systems: 64.79891 mg. This is the one unit that does not diverge."
  }
]
```
**Sources:** Remington's Pharmaceutical Sciences, USP historical appendices, British Pharmacopoeia.
**Effort:** Small. ~12 entries + disambiguation array.

---

### `data/units/household.json`
**Contents:** Kitchen/household volume measures → mL. US defaults with regional variants noted.
**Scope:**
- Drop: ~0.05 mL (FLAGGED: highly variable)
- Smidgen: ~0.12 mL
- Pinch: ~0.36 mL
- Dash: ~0.62 mL
- Teaspoon: 4.92892 mL
- Dessertspoon: 9.85784 mL (2 tsp, UK/AU)
- Tablespoon: 14.78676 mL (US); AU = 20mL
- Fluid ounce: 29.5735 mL (US)
- Cup: 236.588 mL (US); metric = 250mL; Imperial = 284.131mL
- Pint: 473.176 mL (US); Imperial = 568.261mL
- Quart: 946.353 mL (US)
- Gallon: 3785.41 mL (US); Imperial = 4546.09mL
- Dropperful: ~0.75 mL (FLAGGED: range 0.5–1.0, variable by dropper geometry)
**Schema per entry:** Same base schema plus:
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
**The `precise` flag** is consumed by `core/units.py` to append warnings to ConversionResult when imprecise units are involved.
**Sources:** NIST, USDA, FDA labeling guidelines.
**Effort:** Small. ~15 entries + regional variants.

---

### `data/units/historical.json`
**Contents:** Non-Western and historical measurement systems encountered in herbal/medical literature.
**Chinese/TCM — Modern standardized (post-1949):**
- Jīn (斤): 500g (market jin)
- Liǎng (两): 50g (= 1/10 jin, note: modern market liang)
- Qián (钱): 5g (= 1/10 liang)
- Fēn (分): 0.5g (= 1/10 qian)
**Chinese/TCM — Classical (flag as variable):**
- Han dynasty liang: ~15.6g (Zhang Zhongjing era)
- Song dynasty liang: ~40g
- Ming/Qing liang: ~37.3g
**Ayurvedic:**
- Tola (tolā): 11.66g
- Masha (māsha): 0.97g (≈ 1g, = 1/12 tola)
- Ratti (raktikā): 0.12g (= 1/8 masha)
- Pala: 46.64g (= 4 tola)
- Karsha: 11.66g (= 1 tola, synonymous)
- Kudava: 186.56g
**Unani:**
- Mithqal: 4.68g (varies 4.25–5.0g by region)
- Dirham: 3.12g
**Schema per entry:**
```json
{
  "unit_name": "liang_modern",
  "symbol": "两",
  "system": "tcm_modern",
  "type": "mass",
  "to_base": 50.0,
  "base_unit": "gram",
  "era": "post-1949 standardized",
  "region": "China",
  "confidence": "standardized",
  "historical_note": "Classical Han dynasty liang ≈ 15.6g, not modern 50g. Do not convert classical text doses using modern values without scholarly context.",
  "aliases": ["liang", "两", "tael"]
}
```
**Confidence levels:** `"standardized"` (modern official), `"approximate"` (generally agreed), `"variable"` (changed over time/region)
**All entries carry a top-level warning:**
```json
"system_warning": "Historical units varied by region and era. Use for interpretive reference, not precision formulation. Always verify against the specific text and historical context."
```
**Sources:** WHO Traditional Medicine references, Bensky's Materia Medica, Dash & Sharma, academic pharmacognosy.
**Effort:** Medium. Research-intensive for accuracy. ~25 entries with contextual notes.

---

### `data/units/pharmacy_abbrev.json`
**Contents:** Latin/Rx abbreviations and symbols used in historical and modern pharmacy notation. This is a decoder/lookup reference, not a conversion table.
**Categories:**
- **Quantity/Measurement:** aa, q.s., q.s. ad, ad, ss, gt/gtt, ℥, ƒ℥, ʒ, ♏, ℈, M, ft, No.
- **Frequency/Timing:** b.i.d., t.i.d., q.i.d., p.r.n., h.s., a.c., p.c., q.h. (every hour), q.4h. (every 4 hours), stat (immediately)
- **Form/Preparation:** caps, elix, fl/fld, pulv, syr, tr/tinct, ung, lot (lotion), garg (gargle), inf (infusion), dec (decoction), emuls (emulsion)
- **Instructions:** Sig. (signa — write on label), Disp. (dispense), Rx (recipe — take), c̄ (cum — with), s̄ (sine — without), ā (ante — before), p̄ (post — after)
**Schema per entry:**
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
**Top-level `"roman_numeral_convention"` note:**
```json
"roman_numeral_convention": {
  "description": "Quantities written as lowercase Roman numerals after unit symbol",
  "examples": ["℥iv = 4 ounces", "gr x = 10 grains", "gtt iii = 3 drops", "℥ss = half an ounce"],
  "values": { "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10, "xii": 12, "xv": 15, "xx": 20, "xxx": 30 }
}
```
**Sources:** Remington's, any dispensing pharmacy textbook.
**Effort:** Small-medium. ~60 entries.

---

## Tier 2: Solvent & Material Properties (Generate Early — Required for Calculators)

These require some judgment calls about what to include, but the underlying data is well-established.

### `data/solvents/solvents.json`
**Contents:** Physical and extraction properties of solvents used in herbal preparation.
**Solvents to include:** ethanol, water, glycerin, acetic_acid, olive_oil, coconut_oil, jojoba_oil, sweet_almond_oil, grapeseed_oil, sunflower_oil, sesame_oil, honey
**Schema per solvent:**
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
**Critical sub-dataset — top-level key `"ethanol_water_density_table"`:**
Density of ethanol-water mixtures at 20°C, every 5% v/v from 0–100%. This is the single most important reference table for w/v ↔ v/v conversions. Used by `core/solvents.py:lookup_ethanol_density()` with linear interpolation between points.
```json
"ethanol_water_density_table": [
  { "ethanol_pct_vv": 0, "density_g_ml": 1.0000 },
  { "ethanol_pct_vv": 5, "density_g_ml": 0.9900 },
  { "ethanol_pct_vv": 10, "density_g_ml": 0.9819 },
  { "ethanol_pct_vv": 15, "density_g_ml": 0.9752 },
  { "ethanol_pct_vv": 20, "density_g_ml": 0.9687 },
  { "ethanol_pct_vv": 25, "density_g_ml": 0.9617 },
  { "ethanol_pct_vv": 30, "density_g_ml": 0.9539 },
  { "ethanol_pct_vv": 35, "density_g_ml": 0.9449 },
  { "ethanol_pct_vv": 40, "density_g_ml": 0.9352 },
  { "ethanol_pct_vv": 45, "density_g_ml": 0.9247 },
  { "ethanol_pct_vv": 50, "density_g_ml": 0.9138 },
  { "ethanol_pct_vv": 55, "density_g_ml": 0.9026 },
  { "ethanol_pct_vv": 60, "density_g_ml": 0.8911 },
  { "ethanol_pct_vv": 65, "density_g_ml": 0.8795 },
  { "ethanol_pct_vv": 70, "density_g_ml": 0.8676 },
  { "ethanol_pct_vv": 75, "density_g_ml": 0.8556 },
  { "ethanol_pct_vv": 80, "density_g_ml": 0.8436 },
  { "ethanol_pct_vv": 85, "density_g_ml": 0.8312 },
  { "ethanol_pct_vv": 90, "density_g_ml": 0.8180 },
  { "ethanol_pct_vv": 95, "density_g_ml": 0.8029 },
  { "ethanol_pct_vv": 100, "density_g_ml": 0.7893 }
]
```
**Sources:** CRC Handbook of Chemistry and Physics, Merck Index, OIML R 22, USP/NF excipient monographs.
**Effort:** Medium. ~12 solvent entries + density table.

---

### `data/solvents/affinity_matrix.json`
**Contents:** Constituent class × solvent extraction efficiency matrix.
**Constituent classes (rows):**
1. alkaloids
2. flavonoids
3. tannins_hydrolyzable
4. tannins_condensed
5. saponins
6. volatile_oils
7. fixed_oils
8. polysaccharides
9. minerals
10. resins
11. glycosides_cardiac
12. glycosides_anthraquinone
13. glycosides_cyanogenic
14. mucilage
15. bitter_compounds (sesquiterpene lactones, iridoids)
16. phenolic_acids
17. coumarins
18. lignans

**Solvent categories (columns):**
- ethanol_high (>60%)
- ethanol_medium (40–60%)
- ethanol_low (20–40%)
- water_hot
- water_cold
- glycerin
- acetic_acid
- fixed_oil

**Efficiency ratings:** `"good"`, `"moderate"`, `"poor"`, `"none"`, `"variable"` (with explanatory note)

**Schema per entry:**
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
  "notes": "Extraction depends on salt form vs free base. Acidic solvents (vinegar) convert alkaloids to salts, improving aqueous solubility. Some alkaloids (e.g., berberine) are water-soluble as salts."
}
```
**This file requires expert review before finalization.** Flag uncertain ratings with `"confidence": "needs_review"`.
**Sources:** Trease & Evans Pharmacognosy, Bruneton Pharmacognosy Phytochemistry Medicinal Plants, Bone & Mills Principles and Practice of Phytotherapy.
**Effort:** Medium-high. ~18 rows × 8 columns = ~144 cells + notes. Most editorially demanding Tier 2 file.

---

### `data/formulation/excipients.json`
**Contents:** Non-solvent formulation ingredients for topicals and syrups.
**Materials:** beeswax, candelilla_wax, shea_butter, cocoa_butter, mango_butter, lanolin, emulsifying_wax, stearic_acid, vitamin_e_tocopherol, benzoin_tincture, rosemary_oleoresin_extract, sucrose
**Schema per material:**
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
  "vegan_alternative": { "name": "candelilla wax", "ratio_adjustment": "use approximately half the amount", "notes": "Higher melting point (68-73°C), harder result" },
  "safety": "Generally safe. Rare contact allergy possible.",
  "sourcing_notes": "Cosmetic-grade or food-grade. Yellow (unfiltered) retains some propolis and aroma. White (filtered) is neutral.",
  "notes": "Standard thickener for oil-based preparations."
}
```
**Sources:** Formulary references, Poucher's Perfumes Cosmetics and Soaps, cosmetic chemistry references.
**Effort:** Small-medium. ~12 entries.

---

### `data/formulation/preparation_types.json`
**Contents:** Parameters and defaults for each preparation type the toolkit supports.
**Preparations:** tincture, glycerite, acetum, oxymel, standard_infusion, cold_infusion, decoction, simple_syrup, rich_syrup, herbal_syrup, oil_infusion_cold, oil_infusion_hot, salve, balm, lip_balm, poultice, compress, electuary, capsule, pastille
**Schema per preparation:**
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
  "pedagogical_notes": "The standard starting point for herbal extraction. Most herbs have published tincture ratios and alcohol percentages in monograph literature."
}
```
**The `required_solvents` and `calculator_tool` fields** enable the reverse lookup tool ("What can I make?") to filter by available materials and link to the appropriate calculator.
**Sources:** Easley & Horne Making Plant Medicine, Green The Herbal Medicine-Maker's Handbook, Gladstar Medicinal Herbs, Hardin Herbal Medicine From the Heart of the Earth.
**Effort:** Medium. ~20 preparation types, each with 8-12 fields.

---

## Tier 3: Herb Data (Most Labor-Intensive — Built Incrementally)

### `data/herbs/monographs.json`
**Contents:** Structured monograph data per herb. Full schema in claude.md.
**Initial target:** 50 herbs. Build in batches of 5-10 per LLM session using DATA_GENERATION_PROMPT.md.

**Priority list (most commonly taught in introductory curricula):**

**Nervines/Sedatives:** Valerian, Passionflower, Skullcap, Chamomile, Lemon balm, Hops, Lavender, California poppy, Kava
**Adaptogens:** Ashwagandha, Eleuthero, Rhodiola, Holy basil (Tulsi), Astragalus, Schisandra, Reishi
**Digestives/Bitters:** Ginger, Peppermint, Fennel, Dandelion, Gentian, Artichoke leaf, Marshmallow, Slippery elm, Meadowsweet
**Respiratory:** Elderberry/flower, Mullein, Thyme, Elecampane, Osha
**Immune:** Echinacea (angustifolia + purpurea), Andrographis, Elderberry
**Anti-inflammatory:** Turmeric, Willow bark, Meadowsweet, Calendula, Arnica (topical only)
**Liver/Detox:** Milk thistle, Dandelion root, Burdock, Yellow dock, Schisandra
**Urinary:** Cranberry, Uva ursi, Corn silk, Nettle leaf
**Women's health:** Vitex, Dong quai, Black cohosh, Red raspberry leaf, Cramp bark
**Cardiovascular:** Hawthorn, Garlic, Motherwort, Linden
**Topical/Wound:** Calendula, Comfrey (external), Plantain, St. John's wort, Yarrow

(Deduplicate to ~50 unique entries.)

**Per-herb fields required:** See full schema in claude.md. The most time-consuming parts:
- `key_constituents` (requires current pharmacognosy literature)
- `extraction` parameters (ratio, alcohol %, per-preparation suitability)
- `safety` (interactions, contraindications, pregnancy/lactation status)
- `energetics` (taste, temperature, moisture — TCM and Ayurvedic correspondences)

**Source requirement:** Cross-reference minimum 2 per herb from: WHO Monographs, EMA/HMPC assessments, AHP monographs, German Commission E, Bone & Mills, Hoffmann, PDR for Herbal Medicines, Mills & Bone Essential Guide to Herbal Safety.
**Effort:** HIGH. 30-60 min per herb for thorough data entry = 25-50 hours for 50 herbs. Can release with 20 and add incrementally.

---

### `data/herbs/interactions.json`
**Contents:** Herb-drug interaction data. One entry per herb with known or theoretical interactions.
**Work in parallel with monographs.json** — same herb batches.
**Schema per herb:**
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
  "general_notes": "Potent CYP3A4 and P-glycoprotein inducer. Affects metabolism of ~50% of pharmaceutical drugs. The single most interaction-prone herb in common use."
}
```
**Severity scale:** `"major"` / `"moderate"` / `"minor"` / `"theoretical"`
**Evidence scale:** `"clinical_trials"` / `"clinical_reports"` / `"in_vitro"` / `"traditional_caution"` / `"theoretical"`
**The `cyp_interactions` object** is optional per herb but critical for St. John's wort, Echinacea, Ginkgo, Garlic, Goldenseal, Kava, and any herb with documented CYP450 activity. Enables a future "check this formula against CYP pathways" tool.
**Sources:** Natural Medicines Comprehensive Database, Stockley's Herbal Medicines Interactions, EMA assessments, Mills & Bone Essential Guide to Herbal Safety.
**Effort:** HIGH. Parallel to monograph work. ~2-4 interactions per herb average.

---

## Tier 4: Pedagogical Content (Build Alongside Tools)

### `data/pedagogy/glossary.json`
**Contents:** Term definitions for contextual help throughout the UI.
**Schema per term:**
```json
{
  "term": "menstruum",
  "definition": "The liquid solvent or solvent mixture used to extract constituents from plant material. From Latin 'menstruum' (solvent). In tincture-making, the menstruum is typically a combination of ethanol and water, but can also include glycerin, vinegar, or oil depending on the preparation type.",
  "related_terms": ["marc", "maceration", "extraction_ratio"],
  "used_in_tools": ["menstruum_calc", "formula_builder"]
}
```
**Build incrementally.** Generate terms relevant to whichever tools/data files are in the current development sprint.
**Tone:** Clear, precise, accessible without condescension. Same register as Conversion.php's existing expandable sections.
**Effort:** Low-medium. Ongoing. Target ~100-150 terms at full build.

---

## Generation Priority Summary

| Priority | Files | Effort | Blocks |
|---|---|---|---|
| **Do first** | metric.json, avoirdupois.json, apothecary.json, household.json, pharmacy_abbrev.json | 1-2 days | `core/units.py`, all unit converter tools |
| **Do second** | solvents.json (incl. ethanol density table), affinity_matrix.json | 2-3 days | `core/solvents.py`, menstruum calc, Pearson's square, percentage translator, solvent affinity viewer |
| **Do third** | preparation_types.json, excipients.json | 1-2 days | Preparation-specific calculators, reverse lookup |
| **Do fourth** | historical.json | 1-2 days (research) | Apothecary/historical translator |
| **Build incrementally** | monographs.json, interactions.json | 25-50 hours | Monograph viewer, formula builder, interaction checker |
| **Build alongside** | glossary.json | Ongoing | Contextual help in all tools |

---

## Notes on Data Authorship

**Tier 1-2** data is factual/mathematical — compilable by anyone with the right references, suitable for LLM-assisted generation with spot-checking.

**Tier 3** herb data requires herbalism domain expertise. The extraction parameters, energetics, interaction severity judgments, and safety flags need a human herbalist with pharmacovigilance training. LLMs can scaffold the JSON structure and pre-populate from published sources, but editorial review on clinical data is non-negotiable.

**The affinity matrix** (Tier 2) sits in between — the data is published but the editorial judgment about what constitutes "good" vs "moderate" extraction for a given constituent-solvent pair involves interpretation. Flag for review.

**Use `DATA_GENERATION_PROMPT.md`** for all LLM-assisted data generation sessions. It contains the full schema specs and instructions for each file.
