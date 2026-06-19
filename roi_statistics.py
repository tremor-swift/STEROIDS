#!/usr/bin/env python3
import argparse
import os
import re
import numpy as np
import nibabel as nib
import pandas as pd
from nilearn.image import resample_img
from roi_names import HCP_NAMES, SUIT_NAMES


def parse_args():
    base = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Measure activation statistics in atlas ROIs")
    p.add_argument(
        "--activation-map",
        default=os.path.join(base, "activation_map.nii"),
        help="Path to NIfTI activation map (default: activation_map.nii next to script)",
    )
    p.add_argument(
        "--atlas-dir",
        default=os.path.join(base, "atlas"),
        help="Directory containing hcp/ and suit/ atlas subdirectories",
    )
    p.add_argument(
        "--output-dir",
        default=os.path.join(base, "output"),
        help="Directory to write output CSV",
    )
    return p.parse_args()


def collect_roi_files(atlas_dir):
    atlas_subdirs = [("hcp", "HCP-MMP"), ("suit", "SUIT")]
    roi_files = []
    for subdir, label in atlas_subdirs:
        path = os.path.join(atlas_dir, subdir)
        for fname in sorted(os.listdir(path)):
            if fname.endswith(".nii") or fname.endswith(".nii.gz"):
                roi_files.append((os.path.join(path, fname), label))
    return roi_files


def clean_roi_name(basename):
    # Strip roi_ prefix, optional suit_ prefix, and _mask.nii[.gz] suffix
    return re.sub(r"^roi_(?:suit_)?|_mask\.nii(?:\.gz)?$", "", basename)


def lookup_full_name(roi_name: str, atlas_label: str) -> str:
    area_code = re.sub(r"^(?:L|R|Vermis)_", "", roi_name)
    lookup = HCP_NAMES if atlas_label == "HCP-MMP" else SUIT_NAMES
    return lookup.get(area_code, "Unknown")


def process_roi(roi_path, activation_data, activation_img):
    roi_img = nib.load(roi_path)
    roi_data_bin = (roi_img.get_fdata() > 0).astype(np.uint8)
    roi_bin_img = nib.Nifti1Image(roi_data_bin, roi_img.affine, roi_img.header)

    roi_resampled = resample_img(
        roi_bin_img,
        target_affine=activation_img.affine,
        target_shape=activation_img.shape,
        interpolation="nearest",
        force_resample=True,
        copy_header=True,
    )
    roi_mask = roi_resampled.get_fdata()
    masked_values = activation_data[roi_mask > 0]
    masked_values = masked_values[~np.isnan(masked_values)]

    if masked_values.size == 0:
        return None, None, None, [None, None, None]

    min_val = float(np.min(masked_values))
    max_val = float(np.max(masked_values))
    median_val = float(np.median(masked_values))

    masked_indices = np.argwhere(roi_mask > 0)
    activation_vals = activation_data[roi_mask > 0]
    max_idx = np.nanargmax(activation_vals)
    mni = nib.affines.apply_affine(activation_img.affine, masked_indices[max_idx])

    return min_val, max_val, median_val, mni


def main():
    args = parse_args()

    print(f"Loading activation map: {args.activation_map}")
    activation_img = nib.load(args.activation_map)
    activation_data = activation_img.get_fdata()

    roi_files = collect_roi_files(args.atlas_dir)
    print(f"Found {len(roi_files)} ROI files — processing...")

    records = []
    for roi_path, atlas_label in roi_files:
        basename = os.path.basename(roi_path)
        roi_name = clean_roi_name(basename)
        min_val, max_val, median_val, mni = process_roi(roi_path, activation_data, activation_img)
        full_name = lookup_full_name(roi_name, atlas_label)
        records.append(
            {
                "Atlas": atlas_label,
                "ROI": roi_name,
                "Full_Name": full_name,
                "Min": min_val,
                "Max": max_val,
                "Median": median_val,
                "Max_X": mni[0],
                "Max_Y": mni[1],
                "Max_Z": mni[2],
            }
        )

    df = (
        pd.DataFrame(records)
        .dropna()
        .sort_values(by=["Max", "Min"])
        .reset_index(drop=True)
    )

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "roi_stats.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows → {out_path}")


if __name__ == "__main__":
    main()
