# 📤 Instrukcje wysyłania projektu na GitHub

## ✅ Co już przygotowałem:

- ✓ **README.md** - Pełna dokumentacja projektu w formacie Markdown
- ✓ **LICENSE** - Licencja MIT
- ✓ **.gitignore** - Konfiguracja ignorowania plików

---

## 🚀 Kroki do wysłania na GitHub:

### Krok 1: Inicjalizacja repozytorium

```powershell
cd c:\Users\Administrator\Desktop\LISTA_LAB5\lab5
git init
```

### Krok 2: Dodanie wszystkich plików

```powershell
git add .
```

### Krok 3: Pierwszy commit

```powershell
git commit -m "Initial commit: LAB5 Data Extraction Project"
```

### Krok 4: Dodanie remote repozytorium

Przejdź do GitHub.com i stwórz nowe repozytorium o nazwie `lab5` (bez inicjalizacji).

Potem wykonaj:

```powershell
git branch -M main
git remote add origin https://github.com/TWOJA_NAZWA/lab5.git
git push -u origin main
```

**Zastąp `TWOJA_NAZWA` swoją nazwą użytkownika GitHub!**

---

## 📋 Pliki wysyłane na GitHub:

### Ważne pliki:
- `README.md` - Dokumentacja ✓
- `requirements.txt` - Zależności Python
- `sql_extract.py` - Główny skrypt
- `show_results.py` - Wyświetlanie rezultatów
- `LICENSE` - Licencja MIT

### Dane testowe:
- `SBI2526-LAB-Rating-FixedDate.csv` - Oceny produktów
- `Identyfikacja tabel.txt` - Opis źródeł

### Pomoc:
- `RAPORT_LAB5.txt` - Pełny raport (backup)
- `INSTRUKCJA_POWERBI.txt` - Instrukcje Power BI

### Ignorowane pliki (NIE będą wysyłane):
- `venv312/` - Virtual environment
- `__pycache__/` - Python cache
- `.dlt/` - Konfiguracja (zawiera hasła!)
- `*.pyc` - Compiled Python
- `.env` - Zmienne środowiskowe

---

## 🔐 WAŻNE: Bezpieczeństwo

### ⚠️ Hasła w kodzie?

Plik `.dlt/secrets.toml` zawiera hasła do bazy danych.  
**NIE wysyłaj go na GitHub!** Jest już w `.gitignore`.

**Jeśli już wysłałeś:**
```powershell
git rm --cached .dlt/secrets.toml
git commit -m "Remove secrets from history"
```

---

## ✨ Opcjonalne: Ulepsz README

### Badge'i (dodaj na górę README.md):

```markdown
![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
```

### GitHub Topics (na stronie repozytorium):
- `data-extraction`
- `etl`
- `dlt`
- `sql-server`
- `python`
- `powerbi`

---

## 🔄 Po wysłaniu

### Aktualizacja (jeśli zmienisz coś lokalnie):

```powershell
git add .
git commit -m "Opis zmian"
git push origin main
```

### Ściągnięcie zmian (jeśli pracujesz z innego komputera):

```powershell
git clone https://github.com/TWOJA_NAZWA/lab5.git
cd lab5
pip install -r requirements.txt
```

---

## 📖 Jak zdać projekt

1. Wyślij URL repozytorium na GitHub:
   ```
   https://github.com/TWOJA_NAZWA/lab5
   ```

2. Upewnij się, że public (widoczne):
   - Settings → Visibility → Public ✓

3. Podziel link w raporcie:
   ```markdown
   **GitHub Repository:** https://github.com/TWOJA_NAZWA/lab5
   ```

---

## ❓ Szybkie polecenia

```powershell
# Sprawdź status
git status

# Zobacz historię commitów
git log --oneline

# Wyświetl ostatnie zmiany
git diff

# Cofnij ostatni commit (jeśli błąd)
git reset --soft HEAD~1
```

---

**Powodzenia! 🚀** Projekt jest gotowy do GitHub.
