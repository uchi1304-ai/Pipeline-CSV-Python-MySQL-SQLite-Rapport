import sys
import os
import csv
import mysql.connector
import statistics as stats
import sqlite3
import matplotlib
matplotlib.use("Agg")  # évite les soucis de backend sans interface graphique
import matplotlib.pyplot as plt

# Force l'UTF-8 sur la sortie, pour éviter un crash si la console/le fichier
# de redirection utilise un encodage (cp1252) qui ne supporte pas certains
# caractères présents dans le chemin du dossier (ex: →).
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

print("Répertoire de travail courant :", os.getcwd())

# Lire le CSV du pouls; extraire les données brutes.
pouls = []

with open("poulspatient01.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        pouls.append(int(row["pouls"]))

pouls_max = max(pouls)
print("1. CSV lu, pouls_max =", pouls_max)

# Lire la tension dans MySQL: extraire une deuxième source.
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Malbosc!2025",
    database="signes_vitaux",
    use_pure=True
)
print("2. Connexion MySQL OK")

cur = cnx.cursor(dictionary=True)

cur.execute("SELECT tension FROM tension_horaire WHERE id_patient = 1")

tensions = [row["tension"] for row in cur.fetchall()]
print("3. Tensions récupérées :", tensions)

if not tensions:
    raise ValueError(
        "Aucune tension trouvée pour id_patient = 1 : "
        "vérifie le contenu de la table tension_horaire."
    )

tension_moyenne = stats.mean(tensions)
print("4. Tension moyenne =", tension_moyenne)

# Mettre à jour MySQL; stocker les données enrichies.
cur.execute("""
REPLACE INTO patient_signes (id_patient, pouls_max, tension_moyenne)
VALUES (%s, %s, %s)
""", (1, pouls_max, tension_moyenne))

cnx.commit()
print("5. MySQL mis à jour (patient_signes)")

# Exporter dans SQLite (datalake): archiver les données brutes.
cnx_sqlite = sqlite3.connect("datalake.db")
cursqlite = cnx_sqlite.cursor()

cursqlite.execute("CREATE TABLE IF NOT EXISTS datalakepouls (heure INT, pouls INT)")
cursqlite.execute("CREATE TABLE IF NOT EXISTS datalaketension (heure INT, tension INT)")

for h, p in enumerate(pouls):
    cursqlite.execute("INSERT INTO datalakepouls VALUES (?, ?)", (h, p))

for h, t in enumerate(tensions):
    cursqlite.execute("INSERT INTO datalaketension VALUES (?, ?)", (h, t))

cnx_sqlite.commit()
print("6. SQLite mis à jour, fichier :", os.path.abspath("datalake.db"))

# Générer un rapport TXT; produire un artefact d'analyse.
valeur_aberrante = max(pouls) if max(pouls) > 110 else None

with open("rapport_patient.txt", "w", encoding="utf-8") as f:
    f.write("RAPPORT PATIENT\n")
    f.write(f"Pouls max : {pouls_max}\n")
    f.write(f"Tension moyenne : {tension_moyenne:.2f}\n")

    if valeur_aberrante:
        f.write(f"Valeur aberrante détectée : {valeur_aberrante}\n")

print("7. Rapport écrit :", os.path.abspath("rapport_patient.txt"))

# Générer une courbe PNG; visualiser les données.
heures = list(range(len(pouls)))

plt.plot(heures, pouls, marker="o")
plt.xlabel("Heure")
plt.ylabel("Pouls (bpm)")
plt.title("Évolution du pouls sur 24h")
plt.grid(True)
plt.savefig("courbe_pouls.png")

print("8. Courbe enregistrée :", os.path.abspath("courbe_pouls.png"))

print("Pipeline terminé.")