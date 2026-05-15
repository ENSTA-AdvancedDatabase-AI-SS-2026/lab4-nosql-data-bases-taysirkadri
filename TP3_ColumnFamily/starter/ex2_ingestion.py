"""
TP3 - Exercice 2 : Ingestion de données IoT
Use Case : SmartGrid DZ - 10 000 capteurs, 5 minutes de mesures
"""
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
import uuid
import random
from datetime import datetime, timedelta
import time

# Configuration (localhost pour installation locale)
CASSANDRA_HOST = 'localhost'  # ou '127.0.0.1'
KEYSPACE = 'smartgrid'
NB_CAPTEURS = 10000
MINUTES_HISTORIQUE = 5

WILAYAS = ["Alger", "Oran", "Constantine", "Annaba", "Blida"]
COMMUNES = {
    "Alger": ["Bab Ezzouar", "Hydra", "El Harrach", "Dar El Beida"],
    "Oran": ["Bir El Djir", "Es Senia", "Arzew"],
    "Constantine": ["El Khroub", "Ain Smara", "Hamma Bouziane"],
    "Annaba": ["El Bouni", "El Hadjar", "Seraidi"],
    "Blida": ["Bougara", "Boufarik", "Larbaa"],
}

def connect():
    """Connexion au cluster Cassandra"""
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect(KEYSPACE)
    return session, cluster


def generate_mesure(capteur_id, wilaya, commune, timestamp):
    """Générer une mesure réaliste pour un capteur"""
    tension_base = 220  # Volts (réseau algérien)
    
    alerte = random.random() < 0.10
    return {
        "capteur_id": capteur_id,
        "date_jour": timestamp.date(),
        "timestamp": timestamp,
        "wilaya": wilaya,
        "commune": commune,
        # Variation normale ± 10V
        "tension_v": round(tension_base + random.gauss(0, 5), 2),
        "courant_a": round(random.uniform(0.5, 15.0), 2),
        "puissance_kw": round(random.uniform(0.1, 3.3), 3),
        "frequence_hz": round(50 + random.gauss(0, 0.1), 2),
        "temperature": round(random.uniform(20, 65), 1),
        # 5% de chance d'alerte
        "alerte": alerte,
        "code_alerte": "TENSION" if alerte else None,
    }


def insert_single(session, mesure):
    """
    Insérer une seule mesure dans mesures_par_capteur
    Utiliser une prepared statement
    """
    prepared = session.prepare(
        """
        INSERT INTO mesures_par_capteur (
          capteur_id, date_jour, timestamp, wilaya, commune,
          tension_v, courant_a, puissance_kw, frequence_hz,
          temperature, alerte, code_alerte
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )
    session.execute(
        prepared,
        (
            mesure["capteur_id"],
            mesure["date_jour"],
            mesure["timestamp"],
            mesure["wilaya"],
            mesure["commune"],
            mesure["tension_v"],
            mesure["courant_a"],
            mesure["puissance_kw"],
            mesure["frequence_hz"],
            mesure["temperature"],
            mesure["alerte"],
            mesure["code_alerte"],
        )
    )


def insert_batch(session, mesures: list):
    """
    Insérer un batch de mesures de manière efficace
    Utiliser UNLOGGED BATCH pour les séries temporelles
    Faire des batches de max 50 items (bonne pratique Cassandra)
    """
    prepared = session.prepare(
        """
        INSERT INTO mesures_par_capteur (
          capteur_id, date_jour, timestamp, wilaya, commune,
          tension_v, courant_a, puissance_kw, frequence_hz,
          temperature, alerte, code_alerte
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )
    batch = BatchStatement(batch_type=BatchType.UNLOGGED)
    for mesure in mesures:
        batch.add(
            prepared,
            (
                mesure["capteur_id"],
                mesure["date_jour"],
                mesure["timestamp"],
                mesure["wilaya"],
                mesure["commune"],
                mesure["tension_v"],
                mesure["courant_a"],
                mesure["puissance_kw"],
                mesure["frequence_hz"],
                mesure["temperature"],
                mesure["alerte"],
                mesure["code_alerte"],
            )
        )
    session.execute(batch)


def insert_alert_batch(session, alertes: list):
    """
    Insérer un batch d'alertes dans alertes_par_wilaya
    """
    prepared = session.prepare(
        """
        INSERT INTO alertes_par_wilaya (
          wilaya, date_jour, timestamp, capteur_id,
          code_alerte, description, gravite, resolue
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    )
    batch = BatchStatement(batch_type=BatchType.UNLOGGED)
    for alerte in alertes:
        batch.add(
            prepared,
            (
                alerte["wilaya"],
                alerte["date_jour"],
                alerte["timestamp"],
                alerte["capteur_id"],
                alerte["code_alerte"],
                alerte["description"],
                alerte["gravite"],
                alerte["resolue"],
            )
        )
    session.execute(batch)


def run_ingestion(session):
    """
    Générer et insérer NB_CAPTEURS × MINUTES_HISTORIQUE mesures
    1. Générer les capteurs (ID aléatoires + assignation wilaya/commune)
    2. Pour chaque minute des MINUTES_HISTORIQUE dernières minutes
       → Insérer les mesures de tous les capteurs
    3. Mesurer et afficher :
       - Nombre total d'insertions
       - Durée totale
       - Débit (mesures/seconde)
    """
    print(f"Démarrage ingestion : {NB_CAPTEURS} capteurs × {MINUTES_HISTORIQUE} min")
    start = time.time()
    
    capteurs = []
    for i in range(NB_CAPTEURS):
        wilaya = random.choice(WILAYAS)
        commune = random.choice(COMMUNES[wilaya])
        capteurs.append((uuid.uuid4(), wilaya, commune))

    batch_size = 50
    for minute_offset in range(MINUTES_HISTORIQUE):
        timestamp = datetime.utcnow() - timedelta(minutes=minute_offset)
        batch = []
        alert_batch = []

        for capteur_id, wilaya, commune in capteurs:
            mesure = generate_mesure(capteur_id, wilaya, commune, timestamp)
            batch.append(mesure)

            if mesure["alerte"]:
                alert_batch.append({
                    "wilaya": wilaya,
                    "date_jour": mesure["date_jour"],
                    "timestamp": mesure["timestamp"],
                    "capteur_id": capteur_id,
                    "code_alerte": mesure["code_alerte"],
                    "description": "Tension hors seuil",
                    "gravite": 2,
                    "resolue": False,
                })

            if len(batch) >= batch_size:
                insert_batch(session, batch)
                batch = []

            if len(alert_batch) >= batch_size:
                insert_alert_batch(session, alert_batch)
                alert_batch = []

        if batch:
            insert_batch(session, batch)

        if alert_batch:
            insert_alert_batch(session, alert_batch)
    
    elapsed = time.time() - start
    total = NB_CAPTEURS * MINUTES_HISTORIQUE
    print(f"\n✅ {total:,} mesures insérées en {elapsed:.1f}s")
    print(f"   Débit : {total/elapsed:,.0f} mesures/seconde")


if __name__ == "__main__":
    session, cluster = connect()
    run_ingestion(session)
    cluster.shutdown()
