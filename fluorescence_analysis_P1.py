# All libraries needed:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.interpolate import Akima1DInterpolator
from scipy.signal import savgol_filter  # Added for noise filtering

# Files- Names and type-.xlsx
files = {
    "Fluorescein": "LAB C MF Part 1 FE.xlsx",
    "Rhodamine B": "LAB C MF Part 1 RB.xlsx",
    "Rhodamine 6G": "LAB C MF Part 1 R6G.xlsx"
}

save_exposure_time = "C2"  # Cell saving data of exposure time for normalization

rejected_points = {
    "Fluorescein": [],
    "Rhodamine B": [],
    "Rhodamine 6G": []
}

# Samples' colors and linestyles according to the colors in the experiment
style_config = {
    "Fluorescein": {"color": "#FFD700", "marker": "o", "linestyle": "-"},   # Yellow
    "Rhodamine B": {"color": "#FF69B4", "marker": "s", "linestyle": "--"},  # Pink
    "Rhodamine 6G": {"color": "#FF8C00", "marker": "D", "linestyle": "-."}  # Orange
}

# Utilities
def cell_to_indices(cell):
    col = ord(cell[0].upper()) - ord('A')
    row = int(cell[1:]) - 1
    return row, col


exposure_row, exposure_col = cell_to_indices(save_exposure_time)

# Data processing
def integrating_data(filename, sheet, exposure_row, exposure_col): # Integration function
    df_raw = pd.read_excel(filename, sheet_name=sheet, header=None)

    # Normalizing by exposure time
    exposureTime = df_raw.iat[exposure_row, exposure_col] * 10

    df = pd.read_excel(filename, sheet_name=sheet, header=1)
    wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce")

    # Clean data
    DATA_notNA = wavelength.notna() & intensity.notna()
    wavelength = wavelength[DATA_notNA]
    intensity = intensity[DATA_notNA]

    # Spectral filtering mask (above 470nm)
    masking = wavelength >= 470
    wavelength = wavelength[masking]
    intensity = intensity[masking]

    # Smooth the intensity to avoid finding noise spikes as peaks
    # window_length must be an odd number. polyorder=3 preserves peak shape.
    window_size = 15
    if len(intensity) >= window_size:
        smoothed_intensity = savgol_filter(intensity.values, window_length=window_size, polyorder=3)
        peak_wavelength = wavelength.values[np.argmax(smoothed_intensity)]
    else:
        # Fallback in case data is extremely sparse
        peak_wavelength = wavelength.values[np.argmax(intensity.values)]

    return np.trapezoid(intensity, wavelength) / exposureTime, peak_wavelength


def data_process_RawData(filename):
    xls = pd.ExcelFile(filename)
    Con, Int, Peak_WL = [], [], []
    for sheet in xls.sheet_names:
        Int_i, peak_wl_i = integrating_data(filename, sheet, exposure_row, exposure_col)
        Con.append(float(sheet))
        Int.append(Int_i)
        Peak_WL.append(peak_wl_i)

    Con, Int, Peak_WL = np.array(Con), np.array(Int), np.array(Peak_WL)
    sorting = np.argsort(Con)
    return Con[sorting], Int[sorting], Peak_WL[sorting]

# Plots
plt.rcParams['font.size'] = 11
fig_main, ax_main = plt.subplots(figsize=(9, 6))

print("=== Peak Wavelength Analysis ===")

for material, file in files.items():
    # Load and process raw data
    Concentration_all, Intensity_all, Peak_WL_all = data_process_RawData(file)

    # Print the peak wavelength results for each concentration and their average
    print(f"\n{material}:")
    for c, wl in zip(Concentration_all, Peak_WL_all):
        print(f"  Concentration {c} mM -> Peak Wavelength: {wl:.2f} nm")
    avg_wl = np.mean(Peak_WL_all)
    print(f"  --> Average Peak Wavelength: {avg_wl:.2f} nm")

    reject = np.isin(Concentration_all, rejected_points.get(material, []))

    Concentration_fit = Concentration_all[~reject]
    Intensity_fit = Intensity_all[~reject]

    # Akima interpolation
    if len(Concentration_fit) > 1:
        Concentration_smooth = np.linspace(Concentration_fit.min(), Concentration_fit.max(), 300)
        akima_func = Akima1DInterpolator(Concentration_fit, Intensity_fit)
        Intensity_smooth = akima_func(Concentration_smooth) # Generate smooth x-values and apply Akima interpolation
    else:
        Concentration_smooth = Concentration_fit
        Intensity_smooth = Intensity_fit

    # Retrieve material-specific styling
    style = style_config.get(material, {"color": None, "marker": "o", "linestyle": "-"})

    # Plot interpolated curve
    ax_main.plot(
        Concentration_smooth, Intensity_smooth,
        linestyle=style["linestyle"],
        linewidth=3.0,
        color=style["color"]
    )

    # Plot raw experimental data pts
    ax_main.plot(
        Concentration_fit, Intensity_fit,
        marker=style["marker"],
        linestyle='',
        markersize=7,
        color=style["color"],
        markeredgecolor='black',
        markeredgewidth=0.8,
        label=f"{material}"
    )

    if np.any(reject): # Highlight manually rejected data points with a red circle, if any exist
        ax_main.scatter(
            Concentration_all[reject], Intensity_all[reject],
            facecolors='none',
            edgecolors='red',
            s=80,
            linewidths=1.5,
            label=f"{material} (Rejected)"
        )

# Final formatting
ax_main.set_xlabel("Concentration (mM)", fontweight='bold', fontsize=16)
ax_main.set_ylabel("Normalized Intensity (Arb. Units)", fontweight='bold', fontsize=16)
ax_main.set_title("Fluorescence Intensity vs. Concentration", pad=60, fontsize=25, fontweight='bold')

ax_main.grid(True, which='major', linestyle='--', alpha=0.6)
ax_main.minorticks_on()
ax_main.grid(True, which='minor', linestyle=':', alpha=0.3)

legend_handles = []
for material, style in style_config.items():
    handle = Line2D([0], [0],
                    color=style["color"],
                    marker=style["marker"],
                    linestyle=style["linestyle"],
                    linewidth=3.0,
                    markersize=7,
                    markeredgecolor='black',
                    markeredgewidth=0.8,
                    label=material)
    legend_handles.append(handle)

ax_main.legend(
    handles=legend_handles,
    loc='lower center',
    bbox_to_anchor=(0.5, 1.05),
    ncol=3,
    frameon=True,
    edgecolor='black',
    facecolor='white',
    fancybox=True,
    handlelength=5.0,
    handletextpad=1.0,
    fontsize=13
)

fig_main.tight_layout(rect=[0, 0, 1, 0.83])

plt.show()