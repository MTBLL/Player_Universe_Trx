#!/usr/bin/env python
"""Analyze the pipeline results to generate interesting findings."""

import json
from collections import Counter, defaultdict
from pathlib import Path

def analyze_results():
    """Analyze the matched players data."""

    with open('.temp/matched_players.json', 'r') as f:
        matched = json.load(f)

    with open('.temp/unmatched_players.json', 'r') as f:
        unmatched = json.load(f)

    with open('.temp/ambiguous_matches.json', 'r') as f:
        ambiguous = json.load(f)

    findings = []

    # 1. Separate batters and pitchers
    batters = [p for p in matched if p.get('primary_position') not in ['SP', 'RP']]
    pitchers = [p for p in matched if p.get('primary_position') in ['SP', 'RP']]

    findings.append(f"## Overall Statistics\n")
    findings.append(f"- Total matched players: {len(matched)}")
    findings.append(f"  - Batters: {len(batters)}")
    findings.append(f"  - Pitchers: {len(pitchers)}")
    findings.append(f"- Unmatched: {len(unmatched)}")
    findings.append(f"- Ambiguous: {len(ambiguous)}")
    findings.append("")

    # 2. Analyze stat completeness for batters
    findings.append(f"## Batter Statistics Coverage\n")

    batters_with_stats = [b for b in batters if b.get('stats')]
    batters_with_espn = [b for b in batters_with_stats if b['stats'].get('AB')]
    batters_with_fg_proj = [b for b in batters_with_stats if b['stats'].get('proj_AB')]
    batters_with_savant = [b for b in batters_with_stats if b['stats'].get('exit_velo')]

    findings.append(f"- Batters with stats object: {len(batters_with_stats)} / {len(batters)} ({len(batters_with_stats)/len(batters)*100:.1f}%)")
    findings.append(f"- Batters with ESPN current season stats (AB field): {len(batters_with_espn)} / {len(batters)} ({len(batters_with_espn)/len(batters)*100:.1f}%)")
    findings.append(f"- Batters with FanGraphs projections (proj_AB): {len(batters_with_fg_proj)} / {len(batters)} ({len(batters_with_fg_proj)/len(batters)*100:.1f}%)")
    findings.append(f"- Batters with Savant data (exit_velo): {len(batters_with_savant)} / {len(batters)} ({len(batters_with_savant)/len(batters)*100:.1f}%)")
    findings.append("")

    # Count batters by stat source combination
    stat_patterns = Counter()
    for b in batters_with_stats:
        has_espn = bool(b['stats'].get('AB'))
        has_fg = bool(b['stats'].get('proj_AB'))
        has_savant = bool(b['stats'].get('exit_velo'))
        pattern = (has_espn, has_fg, has_savant)
        stat_patterns[pattern] += 1

    findings.append("### Batter Stat Source Combinations\n")
    pattern_names = {
        (True, True, True): "All 3 sources (ESPN + FG + Savant)",
        (True, True, False): "ESPN + FG only",
        (True, False, True): "ESPN + Savant only",
        (False, True, True): "FG + Savant only",
        (True, False, False): "ESPN only",
        (False, True, False): "FG only",
        (False, False, True): "Savant only",
        (False, False, False): "No stats (empty)",
    }

    for pattern, count in stat_patterns.most_common():
        name = pattern_names.get(pattern, str(pattern))
        findings.append(f"- {name}: {count} batters ({count/len(batters)*100:.1f}%)")
    findings.append("")

    # 3. Analyze stat completeness for pitchers
    findings.append(f"## Pitcher Statistics Coverage\n")

    pitchers_with_stats = [p for p in pitchers if p.get('stats')]
    pitchers_with_espn = [p for p in pitchers_with_stats if p['stats'].get('W')]
    pitchers_with_fg_proj = [p for p in pitchers_with_stats if p['stats'].get('proj_IP')]
    pitchers_with_savant = [p for p in pitchers_with_stats if p['stats'].get('swing_miss_pct')]

    findings.append(f"- Pitchers with stats object: {len(pitchers_with_stats)} / {len(pitchers)} ({len(pitchers_with_stats)/len(pitchers)*100:.1f}%)")
    findings.append(f"- Pitchers with ESPN current season stats (W field): {len(pitchers_with_espn)} / {len(pitchers)} ({len(pitchers_with_espn)/len(pitchers)*100:.1f}%)")
    findings.append(f"- Pitchers with FanGraphs projections (proj_IP): {len(pitchers_with_fg_proj)} / {len(pitchers)} ({len(pitchers_with_fg_proj)/len(pitchers)*100:.1f}%)")
    findings.append(f"- Pitchers with Savant data (swing_miss_pct): {len(pitchers_with_savant)} / {len(pitchers)} ({len(pitchers_with_savant)/len(pitchers)*100:.1f}%)")
    findings.append("")

    # Count pitchers by stat source combination
    stat_patterns_p = Counter()
    for p in pitchers_with_stats:
        has_espn = bool(p['stats'].get('W'))
        has_fg = bool(p['stats'].get('proj_IP'))
        has_savant = bool(p['stats'].get('swing_miss_pct'))
        pattern = (has_espn, has_fg, has_savant)
        stat_patterns_p[pattern] += 1

    findings.append("### Pitcher Stat Source Combinations\n")

    for pattern, count in stat_patterns_p.most_common():
        name = pattern_names.get(pattern, str(pattern))
        findings.append(f"- {name}: {count} pitchers ({count/len(pitchers)*100:.1f}%)")
    findings.append("")

    # 4. Find notable missing fields
    findings.append("## Notable Missing ESPN Fields\n")

    # Check if IP is missing from pitcher stats
    pitchers_with_w = [p for p in pitchers_with_espn if p['stats'].get('W')]
    pitchers_with_ip = [p for p in pitchers_with_espn if p['stats'].get('IP')]

    findings.append(f"- Pitchers have W (wins): {len(pitchers_with_w)}")
    findings.append(f"- Pitchers have IP (innings pitched): {len(pitchers_with_ip)}")
    findings.append(f"- **Investigation needed**: Why is IP missing from ESPN pitcher stats?")
    findings.append("")

    # 5. Top players by stat coverage
    findings.append("## Sample Players for Validation\n")

    # Find batters with all 3 sources
    complete_batters = [b for b in batters if b.get('stats') and
                       b['stats'].get('AB') and
                       b['stats'].get('exit_velo')]

    findings.append(f"### Batters with ESPN + Savant (top 5 by AB):\n")
    complete_batters.sort(key=lambda x: x['stats'].get('AB', 0), reverse=True)
    for b in complete_batters[:5]:
        findings.append(f"- {b['name']} ({b['primary_position']}): AB={b['stats']['AB']:.0f}, exit_velo={b['stats']['exit_velo']}, xwOBA={b['stats'].get('xwOBA')}")
    findings.append("")

    # Find pitchers with ESPN + Savant
    complete_pitchers = [p for p in pitchers if p.get('stats') and
                        p['stats'].get('W') and
                        p['stats'].get('swing_miss_pct')]

    findings.append(f"### Pitchers with ESPN + Savant (top 5 by W):\n")
    complete_pitchers.sort(key=lambda x: x['stats'].get('W', 0), reverse=True)
    for p in complete_pitchers[:5]:
        findings.append(f"- {p['name']} ({p['primary_position']}): W={p['stats']['W']:.0f}, ERA={p['stats'].get('ERA'):.2f}, swing_miss={p['stats']['swing_miss_pct']}%")
    findings.append("")

    # 6. Ambiguous match analysis
    findings.append("## Ambiguous Match Analysis\n")

    # Count candidates per ambiguous match
    candidate_counts = [len(a['candidates']) for a in ambiguous]
    avg_candidates = sum(candidate_counts) / len(candidate_counts) if candidate_counts else 0

    findings.append(f"- Total ambiguous matches: {len(ambiguous)}")
    findings.append(f"- Average candidates per ambiguous match: {avg_candidates:.1f}")
    findings.append(f"- Max candidates for a single player: {max(candidate_counts) if candidate_counts else 0}")
    findings.append("")

    # Sample ambiguous cases
    findings.append("### Sample Ambiguous Matches (first 3):\n")
    for a in ambiguous[:3]:
        player = a['player']
        candidates = a['candidates']
        findings.append(f"- **{player['name']}** ({player.get('pro_team', 'N/A')}) has {len(candidates)} candidates:")
        for c in candidates[:3]:  # Show first 3 candidates
            findings.append(f"  - {c['name']} ({c.get('team', 'N/A')})")
        findings.append("")

    # 7. Unmatched player analysis
    findings.append("## Unmatched Player Analysis\n")

    unmatched_batters = [p for p in unmatched if p.get('primary_position') not in ['SP', 'RP']]
    unmatched_pitchers = [p for p in unmatched if p.get('primary_position') in ['SP', 'RP']]

    findings.append(f"- Unmatched batters: {len(unmatched_batters)}")
    findings.append(f"- Unmatched pitchers: {len(unmatched_pitchers)}")
    findings.append("")

    # Sample unmatched
    findings.append("### Sample Unmatched Players (first 5):\n")
    for p in unmatched[:5]:
        findings.append(f"- {p['name']} ({p['primary_position']}, {p.get('pro_team', 'N/A')})")
    findings.append("")

    # 8. Key stats coverage summary
    findings.append("## Key Statistics Available\n")

    # Sample one complete batter
    if complete_batters:
        b = complete_batters[0]
        findings.append(f"### Sample Batter Stats ({b['name']}):\n")
        findings.append(f"**ESPN Current Season:**")
        findings.append(f"- AB: {b['stats'].get('AB')}, H: {b['stats'].get('H')}, HR: {b['stats'].get('HR')}")
        findings.append(f"- AVG: {b['stats'].get('AVG'):.3f}, OBP: {b['stats'].get('OBP'):.3f}, SLG: {b['stats'].get('SLG'):.3f}")
        findings.append(f"")
        findings.append(f"**Savant:**")
        findings.append(f"- Exit Velocity: {b['stats'].get('exit_velo')}")
        findings.append(f"- xwOBA: {b['stats'].get('xwOBA')}, xAVG: {b['stats'].get('xAVG')}, xSLG: {b['stats'].get('xSLG')}")
        findings.append(f"- Barrel %: {b['stats'].get('barrels_per_bbe_pct')}, Hard Hit %: {b['stats'].get('hardhit_pct')}")
        findings.append("")

    # Sample one complete pitcher
    if complete_pitchers:
        p = complete_pitchers[0]
        findings.append(f"### Sample Pitcher Stats ({p['name']}):\n")
        findings.append(f"**ESPN Current Season:**")
        findings.append(f"- W: {p['stats'].get('W')}, L: {p['stats'].get('L')}, ERA: {p['stats'].get('ERA'):.2f}")
        findings.append(f"- K: {p['stats'].get('K')}, BB: {p['stats'].get('BB')}, WHIP: {p['stats'].get('WHIP'):.2f}")
        findings.append(f"")
        findings.append(f"**Savant:**")
        findings.append(f"- Swing & Miss %: {p['stats'].get('swing_miss_pct')}")
        findings.append(f"- Whiff %: {p['stats'].get('whiff_pct')}, Chase %: {p['stats'].get('chase_pct')}")
        findings.append("")

    return "\n".join(findings)

if __name__ == "__main__":
    print("Analyzing results...")
    findings = analyze_results()

    output_file = Path(".temp/ANALYSIS_FINDINGS.md")
    output_file.write_text(findings)
    print(f"\nFindings written to: {output_file}")
    print("\n" + findings)
