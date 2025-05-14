import json
from pprint import pprint

def analyze_player_file(filename, output_filename):
    # Read the players file
    with open(f"output/{filename}", "r") as f:
        players = json.load(f)

    # Filter for active players
    active_players = [player for player in players if player.get("status") == "active"]

    # Print the count and list of active players
    print(f"Total {filename.replace('.json', '')} players: {len(players)}")
    print(f"Active {filename.replace('.json', '')} players: {len(active_players)}")
    print(f"\nList of active {filename.replace('.json', '')} players:")
    for player in active_players:
        team = player.get("team", player.get("pro_team", "N/A"))
        print(f"- {player.get('name', 'N/A')} ({team})")

    # Save the active players to a file
    with open(f"output/{output_filename}", "w") as f:
        json.dump(active_players, f, indent=2)

    print(f"\nSaved active players to output/{output_filename}")

    return active_players

# Analyze unmatched players
print("=== ANALYZING UNMATCHED PLAYERS ===")
unmatched_active = analyze_player_file("unmatched_players.json", "active_unmatched_players.json")

# Analyze ambiguous matches
print("\n=== ANALYZING AMBIGUOUS MATCHES ===")
ambiguous_active = analyze_player_file("ambiguous_matches.json", "active_ambiguous_players.json")

# Combined summary
print("\n=== SUMMARY ===")
print(f"Total active players needing attention: {len(unmatched_active) + len(ambiguous_active)}")