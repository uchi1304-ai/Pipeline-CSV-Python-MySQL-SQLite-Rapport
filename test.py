import mysql.connector

print("avant connexion")

try:
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Malbosc!2025",
        connection_timeout=3,
        use_pure=True
    )

    print("connecté au serveur MySQL")
    cursor = cnx.cursor()
    cursor.execute("SHOW DATABASES;")
    print(cursor.fetchall())

    cnx.close()

except Exception as e:
    print("ERREUR :", repr(e))

print("fin")