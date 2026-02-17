---
title: HerbCalc
emoji: 🌿
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 5.12.0
app_file: app.py
pinned: false
license: cc-by-4.0
---


# HerbCalc: Tools for Herbalists

**Free, open-source calculators and reference tools for learning herbal formulation.**

HerbCalc helps you go from "I have some dried herbs and a bottle of Everclear" to confidently formulating tinctures, glycerites, syrups, salves, and multi-herb extractions — with the math done correctly and the reasoning explained along the way.

---

### **▶ [Use HerbCalc Now](https://huggingface.co/spaces/jcourie/herbcalc)**

No download. No account. No installation. Just open the link and start using the tools.

---

## Who Is This For?

HerbCalc is built for **herbalism students, home herbalists, and anyone learning to make herbal preparations** who wants to get the math right without wrestling with a spreadsheet.

If you've ever stared at a monograph that says "1:5, 60% ethanol" and thought *"ok but how much Everclear and how much water do I actually pour?"* — this is for you.

It's also for instructors teaching herbal product design who want students to understand **why** the calculations work, not just get an answer.

HerbCalc is **not** a substitute for professional dispensary software, clinical decision-making, or medical advice. It is a learning tool.

## What Can I Do With It?

### Figure out how much of each liquid to mix for a tincture

The **Menstruum Calculator** is the core tool. Tell it how much herb you have, what extraction ratio you want, what alcohol you're working with, and what alcohol percentage you need in the final tincture. It tells you exactly how many milliliters of alcohol, water, and glycerin (if any) to measure out.

Defaults match the most common setup: 100g dried herb, 1:5 ratio, 95% Everclear, targeting 40% alcohol. Change any number and the output updates.

### Dilute alcohol to a target concentration

The **Pearson's Square** calculator handles the specific problem of "I have 95% Everclear and I need 60% alcohol — how much water do I add?" It also works in reverse: "I only have 80-proof vodka, what's the strongest tincture I can make at a 1:5 ratio?"

### Convert between measurement systems

Herbalism has a unit problem. Old books use apothecary drams and scruples. Your kitchen has teaspoons and cups. Your scale reads grams. Monographs from different traditions use completely different systems.

