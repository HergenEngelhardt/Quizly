# Docker Setup Guide für Quizly

## Schnellstart mit Docker Desktop

### 1. Voraussetzungen prüfen
```powershell
# Docker Version prüfen
docker --version

# Docker Compose Version prüfen  
docker-compose --version

# Docker Desktop Status prüfen
docker ps
```

### 2. Umgebungsvariablen konfigurieren
Die Docker-Konfiguration verwendet automatisch PostgreSQL. Stellen Sie sicher, dass Sie Ihren GEMINI_API_KEY setzen:

```powershell
# In PowerShell setzen
$env:GEMINI_API_KEY="your-gemini-api-key-here"

# Oder in .env.docker editieren
```

**Wichtig**: Für lokale Entwicklung ohne Docker verwenden Sie die `.env` Datei mit `FORCE_SQLITE=true`.
Für Docker wird automatisch `.env.docker` mit PostgreSQL verwendet.

### 3. Docker Container starten
```powershell
# Container bauen und starten
docker-compose up -d --build

# Logs anzeigen
docker-compose logs -f web
```

### 4. Container Status prüfen
```powershell
# Container Status
docker-compose ps

# PostgreSQL Logs
docker-compose logs db
docker-compose exec web python manage.py createsuperuser
```

### 5. Anwendung testen
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/

### 6. Docker Desktop Überwachung
1. Öffnen Sie Docker Desktop
2. Gehen Sie zu "Containers"
3. Sie sollten das "quizly" Projekt mit zwei Containern sehen:
   - `quizly-web-1` (Django App)
   - `quizly-db-1` (PostgreSQL DB)

### 7. Container stoppen
```powershell
# Container stoppen
docker-compose down

# Container und Volumes löschen (Datenbank wird gelöscht!)
docker-compose down -v
```

## Fehlerbehebung

### Container startet nicht
1. Prüfen Sie ob Docker Desktop läuft
2. Ports 8000 und 5432 verfügbar?
3. Logs prüfen: `docker-compose logs`

### Datenbank Verbindungsfehler
1. PostgreSQL braucht Zeit zum Initialisieren
2. DB Logs prüfen: `docker-compose logs db`
3. Environment Variablen überprüfen

### Performance Probleme
1. Mehr Ressourcen in Docker Desktop zuweisen
2. WSL 2 Backend aktivieren (Windows)
