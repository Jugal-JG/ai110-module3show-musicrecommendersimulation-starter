"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# User Taste Profiles (Stress Test — Step 1)
#
# Profile critique (can these differentiate "intense rock" vs "chill lofi"?):
#   YES — genre + mood together create complete separation.
#   A rock/intense user scores rock songs +3.0+2.0 while lofi/chill scores 0.
#   The energy gap (0.91 vs 0.38) further separates them via proximity scoring.
#   Limitation: genre is an exact string match, so "pop" != "indie pop".
# ---------------------------------------------------------------------------

PROFILES = {
    "High-Energy Pop": {
        "genre":          "pop",
        "mood":           "happy",
        "energy":         0.90,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre":          "lofi",
        "mood":           "chill",
        "energy":         0.38,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre":          "rock",
        "mood":           "intense",
        "energy":         0.91,
        "likes_acoustic": False,
    },
    # Adversarial profile — conflicting preferences designed to stress-test
    # the scoring logic: very high energy but a sad/melancholic mood.
    # A real person might want to rage-listen or process emotions through
    # heavy music, but our system has no mood called "sad" in the catalog,
    # so the mood bonus will NEVER fire. This exposes the vocabulary gap.
    "Adversarial (high energy + sad mood)": {
        "genre":          "metal",
        "mood":           "sad",      # 'sad' does not exist in catalog moods
        "energy":         0.95,
        "likes_acoustic": False,
    },
}


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    """Run and print top-5 recommendations for one profile."""
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n{'=' * 60}")
    print(f"  PROFILE: {profile_name}")
    print(f"  genre={user_prefs['genre']!r}  mood={user_prefs['mood']!r}  "
          f"energy={user_prefs['energy']}  likes_acoustic={user_prefs['likes_acoustic']}")
    print("=" * 60)

    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  -  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print(f"       Score: {score:.2f} / 7.50")
        print(f"       Why:")
        for reason in reasons:
            print(f"         - {reason}")


def main() -> None:
    """Load catalog, run all profiles, and print ranked results for each."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for profile_name, user_prefs in PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs)

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