The **Unit Converter** translates between metric, US customary, apothecary, and household measurements — mass and volume. The **Apothecary Translator** focuses specifically on historical pharmacy units you encounter in older texts (grains, scruples, drams, minims), with notes explaining where the apothecary ounce diverges from the kitchen ounce (they're not the same — this causes real errors).

The **Pharmacy Shorthand Decoder** looks up Latin abbreviations like *aa* (of each), *q.s.* (sufficient quantity), and *gtt* (drops) that appear in formularies and older references.

### Understand which solvents extract what

Different plant constituents dissolve in different liquids. Alkaloids come out well in alcohol and vinegar. Polysaccharides need water. Resins need high-proof alcohol. Volatile oils need alcohol or oil, not water.

The **Solvent Affinity Reference** shows you which constituent classes are extracted well, moderately, or poorly by each solvent system — so you can understand *why* a monograph recommends 70% alcohol for one herb and 25% for another.

### Convert between percentage conventions

Herbal literature uses w/w (weight-in-weight), w/v (weight-in-volume), and v/v (volume-in-volume) interchangeably, often without specifying which one. The **Percentage Expression Translator** converts between all three with the density corrections that matter (ethanol is lighter than water — a "40% v/v" solution is not the same thing as "40% w/w").

### Calibrate your dropper

Drops are not a standardized unit. The **Drop Calibration** tool shows you approximately how many drops per milliliter you get for different dropper types and solvents, with honest confidence ranges. The pedagogical point: if precision matters, measure in milliliters, not drops.

### Build multi-herb formulas

The **Formula Builder** lets you combine multiple herbs, each with their own extraction ratio and alcohol percentage (pulled from monograph data when available), and calculates either a compromise menstruum for a combined extraction or individual extraction volumes for a blend-after-extraction approach. The **Dosage Scaler** converts "parts" notation into actual weights for a target bottle size.

### Calculate preparations beyond tinctures

The **Infusion/Decoction Calculator** handles water-based preparations: standard hot infusion, cold infusion, and decoction with reduction. The **Syrup Calculator** works out sugar-to-liquid ratios for simple and rich syrups, including honey substitution with density correction. The **Salve/Balm Calculator** tells you how much beeswax to add to your infused oil for the consistency you want.

### Check for herb-drug interactions

The **Interaction Checker** flags known and theoretical interactions between herbs and drug classes, with severity ratings, evidence levels, and mechanisms. It's a lookup tool for building the *habit* of checking, not a clinical database.

### Look up herb monograph data

The **Monograph Viewer** provides structured reference cards for commonly used herbs: botanical name, plant part, recommended extraction ratios and alcohol percentages, key constituent classes, dosage ranges, safety considerations, and energetic profiles.

### Generate batch records

The **Batch Log Generator** creates a formatted, printable record of your preparation: herb, source, lot number, weights, solvent volumes, dates, and notes. Even as a hobbyist, keeping batch records builds good practice habits.

### Figure out what you can make with what you have

The **Reverse Lookup** tool flips the question: instead of starting with a recipe, you tell it what solvents and equipment you have on hand, and it shows you which preparation types are feasible.

## Why Does It Explain the Math?

Most calculators give you a number. HerbCalc gives you a number **and tells you where it came from**.

Every tool has expandable "Learn More" sections that explain the underlying logic — why the metric system matters for herbal formulation, why you can't get 70% alcohol from vodka, why apothecary ounces and kitchen ounces are different, why drops are unreliable.

This is deliberate. The goal is not to create dependency on a calculator. The goal is for you to eventually understand the math well enough to do it on paper if you had to — and to use the calculator to save time and catch errors, not as a black box.

## Is the Data Reliable?

The calculation engine has been in use since 2016 and produces verified correct results. The unit conversion factors are from standard metrological references (NIST, SI definitions, Remington's Pharmaceutical Sciences). Solvent properties are from the CRC Handbook and USP. The ethanol-water density table is from the International Alcoholometric Tables.

Herb monograph data is compiled from published pharmacopeial sources (WHO Monographs, EMA/HMPC assessments, AHP, German Commission E) and cross-referenced against standard clinical references (Bone & Mills, Hoffmann, Mills & Bone). Interaction data draws from the Natural Medicines Comprehensive Database and Stockley's Herbal Medicines Interactions.

**However:** This is an educational tool maintained by one person, not a regulated clinical system. Always cross-reference with current authoritative sources for clinical decisions. The interaction checker is not comprehensive. Monograph data may not reflect the most recent research. If you find an error, please report it.

## A Note on the Metric System

HerbCalc thinks in metric internally. This isn't snobbery — it's because the metric system has a 1:1 relationship between mass and volume for water (1 gram = 1 milliliter), which makes herbal formulation math dramatically simpler and more precise. A 1:5 tincture ratio means 1 gram of herb to 5 milliliters of menstruum. Clean. Direct. No conversion factors.

If you're coming from imperial measurements, the Unit Converter will get you into metric, and the educational notes explain why it's worth the switch.

---

## Project Background

HerbCalc was developed by John at the [School of Integrative Health](https://soih.edu) (SOIH), where it grew out of a simple tincture calculator first written in 2016 for personal use. The original tool was a single PHP page that calculated menstruum volumes for hydroethanolic tinctures. It evolved through several iterations between 2016 and 2023, each adding features (custom extraction ratios, input validation, glycerin support, imperial-to-metric conversion) while keeping the core algorithm unchanged.

The current version is a ground-up rebuild as a multi-tool suite, designed to cover the full range of calculations and reference needs a student encounters from their first tincture to multi-herb formulation.

It is released under a **Creative Commons Attribution 4.0 International License** (CC BY 4.0) — free to use, share, and adapt with attribution.

---

## FAQ

**Do I need to install anything?**
No. Use the [web version on HuggingFace](https://huggingface.co/spaces/jcourie/herbcalc). It runs in your browser.

**Does it work on my phone?**
Yes. The interface is responsive. Some of the more complex tools (formula builder, batch log) are easier on a larger screen, but everything functions on mobile.

**Does it save my data?**
No. HerbCalc doesn't store any information you enter. Each session is independent. If you want to keep your results, use the batch log generator to create a printable record, or just screenshot.

**Can I use it without internet?**
Not the web version. If you need offline access, you can run it locally on your own computer (see Developer section below). Alternatively, use the batch log generator to print reference sheets before heading to the bench.

**I found a data error / I want to suggest a herb to add.**
Please open an issue on the [GitHub repository](https://github.com/johncourie/herbcalc/issues) or contact me directly. Corrections and additions are welcome — especially for monograph data and interaction flags.

**Can I use this for my own teaching?**
Absolutely. CC BY 4.0 means you can use, share, adapt, and build on it as long as you provide attribution. If you're teaching herbalism and want to integrate HerbCalc into your curriculum, go for it.

---

## For Developers

The rest of this README is for people who want to run HerbCalc locally, contribute to the codebase, or understand the architecture.

### Tech Stack

- **Python 3.10+** with **Gradio** for the web interface
- Static **JSON data files** — no database, no external API
- All computation is in Python; Gradio handles the UI
- Deployable to **HuggingFace Spaces** or any machine that runs Python

### Local Setup

```bash
git clone https://github.com/johncourie/herbcalc.git
cd herbcalc
pip install -r requirements.txt
python app.py
```

Opens at `http://localhost:7860`.

### Architecture

```
herbcalc/
├── app.py                  # Main Gradio app — assembles tool tabs
├── core/                   # Computation layer (no UI code)
│   ├── data_loader.py      # Loads JSON data at startup
│   ├── units.py            # Unit conversion engine
│   ├── solvents.py         # Menstruum, dilution, density calculations
│   ├── formulation.py      # Multi-herb formula logic
│   └── validation.py       # Input validation with pedagogical errors
├── tools/                  # UI layer — one module per tool tab
│   ├── menstruum_calc.py   # Each exports build_tab() -> gr.Tab
│   ├── unit_converter.py
│   └── ...
├── data/                   # Static JSON — single source of truth
│   ├── units/              # Conversion factors (metric, apothecary, etc.)
│   ├── solvents/           # Solvent properties, affinity matrix
│   ├── herbs/              # Monographs, interactions
│   ├── formulation/        # Preparation types, excipients
│   └── pedagogy/           # Glossary terms
└── tests/                  # pytest test suite for core/ modules
```

**Design principle:** No computation happens in `tools/` modules. They call `core/` functions and format the results for display. If you're adding a new calculation, it goes in `core/`. If you're adding a new UI, it goes in `tools/`.

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Contributing Data

The most valuable contributions are to the JSON data files, especially:
- **Herb monographs** (`data/herbs/monographs.json`) — adding new herbs or correcting existing entries
- **Interaction data** (`data/herbs/interactions.json`) — adding or updating herb-drug interaction flags
- **Glossary terms** (`data/pedagogy/glossary.json`) — expanding definitions

See `STATIC_DATA_MANIFEST.md` for the exact schema each file follows. See `DATA_GENERATION_PROMPT.md` for the template used to generate data with LLM assistance (useful if you want to batch-generate monograph entries for review).

All data contributions require source citations and are subject to expert review before merge.

### License

[CC BY 4.0 International](https://creativecommons.org/licenses/by/4.0/)
