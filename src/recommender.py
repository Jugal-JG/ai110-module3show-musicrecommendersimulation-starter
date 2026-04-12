import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a single song and all its audio/metadata attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a listener's taste preferences used to score songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Content-based recommender that scores and ranks songs against a UserProfile."""

    def __init__(self, songs: List[Song]):
        """Store the song catalog for later scoring."""
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Return a numeric match score (0–7.5) for one song against one user profile."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 3.0
        if song.mood == user.favorite_mood:
            score += 2.0
        energy_diff = abs(user.target_energy - song.energy)
        score += 1.5 * (1.0 - energy_diff)
        if user.likes_acoustic and song.acousticness >= 0.6:
            score += 1.0
        return round(score, 4)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by descending match score."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable sentence listing why a song was recommended."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({song.mood})")
        energy_diff = abs(user.target_energy - song.energy)
        if energy_diff <= 0.15:
            reasons.append(f"energy ({song.energy:.2f}) is very close to your target ({user.target_energy:.2f})")
        elif energy_diff <= 0.35:
            reasons.append(f"energy ({song.energy:.2f}) is reasonably close to your target ({user.target_energy:.2f})")
        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"has strong acoustic character ({song.acousticness:.2f})")
        if not reasons:
            return f"Partial match — score: {self._score(user, song):.2f}"
        return "Recommended because: " + "; ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Functional API  (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read data/songs.csv and return a list of song dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (numeric_score, reasons_list).

    The reasons list contains strings like 'genre match (+3.0)' so callers can
    display exactly which factors contributed to the final score.

    Scoring recipe (max 7.5):
      +3.0  genre match
      +2.0  mood match
      +0.0–+1.5  energy proximity  =  1.5 × (1 − |target_energy − song.energy|)
      +1.0  acoustic bonus  (only when likes_acoustic=True and acousticness ≥ 0.6)
    """
    total = 0.0
    reasons = []

    # Genre match
    if song["genre"] == user_prefs.get("genre", ""):
        total += 3.0
        reasons.append("genre match (+3.0)")

    # Mood match
    if song["mood"] == user_prefs.get("mood", ""):
        total += 2.0
        reasons.append("mood match (+2.0)")

    # Energy proximity
    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(target_energy - song["energy"])
    energy_pts = round(1.5 * (1.0 - energy_diff), 2)
    total += energy_pts
    reasons.append(f"energy proximity (+{energy_pts})")

    # Acoustic bonus
    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        total += 1.0
        reasons.append("acoustic bonus (+1.0)")

    return round(total, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """Score every song with score_song, sort by score descending, return top-k results.

    Uses sorted() (returns a new list) rather than .sort() (mutates in place) so
    the original catalog is never reordered.

    Returns a list of (song_dict, score, reasons_list) tuples.

    Why sorted() and not .sort()?
      .sort()   — mutates the original list in place, returns None.
      sorted()  — leaves the original list untouched, returns a new sorted list.
    Here we use sorted() so the caller's song catalog is never accidentally reordered.
    """
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
