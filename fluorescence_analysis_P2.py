import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import Akima1DInterpolator

# --- Setup and Initialization ---
materials = ['FE', 'RB', 'R6G']
concentrations = [1, 2, 3, 4, 5]  # Assuming file names end with (1) to (5)

results = []

# --- Main Loop over Materials and Concentrations ---
for mat in materials:

    # Auto-select color channel based on emission peak
    if mat == 'RB':
        C = 0  # Red channel for Rhodamine B (~580nm)
    else:
        C = 1  # Green channel for Fluorescein (~520nm) and R6G (~560nm)

    for c in concentrations:
        filename = f"{mat} ({c}).jpg"

        if not os.path.isfile(filename):
            print(f"Warning: File {filename} not found. Skipping...")
            continue

        # Load image
        img_raw = plt.imread(filename)
        if img_raw.dtype == np.uint8:
            img = img_raw.astype(float) / 255.0
        else:
            img = img_raw.copy()

        # Flip image matrix vertically to match Cartesian Y-axis
        img = np.flipud(img)

        # ==========================================
        # --- STEP 1: CONTAINER CALIBRATION ---
        # ==========================================
        fig_calib, ax_calib = plt.subplots(figsize=(7, 4))
        fig_calib.canvas.manager.set_window_title(f"Calibration for {filename}")

        cax_calib = ax_calib.imshow(img[:, :, C], cmap='jet', origin='lower')
        cbar_calib = fig_calib.colorbar(cax_calib)
        cbar_calib.set_label('Intensity Spectrum [Arb. Units]', fontsize=11)

        ax_calib.set_xlabel('x [Arb. Length Units]', fontsize=11)
        ax_calib.set_ylabel('y [Arb. Length Units]', fontsize=11)
        ax_calib.set_title(f'[{filename}]\nSTEP 1: Click Container 0cm (left) and 10cm (right)', fontsize=13)

        ax_calib.minorticks_on()
        ax_calib.grid(which='major', color='white', linestyle='-', linewidth=0.8, alpha=0.6)
        ax_calib.grid(which='minor', color='white', linestyle=':', linewidth=0.5, alpha=0.4)

        print(f"Please click 0cm and 10cm marks on the container for {filename}...")
        calib_points = plt.ginput(2, timeout=0)
        plt.close(fig_calib)

        if len(calib_points) < 2:
            print(f"Warning: 2 calibration points were not selected for {filename}. Skipping...")
            continue

        X_calib0 = calib_points[0][0]
        X_calib10 = calib_points[1][0]

        # CALCULATIONS: Spatial Calibration
        # Calculate the spatial calibration factor (pixels per cm) based on the user-defined 10 cm reference points.
        pixels_per_cm = abs(X_calib10 - X_calib0) / 10.0

        # ==========================================
        # --- STEP 2: BEAM ROI SELECTION ---
        # ==========================================
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.canvas.manager.set_window_title(f"Select ROI for {filename}")

        cax = ax.imshow(img[:, :, C], cmap='jet', origin='lower')
        cbar = fig.colorbar(cax)
        cbar.set_label('Intensity Spectrum [Arb. Units]', fontsize=11)

        ax.set_xlabel('x [Arb. Length Units]', fontsize=11)
        ax.set_ylabel('y [Arb. Length Units]', fontsize=11)
        ax.set_title(f'[{filename}]\nSTEP 2: Click Beam START (left) and Beam END (right)', fontsize=13)

        ax.minorticks_on()
        ax.grid(which='major', color='white', linestyle='-', linewidth=0.8, alpha=0.6)
        ax.grid(which='minor', color='white', linestyle=':', linewidth=0.5, alpha=0.4)

        print(f"Please click beam start and end points for {filename}...")
        points = plt.ginput(2, timeout=0)
        plt.close(fig)

        if len(points) < 2:
            print(f"Warning: 2 ROI points were not selected for {filename}. Skipping...")
            continue

        X1, Y1 = int(round(points[0][0])), int(round(points[0][1]))
        X2, _ = int(round(points[1][0])), int(round(points[1][1]))

        if X1 > X2:
            X1, X2 = X2, X1

        # CALCULATIONS: Intensity Profile Extraction
        # Extract a horizontal slice of the image around the selected beam path and average it vertically to reduce noise.
        window_size = 5
        Av_matrix = img[Y1 - window_size: Y1 + window_size + 1, X1:X2, C]
        Av = np.mean(Av_matrix, axis=0)

        # CALCULATIONS: Physical Axis Mapping
        # Convert the pixel index array into a physical distance array (in cm) using the calculated calibration factor.
        x = np.arange(len(Av)) / pixels_per_cm

        # CALCULATIONS: Peak and 1/e Drop Finding
        # Find the peak intensity value (I0) and its index.
        max_idx = np.argmax(Av)
        I0 = Av[max_idx]

        # Calculate the 1/e intensity threshold. According to the Beer-Lambert law (I = I0 * e^(-alpha * x)),
        # the intensity drops to I0/e exactly at the distance x = 1/alpha.
        I_target = I0 / np.exp(1)

        search_range = Av[max_idx:]
        drop_indices = np.where(search_range <= I_target)[0]

        if len(drop_indices) == 0:
            distance_1e = np.nan
            alpha = np.nan
        else:
            drop_idx_relative = drop_indices[0]
            drop_idx = max_idx + drop_idx_relative

            # Shift the x-axis so the peak intensity is physically located at x=0.
            # Then, extract the exact physical distance where the intensity dropped below the 1/e threshold.
            x_shifted = x - x[max_idx]
            distance_1e = x_shifted[drop_idx]

            # Calculate the attenuation coefficient alpha (in cm^-1), which is the reciprocal of the 1/e drop distance.
            alpha = 1.0 / distance_1e if distance_1e != 0 else np.nan

        # 5. Save results
        results.append({
            'Material': mat,
            'Concentration_Idx': c,
            'Distance_1e_cm': distance_1e,
            'Alpha_cm_inv': alpha
        })

        print(f"Processed: {filename} | x_(1/e) = {distance_1e:.3f} cm | Alpha = {alpha:.3f} cm^-1")

        # ==========================================
        # --- DUAL VISUAL CONFIRMATION ---
        # ==========================================
        fig_verify, (ax_graph, ax_img) = plt.subplots(2, 1, figsize=(5, 5))
        fig_verify.canvas.manager.set_window_title(f"Verification: {filename}")

        # --- Top Subplot: Intensity Profile ---
        conc_map = {1: '0.1 mM', 2: '0.05 mM', 3: '0.025 mM', 4: '0.01 mM', 5: '0.005 mM'}
        fig_verify.suptitle(f"Fluorophore: {mat} | Concentration: {conc_map[c]}", fontsize=13, fontweight='bold')
        ax_graph.plot(x, Av, color='blue', linewidth=2, label='Intensity Profile')
        ax_graph.axhline(I_target, color='gray', linestyle='--', label='1/e Threshold')

        # Mark Peak and 1/e drop with distinct colors
        if not np.isnan(distance_1e):
            ax_graph.plot(x[max_idx], I0, marker='o', color='orange', markersize=5, label='Peak (I_0)')
            ax_graph.plot(x[drop_idx], Av[drop_idx], marker='D', color='magenta', markersize=5, label='1/e Drop')

        ax_graph.set_title(f"Intensity Profile | x_(1/e) = {distance_1e:.3f} cm | Alpha = {alpha:.3f} cm^-1",
                           fontsize=9)

        ax_graph.set_ylabel("Intensity [AU]", fontsize=11)
        ax_graph.set_xlabel("Distance [cm]", fontsize=11)

        ax_graph.legend(loc='upper right', fontsize=8)
        ax_graph.grid(True, linestyle='--', alpha=0.7)

        # --- Bottom Subplot: Image with ROI ---
        cax_img = ax_img.imshow(img[:, :, C], cmap='jet', origin='lower', aspect='auto')
        ax_img.plot([X1, X2], [Y1, Y1], color='white', linestyle='--', linewidth=2)

        # Mark Start and End boundaries
        ax_img.plot(X1, Y1, marker='>', color='lime', markersize=5, label='Start (X1)')
        ax_img.plot(X2, Y1, marker='s', color='red', markersize=5, label='End (X2)')

        # Mark Peak and 1/e drop PHYSICALLY on the image!
        if not np.isnan(distance_1e):
            pixel_peak = X1 + max_idx
            pixel_1e = X1 + drop_idx
            ax_img.plot(pixel_peak, Y1, marker='o', color='orange', markersize=3, label='Peak (I_0)')
            ax_img.plot(pixel_1e, Y1, marker='D', color='magenta', markersize=3, label='1/e Drop')

        ax_img.set_title("Intensity Spectrum Mapping- Data Pts & ROI", fontsize=11)

        ax_img.set_xlabel('x [Arb. Length Units]', fontsize=11)
        ax_img.set_ylabel('y [Arb. Length Units]', fontsize=11)

        ax_img.legend(loc='upper right', fontsize=8)

        # Added the transparent grid to the bottom subplot
        ax_img.minorticks_on()
        ax_img.grid(which='major', color='white', linestyle='-', linewidth=0.8, alpha=0.6)
        ax_img.grid(which='minor', color='white', linestyle=':', linewidth=0.5, alpha=0.4)

        cbar_img = fig_verify.colorbar(cax_img, ax=ax_img)
        cbar_img.set_label('Intensity Spectrum [Arb. Units]', fontsize=9)

        plt.tight_layout()

        plt.savefig(f"Checked_{filename}")

        print("Please close the graph window to continue to the next image...")
        plt.show(block=True)