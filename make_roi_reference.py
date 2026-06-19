#!/usr/bin/env python3
"""Generate a standalone reference CSV mapping every atlas ROI to its full anatomical name."""
import argparse
import os
import re
import pandas as pd

from roi_names import HCP_NAMES, SUIT_NAMES
from roi_statistics import clean_roi_name


def parse_args():
    base = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Generate atlas ROI reference CSV")
    p.add_argument(
        "--atlas-dir",
        default=os.path.join(base, "atlas"),
        help="Directory containing hcp/ and suit/ subdirectories",
    )
    p.add_argument(
        "--output-dir",
        default=os.path.join(base, "output"),
        help="Directory to write roi_reference.csv",
    )
    return p.parse_args()


def lookup_full_name(roi_name: str, atlas_label: str) -> str:
    area_code = re.sub(r"^(?:L|R|Vermis)_", "", roi_name)
    lookup = HCP_NAMES if atlas_label == "HCP-MMP" else SUIT_NAMES
    return lookup.get(area_code, "Unknown")


def main():
    args = parse_args()

    atlas_subdirs = [("hcp", "HCP-MMP"), ("suit", "SUIT")]
    records = []

    for subdir, label in atlas_subdirs:
        path = os.path.join(args.atlas_dir, subdir)
        for fname in sorted(os.listdir(path)):
            if fname.endswith(".nii") or fname.endswith(".nii.gz"):
                roi_name = clean_roi_name(fname)
                full_name = lookup_full_name(roi_name, label)
                records.append({"Atlas": label, "ROI": roi_name, "Full_Name": full_name})

    df = pd.DataFrame(records)

    unknown = df[df["Full_Name"] == "Unknown"]
    if not unknown.empty:
        print(f"WARNING: {len(unknown)} ROIs have no anatomical name mapping:")
        print(unknown.to_string(index=False))

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "roi_reference.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows → {out_path}")


if __name__ == "__main__":
    main()
