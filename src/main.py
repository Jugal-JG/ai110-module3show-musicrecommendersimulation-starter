"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs, SCORING_MODES


# ---------------------------------------------------------------------------
# User Taste Profiles
#
# Challenge 1 additions:
#   min_popularity   — filter out songs below this popularity score
#   preferred_decade — bonus points for matching era
#   liked_mood_tags  — bonus points for matching detailed mood tags
#   explicit_ok      — hard filter; False removes explicit tracks
#
# Profile critique (can these differentiate "intense rock" vs "chill lofi"?):
#   YES — genre + mood + energy all diverge completely between those two profiles.
#   Limitation: genre is exact string matching, so "pop" != "indie pop".
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre":           "pop",
        "mood":            "happy",
        "energy":          0.90,
        "likes_acoustic":  False,
        # Challenge 1 preferences
        "min_popularity":  60,
        "preferred_decade": "2020s",
        "liked_mood_tags": ["upbeat", "feel-good", "euphoric"],
        "explicit_ok":     True,
    },
    "Chill Lofi": {
        "genre":           "lofi",
        "mood":            "chill",
        "energy":          0.38,
        "likes_acoustic":  True,
        # Challenge 1 preferences
        "min_popularity":  0,
        "preferred_decade": "2020s",
        "liked_mood_tags": ["calm", "studious", "ambient"],
        "explicit_ok":     True,
    },
    "Deep Intense Rock": {
        "genre":           "rock",
        "mood":            "intense",
        "energy":          0.91,
        "likes_acoustic":  False,
        # Challenge 1 preferences
        "min_popularity":  50,
        "preferred_decade": "2010s",
        "liked_mood_tags": ["aggressive", "powerful", "driving"],
        "explicit_ok":     False,   # no explicit tracks
    },
    # Adversarial: mood not in catalog — exposes silent failure
    "Adversarial (high energy + sad mood)": {
        "genre":           "metal",
        "mood":            "sad",
        "energy":          0.95,
        "likes_acoustic":  False,
        "min_popularity":  0,
        "preferred_decade": "",
        "liked_mood_tags": ["dark"],
        "explicit_ok":     True,
    },
}


def print_recommendations(profile_name: str, user_prefs: dict, songs: list,
                           mode: str = "genre-first") -> None:
    """Run and print top-5 recommendations for one profile with the chosen mode."""
    recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)
    mode_desc = SCORING_MODES[mode]["description"]

    print(f"\n{'=' * 62}")
    print(f"  PROFILE : {profile_name}")
    print(f"  MODE    : {mode_desc}")
    print("=" * 62)

    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  "
              f"|  Energy: {song['energy']}  |  Popularity: {song['popularity']}")
        print(f"       Decade: {song['release_decade']}  "
              f"|  Tags: {', '.join(song['mood_tags'])}")
        print(f"       Score: {score:.2f}")
        for reason in reasons:
            print(f"         - {reason}")


def main() -> None:
    """Load catalog, run each profile across all 3 scoring modes, print results."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring modes available: {', '.join(SCORING_MODES.keys())}")

    # --- Challenge 2: run each profile under all 3 scoring modes ---
    for profile_name, user_prefs in PROFILES.items():
        for mode in SCORING_MODES:
            print_recommendations(profile_name, user_prefs, songs, mode=mode)

    print(f"\n{'=' * 62}")


if __name__ == "__main__":
    main()
