"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# Step 2: User Taste Profile
#
# This dictionary is the "taste profile" the recommender uses for comparisons.
# It defines a specific listener's preferences as target values for the
# features identified in data/songs.csv.
#
# Profile critique:
#   - Can it differentiate "intense rock" vs "chill lofi"?
#       YES — genre + mood together make those two profiles completely
#       distinct. A rock/intense user scores rock songs +3.0 (genre) +2.0
#       (mood), while lofi/chill songs score 0 on both. The energy gap
#       (0.9 vs 0.4) adds further separation via the energy proximity term.
#   - Is it too narrow?
#       Somewhat. Because genre is a string match, a user whose favorite
#       genre is "pop" gets 0 genre points for "indie pop" even though those
#       are musically similar. The profile also captures only one mood at a
#       time — a user who enjoys both "happy" and "chill" moods cannot
#       express that nuance here.
# ---------------------------------------------------------------------------

user_prefs = {
    "genre":         "pop",    # favorite_genre  — string match, +3.0 pts
    "mood":          "happy",  # favorite_mood   — string match, +2.0 pts
    "energy":        0.80,     # target_energy   — float 0-1, proximity scored
    "likes_acoustic": False,   # acoustic bonus  — +1.0 if True & acousticness >= 0.6
}


def main() -> None:
    songs = load_songs("data/songs.csv")

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        song, score, explanation = rec
        print(f"{song['title']} by {song['artist']} ({song['genre']}, {song['mood']}) — Score: {score:.2f}")
        print(f"  {explanation}")
        print()


if __name__ == "__main__":
    main()
