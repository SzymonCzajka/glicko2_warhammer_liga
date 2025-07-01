import csv
import sys
from datetime import datetime
from glicko2 import Player
import os
import glob

# Parametry Glicko2
TAU = 0.3
INITIAL_RD = 250
MIN_RD = 130

# Modyfikatory za różnice ratingów
BONUS_HIGH = 1.1
BONUS_VERY_HIGH = 1.2
PENALTY_LOW = 0.9
PENALTY_VERY_LOW = 0.8
RATING_THRESHOLD_1 = 50
RATING_THRESHOLD_2 = 100

# Modyfikatory za liczbę gier w miesiącu
GAMES_THRESHOLD_1 = 3
GAMES_THRESHOLD_2 = 6
GAMES_BONUS_1 = 0.75
GAMES_BONUS_2 = 0.5

# Data startu ligi
LEAGUE_START_DATE = datetime(2025, 4, 14, 0, 0)

# Wynik Glicko2
def determine_result(dp1, dp2):
    total = dp1 + dp2
    if total == 0:
        return 0.5, 0.5
    return dp1 / total, dp2 / total

# Wczytaj ranking
def load_rankings(filename):
    players = {}
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

# Wczytaj historię
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

# Zlicz mecze gracza w miesiącu
def count_games_in_month(nick, history, now):
    count = 0
    for line in history:
        parts = line.split(',')
        date = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
        if parts[1] == nick or parts[2] == nick:
            if date.year == now.year and date.month == now.month:
                count += 1
    return count

# Sprawdź, czy para grała w miesiącu
def pair_played_this_month(nick1, nick2, history, now):
    for line in history:
        parts = line.split(',')
        date = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
        if (parts[1] == nick1 and parts[2] == nick2) or (parts[1] == nick2 and parts[2] == nick1):
            if date.year == now.year and date.month == now.month:
                return True
    return False

# Znajdź najnowszy plik rankingowy
def get_latest_ranking_file():
    ranking_files = glob.glob("wyniki/ranking_*.csv")
    if not ranking_files:
        return 'data/ranking_initial.csv'
    ranking_files.sort(key=os.path.getmtime, reverse=True)
    return ranking_files[0]

# Zapisz ranking
def save_rankings(filename, players, history, now):
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    out_filename = os.path.join("wyniki", f"ranking_{timestamp}.csv")
    with open(out_filename, 'w', newline='') as csvfile:
        fieldnames = ['nick', 'rating', 'rd', 'vol']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for nick, player in players.items():
            writer.writerow({
                'nick': nick,
                'rating': round(player.rating, 2),
                'rd': round(player.rd, 2),
                'vol': round(player.vol, 15)
            })
        csvfile.write("#history\n")
        for line in history:
            csvfile.write(line + '\n')
    print(f"Zapisano ranking do pliku: {out_filename}")
    return out_filename

# Główna funkcja
def main():
    if len(sys.argv) < 7:
        print(f"Użycie: python {sys.argv[0]} gracz1 gracz2 dp1 dp2 mp1 mp2 [tag]")
        return

    nick1, nick2 = sys.argv[1], sys.argv[2]
    dp1, dp2 = int(sys.argv[3]), int(sys.argv[4])
    mp1, mp2 = int(sys.argv[5]), int(sys.argv[6])
    tag = sys.argv[7] if len(sys.argv) > 7 else ""

    filename = get_latest_ranking_file()
    players = load_rankings(filename)
    history = load_history(filename)
    now = datetime.now()

    if nick1 not in players or nick2 not in players:
        print("Nie znaleziono jednego z graczy w rankingu.")
        return

    if not (tag == "wieczorek" or tag == "turniej"):
        if pair_played_this_month(nick1, nick2, history, now):
            print("Ci gracze już grali ze sobą w tym miesiącu.")
            return

    result1, result2 = determine_result(dp1, dp2)
    p1, p2 = players[nick1], players[nick2]

    rating1_before = p1.rating
    rating2_before = p2.rating

    p1.update_player([p2.rating], [p2.rd], [result1])
    p2.update_player([p1.rating], [p1.rd], [result2])

    diff1_czysty = p1.rating - rating1_before
    diff2_czysty = p2.rating - rating2_before

    diff1 = diff1_czysty
    diff2 = diff2_czysty

    diff = abs(rating1_before - rating2_before)
    if diff >= RATING_THRESHOLD_2:
        if rating1_before > rating2_before:
            # p1 mocniejszy
            diff1 *= PENALTY_VERY_LOW if diff1 > 0 else BONUS_VERY_HIGH
            diff2 *= BONUS_VERY_HIGH if diff2 > 0 else PENALTY_VERY_LOW
        else:
            # p2 mocniejszy
            diff1 *= BONUS_VERY_HIGH if diff1 > 0 else PENALTY_VERY_LOW
            diff2 *= PENALTY_VERY_LOW if diff2 > 0 else BONUS_VERY_HIGH

    games1 = count_games_in_month(nick1, history, now)
    games2 = count_games_in_month(nick2, history, now)

    if games1 >= GAMES_THRESHOLD_2:
        diff1 *= GAMES_BONUS_2
    elif games1 >= GAMES_THRESHOLD_1:
        diff1 *= GAMES_BONUS_1

    if games2 >= GAMES_THRESHOLD_2:
        diff2 *= GAMES_BONUS_2
    elif games2 >= GAMES_THRESHOLD_1:
        diff2 *= GAMES_BONUS_1

    print(f"CZYSTY GLICKO: {nick1}: {diff1_czysty:.2f}, {nick2}: {diff2_czysty:.2f}")
    print(f"PO WSZYSTKIM: {nick1}: {diff1:.2f}, {nick2}: {diff2:.2f}")

    p1.rating = rating1_before + diff1
    p2.rating = rating2_before + diff2

    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    new_entry = f"{timestamp},{nick1},{nick2},{dp1},{dp2},{mp1},{mp2}"
    history.append(new_entry)

    save_rankings(filename, players, history, now)

    print(f"ZAREJESTROWANO: {nick1} zmiana: {round(diff1, 2)} | {nick2} zmiana: {round(diff2, 2)}")

if __name__ == '__main__':
    main()
