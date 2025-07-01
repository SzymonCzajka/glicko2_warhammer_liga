import csv
from glicko2symulacja import Player
from datetime import datetime
import os

# =============================
# PARAMETRY DEKOMPOZYCJI
# =============================
DECAY_PER_DAY = 0  # ustaw dowolnie np. 5 jeśli chcesz, albo 0

# =============================
# WCZYTAJ RANKING I OSTATNIE DATY
# =============================
def load_rankings(filename):
    players = {}
    last_played = {}

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['nick'].startswith('#history'):
                break
            players[row['nick']] = Player(
                rating=float(row['rating']),
                rd=float(row['rd']),
                vol=float(row['vol'])
            )
    return players, last_played

# =============================
# ZASTOSUJ DEKOMPOZYCJĘ RD
# =============================
def apply_rd_decay(player, days_since_last_game):
    if days_since_last_game > 0:
        weeks_missed = days_since_last_game // 7
        player.rd += weeks_missed * DECAY_PER_DAY

# =============================
# ZAPISZ NOWY RANKING Z HISTORIĄ
# =============================
def save_rankings(filename, players, history, last_played, now):
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    out_filename = os.path.join("wyniki", f"ranking_{timestamp}.csv")

    with open(out_filename, 'w', newline='') as csvfile:
        fieldnames = ['nick', 'rating', 'rd', 'vol']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for nick, player in players.items():
            writer.writerow({
                'nick': nick,
                'rating': round(player.getRating(), 2),
                'rd': round(player.getRd(), 2),
                'vol': round(player.vol, 15)
            })

        csvfile.write("#history\n")
        for line in history:
            csvfile.write(line + '\n')

    print(f"Zapisano ranking do pliku: {out_filename}")
    return out_filename
