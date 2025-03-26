
# Warhammer Liga Ranking (Glicko2)

System do zarządzania rankingiem graczy ligi Warhammer 40k na podstawie systemu **Glicko2**.

```bash
python core/liga_ranking.py player1 player2 18 2 75 25
```

- `player1`, `player2` — nicki graczy
- `18 2` — duże punkty
- `75 25` — małe punkty

System:
- Wczyta najnowszy ranking (lub `ranking_initial.csv`)
- Zaktualizuje ratingi i historię
- Zapisze nowy plik w `wyniki/ranking_YYYY-MM-DD_HH-MM-SS.csv`

---

### 🧪 Symulacja pełnej ligi:

```bash
python scripts/simulate_full_season.py
```

Wczyta plik `data/whole_liga_sim.csv`, przetworzy mecze chronologicznie i zapisze końcowy ranking do `wyniki/`.

---

## ✅ Walidacje bezpieczeństwa

- Duże punkty muszą być w zakresie `0–20`
- Suma dużych punktów = maks. `20`
- Gracze muszą istnieć w rankingu
- RD (odchylenie) rośnie, jeśli gracz nie gra przez więcej niż 7 dni

---

## 🗓️ Dostosowanie ligi

W `liga_ranking.py` można ustawić:

```python
LEAGUE_START_DATE = datetime(2025, 3, 24)
DECAY_THRESHOLD_DAYS = 7
DECAY_PER_DAY = 5
```

---

## 💡 Uwagi

- Historia meczów zapisywana jest pod `#history` w pliku CSV
- Możesz analizować dane ręcznie lub zbudować wykresy (np. w pandas/Excel)
