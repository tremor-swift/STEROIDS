# STEROIDS
### Semiautomated TEchnique for ROI Slicing and Dicing

STEROIDS extracts activation statistics from a 3D NIfTI brain map (e.g., a t-stat or z-stat map) across a set of predefined cortical and cerebellar parcellations. For each region of interest (ROI), it computes the min, max, and median activation as well as the MNI coordinates of the peak voxel.

Results are written to a single CSV file that includes the atlas label, short ROI name, full anatomical name, and all statistics — ready for downstream analysis or visualisation.

---

## Atlases included

### HCP Multi-Modal Parcellation (HCP-MMP1.0)
**360 cortical areas** (180 per hemisphere), derived from the Human Connectome Project Multi-Modal Parcellation version 1.0.

> Glasser MF, Coalson TS, Robinson EC, et al. (2016). A multi-modal parcellation of human cerebral cortex. *Nature*, 536, 171–178. https://doi.org/10.1038/nature18933

The HCP-MMP atlas subdivides the cortex based on myelin content, resting-state functional connectivity, cortical thickness, task-fMRI, and topography. Areas are labelled using a combination of Brodmann-style numbers (e.g., area 4, area 44) and descriptive acronyms (e.g., MT, FEF, RSC).

### SUIT Cerebellar Atlas
**34 cerebellar regions**: lobules (I–IV, V, VI, VIIb, VIIIa, VIIIb, IX, X), Crus I and II, Vermis subdivisions, and the three deep cerebellar nuclei (Dentate, Fastigial, Interposed).

> Diedrichsen J, Balsters JH, Flavell J, Cussans E, Ramnani N. (2009). A probabilistic MR atlas of the human cerebellum. *NeuroImage*, 46(1), 39–46. https://doi.org/10.1016/j.neuroimage.2009.01.045

---

## Output

Running `roi_statistics.py` produces `output/roi_stats.csv` with the following columns:

| Column | Description |
|--------|-------------|
| `Atlas` | Source atlas: `HCP-MMP` or `SUIT` |
| `ROI` | Short region code (e.g., `L_V1`, `R_4`, `Vermis_VI`) |
| `Full_Name` | Full anatomical name (e.g., `Primary Visual Cortex`) |
| `Min` | Minimum activation value within the ROI |
| `Max` | Maximum activation value within the ROI |
| `Median` | Median activation value within the ROI |
| `Max_X` | MNI X coordinate of the peak voxel |
| `Max_Y` | MNI Y coordinate of the peak voxel |
| `Max_Z` | MNI Z coordinate of the peak voxel |

Rows are sorted by `Max` then `Min` (most negative to most positive activation). Rows where the ROI has no overlap with the activation map are dropped.

Running `make_roi_reference.py` separately produces `output/roi_reference.csv` with just `Atlas`, `ROI`, and `Full_Name` — useful as a standalone lookup table.

---

## Installation

```bash
git clone https://github.com/<your-username>/STEROIDS.git
cd STEROIDS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.10+ recommended. Tested on Python 3.14.

---

## Usage

Place your NIfTI activation map (named `activation_map.nii`) in the project root, then run:

```bash
python roi_statistics.py
```

Custom paths are also supported:

```bash
python roi_statistics.py \
  --activation-map /path/to/your_stat_map.nii \
  --atlas-dir /path/to/atlas \
  --output-dir /path/to/output
```

To generate only the anatomical name reference table (no activation map required):

```bash
python make_roi_reference.py
```

---

## Caveats and known ambiguities in the HCP-MMP atlas

The HCP-MMP1.0 parcellation is a data-driven, multi-modal atlas and does not map cleanly onto traditional cytoarchitectonic or functional labels in all cases. The following areas warrant caution:

**Area H** — Labeled here as "Hippocampal Area H." Its precise identity is ambiguous: the Entorhinal Cortex (`EC`) is already a separate parcel in this atlas, and the role of area H as a distinct hippocampal or parahippocampal subdivision is not fully established in the original Glasser et al. 2016 paper.

**DVT (Dorsal Visual Transitional Area)** — A relatively new area without a widely adopted alternative anatomical name. Its functional profile is still being characterised in the literature.

**Area 55b** — Sometimes described as a "Premotor-Prefrontal Transition Area" or linked to the language-premotor junction. Its functional role remains an active area of investigation.

**Cingulate subdivisions** — The atlas includes many fine-grained cingulate subdivisions (areas 23c, 23d, 24dd, 24dv, 31a, 31pd, 31pv, a24, p24, d32, s32, a32pr, p32pr, 33pr, 25). These do not map one-to-one onto the traditional anterior/posterior cingulate division and should be interpreted with reference to Glasser et al. 2016 directly.

**V1 is visual, not motor** — Area `V1` is the **Primary Visual Cortex**. The **Primary Motor Cortex** is area `4`. These are occasionally confused when interpreting short codes without the full name column.

**Belt auditory areas** — `LBelt`, `MBelt`, and `PBelt` (lateral, medial, and parabelt auditory cortex) represent hierarchical stages of auditory processing. Their boundaries and labels differ from some earlier parcellation schemes.

---

## Repository contents

```
STEROIDS/
├── roi_statistics.py            # Main script: activation stats per ROI
├── roi_names.py                 # Lookup tables: short code → full anatomical name
├── make_roi_reference.py        # Generates standalone ROI reference CSV
├── roi_statistics_nilearn.ipynb # Exploratory notebook (development reference)
├── requirements.txt
├── atlas/
│   ├── hcp/                     # HCP-MMP ROI masks (360 × .nii.gz)
│   └── suit/                    # SUIT cerebellar ROI masks (34 × .nii.gz)
└── output/                      # Generated CSVs written here (not tracked by git)
```

---

## Citation

If you use STEROIDS in your work, please cite the atlases above and acknowledge this tool.
