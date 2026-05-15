# Local Setup Guide (No Docker)

## 1. Install Redis (Windows)

Download from: https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi

Or use Chocolatey:
```powershell
choco install redis -y
```

Start Redis:
```powershell
redis-server
```

Test connection:
```powershell
redis-cli ping
# Should return: PONG
```

---

## 2. Install MongoDB (Windows)

Download from: https://www.mongodb.com/try/download/community

Or use Chocolatey:
```powershell
choco install mongodb-community -y
```

Start MongoDB:
```powershell
mongod --dbpath "C:\data\db"
```

Or if installed as service:
```powershell
net start MongoDB
```

Test connection:
```powershell
mongosh -u admin -p admin123 --authenticationDatabase admin
```

---

## 3. Install Cassandra (Windows)

Download from: https://cassandra.apache.org/download/

Requirements: Java 11+ (install from https://www.oracle.com/java/technologies/downloads/)

Extract and add to PATH. Then start:
```powershell
cassandra.bat
```

Test connection:
```powershell
cqlsh
# Should connect without error
```

---

## 4. Install Neo4j (Windows)

Download from: https://neo4j.com/download/

Or use Chocolatey:
```powershell
choco install neo4j-community -y
```

Start Neo4j:
```powershell
neo4j start
```

Test connection (browse to):
http://localhost:7474

Login: neo4j / password123

---

## 5. Python Dependencies

All already installed:
```powershell
pip install redis pymongo cassandra-driver neo4j pytest
```

---

## Run Tests & Benchmarks

See below for exact commands.

---

## Lancer avec Docker Compose (rapide)

Si vous préférez ne pas installer les services localement, utilisez Docker Compose depuis la racine du projet.

```powershell
# Démarrer tous les services en arrière-plan
docker-compose up -d

# Vérifier les conteneurs
docker-compose ps

# Tester Redis depuis le conteneur
docker-compose exec redis redis-cli ping   # PONG attendu

# Arrêter et supprimer les conteneurs
docker-compose down
```

Le dépôt contient déjà un `docker-compose.yml` prêt à l'emploi pour Redis, MongoDB, Cassandra et Neo4j. C'est la façon la plus simple pour exécuter les TP sur une machine sans installer chaque base.
