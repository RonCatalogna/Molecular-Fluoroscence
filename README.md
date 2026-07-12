# Molecular Fluorescence Code Repository

This repository contains the code used to process and analyze data from our molecular fluorescence experiment. Specifically, this project investigates the breakdown of the Beer-Lambert law at high concentrations due to the Inner Filter Effect (IFE). The code is open-source.

## fluorescence_analysis_P1.py:
It contains the data for the first part of the experiment. This script analyzes the relationship between fluorophore concentration and normalized fluorescence intensity.

### Usage Instructions

Data Formatting Requirements: To run the script successfully, your raw data must be organized in a specific format:

#### File Structure:
Provide three distinct Excel (.xlsx) files, one for each fluorescent material.

Sheet Naming: Within each file, create a separate sheet for every measured concentration. The sheet name must be the numerical value of that concentration.

Data Columns: In every sheet, the first two columns (A and B) must contain the Wavelength and Intensity data, respectively.

Exposure Time: Each sheet must contain the measurement's exposure time saved in cell  C2. The code can be changed to save it in any other consistent cell- except for cells in columns A & B. The value in this cell is crucial for normalizing the intensity across different measurements. 


Since the acquired data is discrete, standard analytical integration cannot be applied. Instead, the total fluorescence signal was calculated by numerical integration using the trapezoidal rule. This algorithm connects consecutive discrete measurement points with straight lines and sums the area of the resulting trapezoids. This method provides a highly reliable calculation of the total emission without making artificial assumptions about the underlying continuous function.
Following the calculation of the integrated area for each sample, the discrete data points were plotted. To accurately illustrate the continuous trend between these discrete measurements, Akima 1D interpolation was utilized rather than a classical Cubic Spline. Standard global splines optimize for overall curve smoothness. Consequently, fitting regions with abrupt trend changes often produces non physical overshoots or oscillations. The Akima algorithm, which is a local spline, calculates the curve based only on a localized neighborhood of data points. This ensures that the fitted curve remains strictly close to the experimental measurements, accurately representing the physical saturation and subsequent decay without introducing unjustified mathematical fluctuations.

### Execution and Output
Once your data is formatted and the file paths are updated in the configuration section:

Run the program and wait for a short processing time, the script will output a graph for all three fluorophores (Normalized Intensity VS Fluorophore Concentration).

The visualization will display the normalized experimental data points overlaid with a physically accurate, smooth trendline generated using Akima1DInterpolator.


