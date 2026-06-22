import pandas as pd

# Charger le CSV sale
df = pd.read_csv("nuitpatientsale.csv", sep=";")

lignes_initiales = len(df)

# Compter les valeurs manquantes avant correction
valeurs_manquantes = df.isna().sum().sum()

# Corriger les types; Si no puedes convertirlo a número, conviértelo en NaN
df["frequenceresp"] = pd.to_numeric(df["frequenceresp"], errors="coerce")
df["spo2"] = pd.to_numeric(df["spo2"], errors="coerce")

# Remplacer les valeurs manquantes
df["frequenceresp"] = df["frequenceresp"].fillna(df["frequenceresp"].mean())
df["spo2"] = df["spo2"].fillna(df["spo2"].median())

# Corriger les valeurs aberrantes : SpO2 > 100
# Está sumando los True.
valeurs_aberrantes = (df["spo2"] > 100).sum()
# hayo la media de los valores menores a 100
moyenne_spo2_valide = df[df["spo2"] <= 100]["spo2"].mean()
# reemplawo los valores mayores por la media 
df.loc[df["spo2"] > 100, "spo2"] = moyenne_spo2_valide

# Convertir en entier
df["frequenceresp"] = df["frequenceresp"].round().astype(int)
df["spo2"] = df["spo2"].round().astype(int)

# Normaliser les événements
event_avant = df["eventtype"].copy()

df["eventtype"] = df["eventtype"].str.lower()

corrections = {
    "hypopne": "hypopnee",
    "hypopnée": "hypopnee",
    "hypopnee": "hypopnee",
    "none": "none",
    "NONE": "none",
    "Hypopnee": "hypopnee"
}

df["eventtype"] = df["eventtype"].replace(corrections)

# se guarda la lista de correciones para el info final 
corrections_evenements = []

for ancien, nouveau in zip(event_avant, df["eventtype"]):
    if ancien != nouveau:
        corrections_evenements.append(f"{ancien} -> {nouveau}")

# Supprimer les doublons y cuenta la las filas de duplicados 
doublons = df.duplicated().sum()
df = df.drop_duplicates()

lignes_finales = len(df)

# Exporter le CSV propre
df.to_csv("nuitpatientpropre.csv", sep=";", index=False)

# Générer le rapport qualité
with open("rapport_qualite.txt", "w", encoding="utf-8") as f:
    f.write("RAPPORT QUALITÉ\n")
    f.write("================\n")
    f.write(f"Nombre de lignes initiales : {lignes_initiales}\n")
    f.write(f"Nombre de doublons supprimés : {doublons}\n")
    f.write(f"Nombre de valeurs manquantes corrigées : {valeurs_manquantes}\n")
    f.write(f"Nombre de valeurs aberrantes corrigées : {valeurs_aberrantes}\n")
    f.write("Liste des corrections d'événements :\n")

    for correction in corrections_evenements:
        f.write(f"- {correction}\n")

    f.write(f"Nombre de lignes finales : {lignes_finales}\n")

print("Nettoyage terminé avec succès.")