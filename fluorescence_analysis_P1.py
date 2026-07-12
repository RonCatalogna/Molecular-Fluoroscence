#All libraries needed:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.interpolate import Akima1DInterpolator

# Files- Names and type-.xlsx
files = {
    "Fluorescein": "LAB C MF Part 1 FE.xlsx",
    "Rhodamine B": "LAB C MF Part 1 RB.xlsx",
    "Rhodamine 6G": "LAB C MF Part 1 R6G.xlsx"
}

EXPOSURE_CELL = "C2"  # Cell containing exposure time for normalization

excluded_points = {
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


exp_row, exp_col = cell_to_indices(EXPOSURE_CELL)

# Data processing
def integrate_sheet(filename, sheet, exp_row, exp_col): #Integration function
    df_raw = pd.read_excel(filename, sheet_name=sheet, header=None)

    # Normalizing by exposure time
    exposure_time = df_raw.iat[exp_row, exp_col] * 10

    df = pd.read_excel(filename, sheet_name=sheet, header=1)
    wavelength = pd.to_numeric(df.iloc[:, 0], errors="coerce")
    intensity = pd.to_numeric(df.iloc[:, 1], errors="coerce")

    # Clean data
    valid = wavelength.notna() & intensity.notna()
    wavelength = wavelength[valid]
    intensity = intensity[valid]

    # Spectral filtering mask (above 470nm)
    mask = wavelength >= 470
    wavelength = wavelength[mask]
    intensity = intensity[mask]

    return np.trapezoid(intensity, wavelength) / exposure_time


def process_material(filename):
    xls = pd.ExcelFile(filename)
    c, I = [], []
    for sheet in xls.sheet_names:
        I_i = integrate_sheet(filename, sheet, exp_row, exp_col)
        c.append(float(sheet))
        I.append(I_i)

    c, I = np.array(c), np.array(I)
    order = np.argsort(c)
    return c[order], I[order]

# Plots
plt.rcParams['font.size'] = 11
fig_main, ax_main = plt.subplots(figsize=(9, 6))

for material, file in files.items():
    # Load and process raw data
    c_all, I_all = process_material(file)

    excluded = np.isin(c_all, excluded_points.get(material, []))
    included = ~excluded # Separate included and excluded data points

    c_fit = c_all[included]
    I_fit = I_all[included]

    # Akima interpolation
    c_smooth = np.linspace(c_fit.min(), c_fit.max(), 300)
    akima_func = Akima1DInterpolator(c_fit, I_fit)
    I_smooth = akima_func(c_smooth) # Generate smooth x-values and apply Akima interpolation

    # Retrieve material-specific styling
    style = style_config.get(material, {"color": None, "marker": "o", "linestyle": "-"})

    # Plot interpolated curve
    ax_main.plot(
        c_smooth, I_smooth,
        linestyle=style["linestyle"],
        linewidth=3.0,
        color=style["color"]
    )

    # Plot raw experimental data pts
    ax_main.plot(
        c_fit, I_fit,
        marker=style["marker"],
        linestyle='',
        markersize=7,
        color=style["color"],
        markeredgecolor='black',
        markeredgewidth=0.8,
        label=f"{material}"
    )

    if np.any(excluded): # Highlight manually excluded data points with a red circle, if any exist
        ax_main.scatter(
            c_all[excluded], I_all[excluded],
            facecolors='none',
            edgecolors='red',
            s=80,
            linewidths=1.5,
            label=f"{material} (Excluded)"
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