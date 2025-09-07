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
Stellen Sie sicher, dass Ihre `.env` Datei korrekt konfiguriert ist:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
GEMINI_API_KEY=your-gemini-api-key-here
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Zusätzlich für Docker mit PostgreSQL
POSTGRES_DB=quizly
POSTGRES_USER=quizly_user
POSTGRES_PASSWORD=quizly_password
```

### 3. Docker Container starten
```powershell
# Container bauen und starten
docker-compose up -d --build

# Logs anzeigen
docker-compose logs -f web
```

### 4. Datenbank initialisieren
```powershell
# Migrationen ausführen
docker-compose exec web python manage.py migrate

# Superuser erstellen
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
