import pickle
import numpy as np
import pandas as pd
import streamlit as st
import librosa
import librosa.feature


def extract_audio_features(file_path, sr=None, n_mfcc=5):
    """Same feature extraction as used during training in the notebook."""
    audio, sr = librosa.load(file_path, sr=sr)

    features = {}

    # Basic energy
    rms = librosa.feature.rms(y=audio)[0]
    features["rms_mean"] = float(rms.mean())
    features["rms_std"] = float(rms.std())

    # Zero-crossing rate
    zcr = librosa.feature.zero_crossing_rate(y=audio)[0]
    features["zcr_mean"] = float(zcr.mean())
    features["zcr_std"] = float(zcr.std())

    # Spectral centroid
    spec_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
    features["spec_centroid_mean"] = float(spec_centroid.mean())
    features["spec_centroid_std"] = float(spec_centroid.std())

    # MFCCs
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    for i in range(n_mfcc):
        coeff = mfcc[i]
        features[f"mfcc_{i + 1}_mean"] = float(coeff.mean())
        features[f"mfcc_{i + 1}_std"] = float(coeff.std())

    return features


with open("lung_model.pkl", "rb") as f:
    artifacts = pickle.load(f)

model = artifacts["model"]
preprocessor = artifacts["preprocessor"]
audio_feature_cols = artifacts["audio_feature_cols"]


st.title("Respiratory Disease Prediction")

st.write("Upload a lung sound recording (.wav) and enter basic info.")

uploaded_file = st.file_uploader("Lung sound (.wav)", type=["wav"])
age = st.number_input("Age", 0, 120, 60)
bmi = st.number_input("BMI", 10.0, 60.0, 24.0)
gender = st.selectbox("Gender", ["M", "F"])

if st.button("Predict"):
    if uploaded_file is None:
        st.error("Please upload a .wav file first.")
    else:
        # Save uploaded file to a temporary location for librosa
        with open("_tmp_uploaded.wav", "wb") as tmp_f:
            tmp_f.write(uploaded_file.read())

        feats_ext = extract_audio_features("_tmp_uploaded.wav", sr=None)

        feature_dict = {"Age": age, "BMI (kg/m2)": bmi, "Gender": gender}
        for col in audio_feature_cols:
            feature_dict[col] = float(feats_ext.get(col, np.nan))

        X = pd.DataFrame([feature_dict])
        X_proc = preprocessor.transform(X)
        if hasattr(X_proc, "toarray"):
            X_proc = X_proc.toarray()
        pred = model.predict(X_proc)[0]
        st.success(f"Predicted diagnosis: {pred}")