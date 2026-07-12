import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Data Loading ---
file_path = 'RESULTS_MF_PT2_DATASHEET.xlsx'

try:
    results_df = pd.read_excel(file_path)
    results_df.columns = results_df.columns.str.strip()
    print("=== Loaded Results ===")
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    exit()

# --- 2. Setup and Formatting ---
plt.figure("Alpha vs Concentration", figsize=(8, 6))

style_config = {
    "Fluorescein": {"color": "#FFD700", "marker": "o", "linestyle": "-"},
    "Rhodamine B": {"color": "#FF69B4", "marker": "s", "linestyle": "--"},
    "Rhodamine 6G": {"color": "#FF8C00", "marker": "D", "linestyle": "-."}
}

name_mapping = {
    'FE': 'Fluorescein',
    'RB': 'Rhodamine B',
    'R6G': 'Rhodamine 6G'
}

conc_num_map = {1: 0.1, 2: 0.05, 3: 0.025, 4: 0.01, 5: 0.005}
plot_order = ['FE', 'RB', 'R6G']

# --- 3. Plotting and Analysis Loop ---
for mat in plot_order:
    mat_data = results_df[(results_df['Fluorophore'] == mat)].dropna(subset=['Alpha [cm^-1]'])

    if not mat_data.empty:
        full_name = name_mapping[mat]
        config = style_config[full_name]

        c_indices = mat_data['Concentration IDX'].values
        x = np.array([conc_num_map[c] for c in c_indices])
        y = mat_data['Alpha [cm^-1]'].values

        # Linear Fit to calculate R^2
        m, b = np.polyfit(x, y, 1)
        y_fit = m * x + b

        residuals = y - y_fit
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Construct label with R^2 value
        label_text = f"{full_name} ($R^2={r_squared:.3f}$)"

        # Plot label entry for legend
        plt.plot([], [], color=config['color'], marker=config['marker'],
                 linestyle=config['linestyle'], label=label_text, linewidth=3, markersize=8)

        # Plot linear fit line
        plt.plot(x, y_fit, color=config['color'], linestyle=config['linestyle'], linewidth=3)

        # Plot data points
        plt.plot(x, y, color=config['color'], marker=config['marker'],
                 linestyle='None', markersize=8)

# --- 4. Final Plot Formatting ---
plt.xlabel('Concentration [mM]', fontsize=16)
plt.ylabel(r'$\alpha$ [cm$^{-1}$]', fontsize=16)
plt.title('Attenuation Coefficient vs. Concentration', fontsize=18)
plt.legend(loc='best', fontsize=13, handlelength=5)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()