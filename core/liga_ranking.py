import csv
import sys
from datetime import datetime, timedelta
from glicko2 import Player
import os
import glob

# =============================
# KONFIGURACJA STARTU LIGI I DEKOMPOZYCJI RANKINGU
# =============================
LEAGUE_START_DATE = datetime(2025, 4, 14, 0, 0)
DECAY_PER_DAY = 5  # przyrost RD za kazdy pelny tydzien nieaktywnosci

# =============================
# Przeliczenie wyniku na proporcje Glicko2
# =============================
def determine_result(dp1, dp2):
    total = dp1 + dp2
    if total == 0:
        return 0.5, 0.5
    return dp1 / total, dp2 / total

# =============================
# Wczytaj graczy z pliku rankingowego
# =============================
def load_rankings(filename):
    players = {}
    last_game_map = {}
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
    return players

# =============================
# Wczytaj historie meczow z pliku rankingowego
# =============================
def load_history(filename):
    history = []
    with open(filename, newline='') as f:
        lines = f.readlines()
        history_mode = False
        for line in lines:
            if line.strip().startswith("#history"):
                history_mode = True
                continue
            if history_mode:
                history.append(line.strip())
    return history

# =============================
# Zastosuj decay RD jesli gracz byl nieaktywny
# =============================
def apply_rd_decay(player, days_since_last_game):
    if days_since_last_game > 0:
        weeks_missed = days_since_last_game // 7
        player.rd += weeks_missed * DECAY_PER_DAY

# =============================
# Pomocnicza: znajdz date ostatniego meczu gracza
# =============================
def get_last_game_date(nick, history):
    relevant_dates = [
        datetime.strptime(line.split(',')[0], '%Y-%m-%d %H:%M:%S')
        for line in history
        if nick in (line.split(',')[1], line.split(',')[2])
    ]
    return max(relevant_dates) if relevant_dates else LEAGUE_START_DATE

# =============================
# Zapisz nowy ranking z historia i aktualnym stanem graczy
# =============================
def save_rankings(filename, players, history, now):
    decayed_players = set()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    out_filename = os.path.join("wyniki", f"ranking_{timestamp}.csv")
    with open(out_filename, 'w', newline='') as csvfile:
        fieldnames = ['nick', 'rating', 'rd', 'vol']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nick, player in players.items():
            if nick in sys.argv[1:3]:
                last_game_date = now
            else:
                last_game_date = get_last_game_date(nick, history)
            days_since = (now - last_game_date).days
            if nick not in decayed_players:
                apply_rd_decay(player, days_since)
                decayed_players.add(nick)
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

# =============================
# Znajdz najnowszy plik rankingowy
# =============================
def get_latest_ranking_file():
    ranking_files = glob.glob("wyniki/ranking_*.csv")
    if not ranking_files:
        return 'data/ranking_initial.csv'
    ranking_files.sort(key=os.path.getmtime, reverse=True)
    return ranking_files[0]

# =============================
# Glowna funkcja programu
# =============================
def main():
    if len(sys.argv) != 7:
        print(f"Uzycie: python {sys.argv[0]} gracz1 gracz2 dp1 dp2 mp1 mp2")
        return

    nick1, nick2 = sys.argv[1], sys.argv[2]
    dp1, dp2 = int(sys.argv[3]), int(sys.argv[4])
    mp1, mp2 = int(sys.argv[5]), int(sys.argv[6])

    if not (0 <= dp1 <= 20 and 0 <= dp2 <= 20):
        raise ValueError(f"Blad: duze punkty musza byc w zakresie 0–20. Otrzymano: {dp1}-{dp2} ({nick1} vs {nick2})")
    if dp1 + dp2 > 20:
        raise ValueError(f"Blad: suma duzych punktow nie moze przekraczac 20. Otrzymano: {dp1 + dp2} ({nick1} vs {nick2})")

    filename = get_latest_ranking_file()
    if not os.path.exists(filename):
        print(f"Plik {filename} nie istnieje.")
        return

    players = load_rankings(filename)
    history = load_history(filename)
    now = datetime.now()

    if nick1 not in players or nick2 not in players:
        print("Nie znaleziono jednego z graczy w rankingu.")
        return

    p1, p2 = players[nick1], players[nick2]
    result1, result2 = determine_result(dp1, dp2)

    rating1_before = p1.getRating()
    rating2_before = p2.getRating()

    p1.update_player([p2.getRating()], [p2.getRd()], [result1])
    p2.update_player([p1.getRating()], [p1.getRd()], [result2])

    rating1_after = p1.getRating()
    rating2_after = p2.getRating()

    diff1 = round(rating1_after - rating1_before, 2)
    diff2 = round(rating2_after - rating2_before, 2)

    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    new_entry = f"{timestamp},{nick1},{nick2},{dp1},{dp2},{mp1},{mp2}"
    history.append(new_entry)

    output_file = save_rankings(filename, players, history, now)

    print(f"Zarejestrowano gre pomiedzy {nick1} i {nick2} z wynikiem {dp1}-{dp2}.")
    print(f"{nick1} zdobywa {diff1} punktow rankingowych, {nick2} zdobywa {diff2}.")

if __name__ == '__main__':
    main()
