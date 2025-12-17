# Respiratory Disease Detection Using Lung Sound Analysis

A lightweight, reproducible workflow to explore lung-sound recordings, segment breath cycles, visualize spectrograms, and prepare tabular features for downstream modeling.

## What This Project Does
- Loads diagnosis labels and demographic data.
- Parses audio file names to extract metadata (patient, location, equipment).
- Visualizes mel-spectrograms for quick, sanity-checked inspection.
- Segments each `.wav` recording into labeled breath-cycle clips using annotation `.txt` files.
- Cleans and merges demographics with diagnosis, then builds a numeric feature matrix (scaled numeric + one-hot categorical) ready for ML.

## Repository Layout
- [copdresearch.ipynb](copdresearch.ipynb): Main notebook with the full workflow.
- [demographic_info.txt](demographic_info.txt): Demographic table (age, gender, BMI/child measures).
- [Respiratory_Sound_Database/](Respiratory_Sound_Database/)
  - [patient_diagnosis.csv](Respiratory_Sound_Database/patient_diagnosis.csv): Patient-level diagnosis labels.
  - [audio_and_txt_files/](Respiratory_Sound_Database/audio_and_txt_files/): Paired `.wav` audio and `.txt` annotations (start, end, crackles, wheezes).
  - [segmented_audio/](Respiratory_Sound_Database/segmented_audio/): Output folder for per-cycle clips created by the notebook.
  - [filename_format.txt](Respiratory_Sound_Database/filename_format.txt) and [filename_differences.txt](Respiratory_Sound_Database/filename_differences.txt): Dataset notes.

## Dataset Notes
- Each `.txt` file has tab-separated columns: `Start`, `End`, `Crackles`, `Wheezes`.
- Each segment is saved as: `<original>.wav` → `<original>_cycle_<i>_label_<CW>.wav`
  - `CW` is a two-digit code: `00`=none, `01`=wheeze, `10`=crackle, `11`=crackle+wheeze.
- File name schema (simplified):
  `Patient_RecordingIndex_ChestLocation_AcquisitionMode_Equipment.wav`

## Requirements
- Python 3.10+
- Recommended: a virtual environment

Install core packages:

```bash
pip install pandas numpy scikit-learn librosa soundfile matplotlib
```

If librosa warns about resampling backends, also install:

```bash
pip install soxr
```

## Quick Start
1. Open the notebook: [copdresearch.ipynb](copdresearch.ipynb).
2. Run the initial cells to:
   - Load diagnosis and demographics tables.
   - Parse and index audio files.
   - Build the combined annotations DataFrame.
3. Use the mel-spectrogram cells to visualize example recordings and confirm audio integrity.
4. Run the segmentation cell to create labeled breath-cycle clips in
   [Respiratory_Sound_Database/segmented_audio/](Respiratory_Sound_Database/segmented_audio/).
5. Run the preprocessing cell to produce a numeric feature matrix (`processed_df`) from demographics and diagnosis.

## Segmentation Details
- Segmentation uses the annotation files to slice each `.wav` by `Start/End` seconds.
- By default, the loop processes only the first 5 annotated files (for quick testing). To process all files, remove or adjust this limit in the segmentation loop:

```python
for i, meta_file in enumerate(glob.glob(os.path.join(audio_path, "*.txt"))):
    # if i >= 5:  # ← remove or change this limit
    #     break
    input_path = os.path.splitext(meta_file)[0] + ".wav"
    seg_and_save(input_path, meta_file, output_dir)
```

- Output segments land in: [Respiratory_Sound_Database/segmented_audio/](Respiratory_Sound_Database/segmented_audio/).

## Preprocessing & Features
- The notebook scales numeric columns (`Age`, `BMI (kg/m2)`) and one-hot encodes categorical columns (`Gender`, `Diagnosis`).
- Result: `processed_df`, a clean numeric matrix you can feed into ML models.
- Tip: If you see a KeyError for `Sex` vs `Gender`, ensure the categorical column list uses `Gender` (the demographics table uses `Gender`).

## Optional Next Steps
- Extract per-segment audio features (e.g., log-mel, MFCCs, spectral stats) and aggregate by patient or use directly for segment-level models.
- Split data by patient to avoid leakage (train/validation/test).
- Train a baseline classifier (e.g., Logistic Regression, Random Forest, SVM) on `processed_df` plus audio features.
- Evaluate with accuracy/F1, confusion matrix, ROC-AUC; save trained models and reports.

## Troubleshooting
- Paths on Windows: In Python strings, use raw strings (`r"..."`) or double backslashes to avoid escape issues.
- Long runs: Processing all files can be slow. Start with small subsets (keep the 5-file limit) and scale up.
- Sparse outputs: Some scikit-learn transformers return sparse matrices; the notebook converts to dense when building a DataFrame.

## Acknowledgments
This project uses the ICBHI Respiratory Sound Database (2017). Please follow the dataset’s license and citation guidelines when using the data.
