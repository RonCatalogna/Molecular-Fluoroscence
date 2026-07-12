# Molecular Fluorescence Code Repository

This repository contains the code used to process and analyze data from our molecular fluorescence experiment. Specifically, this project investigates the breakdown of the Beer-Lambert law at high concentrations due to the Inner Filter Effect (IFE). The code is open-source.
---


## fluorescence_analysis_P1.py:
It contains the data for the first part of the experiment. This script analyzes the relationship between fluorophore concentration and normalized fluorescence intensity. The script automates the integration of spectral data, normalizes by exposure time and generates publication-quality plots comparing fluorescence intensity vs concentration for various fluorophores.

---

### Core Features

* **Automated Data Processing:** Parses multiple Excel files containing spectral data, normalizes raw intensity signals by exposure time, and integrates spectral peaks using the Trapezoidal rule.
* **Intelligent Filtering:** Automatically cleans noisy data and applies spectral masking to focus on the relevant fluorescence emission range.
* **Advanced Visualization:** * **Akima Interpolation:** Uses Akima splines to create smooth, accurate curves between experimental data points.
* **Custom Styling:** Automatically applies specific color schemes, markers, and line styles based on the material type.


* **Data Quality Control:** Allows manual rejection of specific data points, visually highlighting them as outliers in the final plot.

---

### Workflow

1. **Initialization:** Defines a dictionary of source files and mapping configurations for each material (Fluorescein, Rhodamine B, Rhodamine 6G).
2. **Spectral Integration:** The `integrating_data` function calculates the area under the curve for each spectrum, normalized by the exposure time retrieved from the file data.
3. **Data Fitting:** Applies Akima interpolation to the filtered experimental data to create smooth continuous curves.
4. **Plotting:** the intensity-vs-concentration curves, combining experimental markers with the interpolated trend lines.

---

### Requirements

To run this script, ensure you have the following dependencies installed:

`pip install pandas numpy matplotlib scipy openpyxl`

---

### Usage

1. **Prepare your data:** Data Formatting Requirements:
To run the script successfully, your raw data must be organized in a specific format:
Provide three distinct Excel (.xlsx) files, one for each fluorescent material.
Sheet Naming: Within each file, create a separate sheet for every measured concentration. The sheet name must be the numerical value of that concentration.
Data Columns: In every sheet, the first two columns (A and B) must contain the Wavelength and Intensity data, respectively.

Exposure Time: Each sheet must contain the measurement's exposure time saved in cell  C2. The code can be changed to save it in any other consistent cell- except for cells in columns A & B. The value in this cell is crucial for normalizing the intensity across different measurements. 

2. **Configuration:** * Update the `files` dictionary with your specific filenames.
* Use the `rejected_points` dictionary to flag any anomalous data points that should not be included.

Since the acquired data is discrete, standard analytical integration cannot be applied. Instead, the total fluorescence signal was calculated by numerical integration using the trapezoidal rule. This algorithm connects consecutive discrete measurement points with straight lines and sums the area of the resulting trapezoids. This method provides a highly reliable calculation of the total emission without making artificial assumptions about the underlying continuous function.
Following the calculation of the integrated area for each sample, the discrete data points were plotted. To accurately illustrate the continuous trend between these discrete measurements, Akima 1D interpolation was utilized rather than a classical Cubic Spline. Standard global splines optimize for overall curve smoothness. Consequently, fitting regions with abrupt trend changes often produces non physical overshoots or oscillations. The Akima algorithm, which is a local spline, calculates the curve based only on a localized neighborhood of data points. This ensures that the fitted curve remains strictly close to the experimental measurements, accurately representing the physical saturation and subsequent decay without introducing unjustified mathematical fluctuations.

### Execution and Output
Once your data is formatted and the file paths are updated in the configuration section:
Run the program and wait for a short processing time, the script will output a graph for all three fluorophores (Normalized Intensity VS Fluorophore Concentration). Overall: the visualization will display the normalized experimental data points overlaid with a physically accurate, smooth trendline generated using Akima1DInterpolator.

## fluorescence_analysis_P2.py:

This repository contains a robust Python automation tool designed to analyze fluorescence intensity profiles from experimental imaging data. The tool calculates the attenuation coefficient ($\alpha$) for various fluorophores across multiple concentrations by performing spatial calibration and intensity decay analysis.

### Features

* **Interactive Calibration:** Automatically calculates pixel-to-cm scale factors based on user-defined reference points.
* **Automated ROI Processing:** Extracts intensity profiles along a specified beam path, averaging across a defined window to minimize noise.
* **Physics-Based Analysis:** Calculates the $1/e$ decay length and the attenuation coefficient ($\alpha$) based on the Beer-Lambert law.
* **Verification Workflow:** Generates side-by-side visual confirmations for every processed image, overlaying calculated peak and decay points directly onto the intensity map.
* **Batch Processing:** Iterates through folders of image files, organizing results into a structured dataset for final analysis.

### Workflow

### 1. Inputs
* **Images:** A set of `.jpg` files named by material and concentration (e.g., `FE (1).jpg`).
* **User Interaction:**
* **Step 1:** Select two points on the container to define the 10 cm reference length.
* **Step 2:** Select two points to define the Region of Interest (ROI) along the fluorescence beam.

### 2. Processing
The script performs:
1. **Spatial Mapping:** Translates pixel coordinates to physical distances.
2. **Signal Extraction:** Calculates the average intensity profile within the ROI.
3. **Decay Analysis:** Locates the peak intensity ($I_0$) and determines the distance at which intensity drops to $I_0/e$.
4. **Parameter Calculation:** Derives $\alpha$ (in $\text{cm}^{-1}$) using the relationship $\alpha = 1/x_{1/e}$.

### 3. Outputs
* **Visual Verification:** A generated report for each image displaying the intensity profile graph and the mapped intensity spectrum image with marked data points.
* **Numerical Results:** A console-printed summary and an integrated dataframe containing:
* `Material`
* `Concentration Index`
* `Distance_1e_cm`
* `Alpha_cm_inv`

## Requirements
* `numpy`
* `pandas`
* `matplotlib`
* `scipy`

## Usage
1. Place your data images in the working directory.
2. Ensure your Excel datasheet (`RESULTS_MF_PT2_DATASHEET.xlsx`) is configured with the required columns.
3. Run the script: `python fluorescence_analysis.py`.
4. Follow the interactive prompts to calibrate and select ROIs for each image.
