📚 Flask Študijný Tracker

Táto aplikácia umožňuje zaznamenávať a spravovať študijné aktivity. Dáta sa ukladajú do PostgreSQL databázy a všetko beží v Docker kontajneroch.

📦 Štruktúra projektu

- 🐍 Flask aplikácia – obsluhuje webové rozhranie a API.
- 🐘 PostgreSQL databáza – ukladá študijné aktivity.
- 🐳 Docker Compose – zabezpečuje jednoduché spustenie celej infraštruktúry.

▶️ Spustenie aplikácie

1. Otvor PowerShell ako administrátor

Prejdi do priečinka, kde máš uložený projekt. Uisti sa, že máš spustený Docker Desktop.

2. Povolenie spúšťania skriptov

    Set-ExecutionPolicy Unrestricted -Scope Process

3. Príprava aplikácie

    ./prepare-app.ps1

4. Spustenie aplikácie

    ./start-app.ps1

5. Otvorenie webového rozhrania

    http://localhost:5000

6. Zastavenie aplikácie

    ./end-app.ps1

📈 Funkcionalita aplikácie

- Pridávanie študijných aktivít s témou, trvaním a dátumom.
- Automatický výpočet celkového času štúdia.
- Zobrazenie histórie štúdia.
- Vymazanie jednotlivých záznamov alebo celkovej histórie.
