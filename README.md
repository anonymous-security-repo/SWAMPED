# WADE (WebAsssembly Anti-evasion Detection Evaluation)

# Project Overview

This repository contains tools for parsing and applying perturbation methods to WebAssembly binary files.

## Folder Structure

### `wasmParser`
- **`parser.py`**: Parses `.wast` files into individual sections.
- **`sectionStructure.py`**: Defines the structure and content of each section for recording purposes.

### `strategies`
- **`section_entry.py`**: Contains strategies related to section entries.
- **`function_code.py`**: Implements strategies for function code manipulations.

### `perturb.ipynb`
- Jupyter notebook that imports modules from the `strategies` folder.
- Includes test code to demonstrate and validate implemented perturbation methods.

## Usage
1. Use the `wasmParser` module to parse `.wast` files into sections.
2. Apply perturbation methods using `strategies` modules in the `perturb.ipynb` notebook.
3. Run the test code in `perturb.ipynb` to validate your modifications.
