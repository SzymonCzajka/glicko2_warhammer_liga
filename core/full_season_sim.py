import csv
from datetime import datetime
from glicko2symulacja import Player
from liga_ranking_symulacja import load_rankings, apply_rd_decay, save_rankings

# Plik startowy i plik z meczami
initial_ranking_file = "data/ranking_initial.csv"
match_csv_file = "data/whole_liga_sim.csv"

# Wczytaj ranking i mapę ostatnich gier
players, last_played = load_rankings(initial_ranking_file)

# Wczytaj wszystkie mecze
with open(match_csv_file, newline='') as f:
    reader = csv.DictReader(f)
    matches = list(reader)

history = []

for row in matches:
    date = datetime.strptime(row['date'], '%Y-%m-%d')
    p1_nick, p2_nick = row['p1'], row['p2']
    dp1, dp2 = int(row['dp1']), int(row['dp2'])
    mp1, mp2 = int(row['mp1']), int(row['mp2'])

    if not (0 <= dp1 <= 20 and 0 <= dp2 <= 20):
        raise ValueError(f"Błąd: punkty muszą być 0–20. {dp1}-{dp2}")

    if dp1 + dp2 > 20:
        raise ValueError(f"Błąd: suma punktów > 20. {dp1 + dp2}")

    for nick in (p1_nick, p2_nick):
        if nick not in last_played:
            last_played[nick] = date

    if p1_nick not in players:
        players[p1_nick] = Player()
    if p2_nick not in players:
        players[p2_nick] = Player()

    # Decay
    days1 = (date - last_played[p1_nick]).days
    days2 = (date - last_played[p2_nick]).days
    apply_rd_decay(players[p1_nick], days1)
    apply_rd_decay(players[p2_nick], days2)

    last_played[p1_nick] = date
    last_played[p2_nick] = date

    total = dp1 + dp2
    result1 = dp1 / total if total else 0.5
    result2 = dp2 / total if total else 0.5

    p1 = players[p1_nick]
    p2 = players[p2_nick]

    rating1_before = p1.getRating()
    rating2_before = p2.getRating()

    p1.update_player([p2.getRating()], [p2.getRd()], [result1])
    p2.update_player([p1.getRating()], [p1.getRd()], [result2])

    diff1 = round(p1.getRating() - rating1_before, 2)
    diff2 = round(p2.getRating() - rating2_before, 2)

    print(f"{p1_nick} zmiana: {diff1} | {p2_nick} zmiana: {diff2}")

    timestamp = date.strftime('%Y-%m-%d %H:%M:%S')
    history.append(f"{timestamp},{p1_nick},{p2_nick},{dp1},{dp2},{mp1},{mp2}")

final_date = max(datetime.strptime(row['date'], '%Y-%m-%d') for row in matches)

output_file = save_rankings(initial_ranking_file, players, history, last_played, final_date)

print("Symulacja zakończona.")
print(f"Ranking końcowy zapisany: {output_file}")
