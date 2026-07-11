# Molecular Fluorescence Code Repository

This repository contains the code used to process and analyze data from our molecular fluorescence experiment. Specifically, this project investigates the breakdown of the Beer-Lambert law at high concentrations due to the Inner Filter Effect (IFE). The code is open-source.

## fluorescence_analysis_P1.py:
It contains the data pfor the first part of the experiment. This script analyzes the relationship between fluorophore concentration and normalized fluorescence intensity.

### Usage Instructions

Data Formatting Requirements: To run the script successfully, your raw data must be organized in a specific format:

#### File Structure:
Provide three distinct Excel (.xlsx) files, one for each fluorescent material.

Sheet Naming: Within each file, create a separate sheet for every measured concentration. The sheet name must be the numerical value of that concentration.

Data Columns: In every sheet, the first two columns (A and B) must contain the Wavelength and Intensity data, respectively.

Exposure Time: Each sheet must contain the measurement's exposure time saved in cell  C2. The code can be changed to save it in any other consistent cell- except for cells in columns A & B. The value in this cell is crucial for normalizing the intensity across different measurements. 

### Execution and Output
Once your data is formatted and the file paths are updated in the configuration section:

Run the program and wait for a short processing time (up to 20-30 seconds), the script will output a graph for all three fluorophores (Normalized Intensity VS Fluorophore Concentration).

The visualization will display the normalized experimental data points overlaid with a physically accurate, smooth trendline generated using Akima1DInterpolator.
