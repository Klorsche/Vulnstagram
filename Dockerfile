FROM python:3.11-slim

WORKDIR /app

# Dipendenze di sistema (utile avere il client mysql per test/debug interni)
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Best practice di sicurezza: eseguiamo l'app con un utente non root
RUN useradd -m appuser
# Nota per il lab: useremo root o aggiusteremo i permessi se ci servirà testare privilege escalation o LFI particolari, ma partiamo sicuri.
RUN chown -R appuser:appuser /app
USER appuser

# L'app verrà montata come volume per comodità di sviluppo
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
