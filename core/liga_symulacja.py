import csv
import sys
from glicko2 import Player

# Slownik graczy
players = {}

# Funkcja pomocnicza: dodaj gracza jeśli nie istnieje
def get_or_create_player(nick):
    if nick not in players:
        players[nick] = Player()
    return players[nick]

# Wczytaj plik CSV przekazany jako argument
if len(sys.argv) != 2:
    print("Użycie: python symulacja_glicko2.py <plik.csv>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        nick1 = row['p1']
        nick2 = row['p2']
        dp1 = int(row['dp1'])
        dp2 = int(row['dp2'])
        mp1 = int(row['mp1'])
        mp2 = int(row['mp2'])

        p1 = get_or_create_player(nick1)
        p2 = get_or_create_player(nick2)

        result1 = dp1 / (dp1 + dp2) if (dp1 + dp2) > 0 else 0.5
        result2 = dp2 / (dp1 + dp2) if (dp1 + dp2) > 0 else 0.5

        r1_before = round(p1.getRating(), 2)
        rd1_before = round(p1.getRd(), 2)
        vol1_before = round(p1.vol, 5)

        r2_before = round(p2.getRating(), 2)
        rd2_before = round(p2.getRd(), 2)
        vol2_before = round(p2.vol, 5)

        p1.update_player([p2.getRating()], [p2.getRd()], [result1])
        p2.update_player([p1.getRating()], [p1.getRd()], [result2])

        r1_after = round(p1.getRating(), 2)
        rd1_after = round(p1.getRd(), 2)
        vol1_after = round(p1.vol, 5)

        r2_after = round(p2.getRating(), 2)
        rd2_after = round(p2.getRd(), 2)
        vol2_after = round(p2.vol, 5)

        print(f"Gra nr {i}")
        print(f"wynik: {dp1} - {dp2}")
        print(f"{nick1} rating: {r1_before} -> {r1_after}  RD: {rd1_before} -> {rd1_after}  vol: {vol1_before} -> {vol1_after}")
        print(f"{nick2} rating: {r2_before} -> {r2_after}  RD: {rd2_before} -> {rd2_after}  vol: {vol2_before} -> {vol2_after}")
        print("\n------------------------------------------\n------------------------------------------\n")
