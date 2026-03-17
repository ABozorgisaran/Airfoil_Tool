# Airfoil Analysis Tool

A Python-based aerodynamic analysis tool for evaluating airfoil geometry and predicting aerodynamic performance using an inviscid vortex panel method.

---

## Overview

This project provides a modular and extensible framework for analysing airfoil geometries using classical aerodynamic theory. It enables rapid evaluation of geometric properties and lift characteristics, making it suitable for preliminary aircraft design, UAV development, and aerodynamic studies.

The tool integrates with the **UIUC Airfoil Database**, allowing analysis of over 1600 airfoil geometries.

---

## Features

* Airfoil geometry processing from Selig-format `.dat` files
* Camber and thickness distribution computation
* Leading-edge radius estimation
* Inviscid vortex panel method solver
* Lift coefficient ((C_L)) and moment coefficient ((C_m)) calculation
* Pressure coefficient ((C_p)) distribution
* Command-line interface for fast analysis
* Support for large external airfoil datasets

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Airfoil_Tool.git
cd Airfoil_Tool
```

Install the package:

```bash
python -m pip install -e .
```

---

## Usage

### Geometry Analysis

```bash
airfoil-tool analyze data/examples/naca2412.dat
```

---

### Aerodynamic Polar

```bash
airfoil-tool polar data/examples/naca2412.dat --alpha-start -4 --alpha-end 10 --alpha-step 2
```

---

### Pressure Distribution

```bash
airfoil-tool plot-cp data/examples/naca2412.dat --alpha 4
```

---

## Airfoil Database

This project uses the **UIUC Airfoil Database (Selig format)**:

https://m-selig.ae.illinois.edu/ads/coord_seligFmt/

Due to the large size of the dataset, it is **not included in this repository**.

To use the full database:

1. Download the airfoil coordinate files from the link above
2. Extract the files
3. Place them into:

```text
data/uiuc/
```

Example:

```bash
airfoil-tool analyze data/uiuc/naca2412.dat
```

## Methodology

The aerodynamic solver is based on the **vortex panel method**, where the airfoil surface is discretised into panels with distributed vortex strength.

The governing condition is the flow tangency condition:

[
\vec{V} \cdot \vec{n} = 0
]

A linear system is solved to determine vortex strengths, from which surface velocity, pressure coefficient, and lift coefficient are obtained.

---

## Limitations

* Inviscid model (no viscosity or boundary layer effects)
* Does not predict drag accurately
* Not suitable for stall or separated flow analysis

This tool is intended for **preliminary design and comparative analysis**.

---

## Applications

* UAV and aircraft wing design
* Airfoil performance comparison
* Aerodynamics education
* Rapid prototyping and feasibility studies

---

## Future Work

* Viscous corrections and drag estimation
* Airfoil optimisation capabilities
* GUI-based interface
* Integration with CFD tools

---

## Author

**Alexander Bozorgisaran**
Aerospace Engineering Student

---

## License

This project is licensed under the MIT License.
