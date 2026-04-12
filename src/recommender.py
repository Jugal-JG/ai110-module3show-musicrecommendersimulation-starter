import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """
        Scoring recipe (content-based filtering):
          +3.0  genre match
          +2.0  mood match
          +1.5  energy proximity  (1.5 * (1 - |target - song|))
          +1.0  acousticness bonus when user likes_acoustic and song.acousticness >= 0.6
        Max possible score = 7.5
        """
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
        scored = sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches your favorite ({song.genre})")

        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches your preference ({song.mood})")

        energy_diff = abs(user.target_energy - song.energy)
        if energy_diff <= 0.15:
            reasons.append(f"energy level ({song.energy:.2f}) is very close to your target ({user.target_energy:.2f})")
        elif energy_diff <= 0.35:
            reasons.append(f"energy level ({song.energy:.2f}) is reasonably close to your target ({user.target_energy:.2f})")

        if user.likes_acoustic and song.acousticness >= 0.6:
            reasons.append(f"has strong acoustic character ({song.acousticness:.2f})")

        if not reasons:
            return f"Partial match — score: {self._score(user, song):.2f}"

        return "Recommended because: " + "; ".join(reasons) + "."


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def _score_song(user_prefs: Dict, song: Dict) -> float:
    """
    Scoring recipe (functional version):
      +3.0  genre match
      +2.0  mood match
      +1.5  energy proximity  (1.5 * (1 - |target - song|))
      +1.0  acousticness bonus when user likes acoustic songs (acousticness >= 0.6)
    """
    score = 0.0

    if song["genre"] == user_prefs.get("genre", ""):
        score += 3.0

    if song["mood"] == user_prefs.get("mood", ""):
        score += 2.0

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(target_energy - song["energy"])
    score += 1.5 * (1.0 - energy_diff)

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        score += 1.0

    return round(score, 4)


def _explain_song(user_prefs: Dict, song: Dict) -> str:
    reasons = []

    if song["genre"] == user_prefs.get("genre", ""):
        reasons.append(f"genre matches ({song['genre']})")

    if song["mood"] == user_prefs.get("mood", ""):
        reasons.append(f"mood matches ({song['mood']})")

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(target_energy - song["energy"])
    if energy_diff <= 0.15:
        reasons.append(f"energy ({song['energy']:.2f}) is very close to your target ({target_energy:.2f})")
    elif energy_diff <= 0.35:
        reasons.append(f"energy ({song['energy']:.2f}) is reasonably close to target ({target_energy:.2f})")

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        reasons.append(f"strong acoustic feel ({song['acousticness']:.2f})")

    if not reasons:
        return "Partial match based on overall profile similarity."

    return "Because: " + "; ".join(reasons) + "."


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    Returns: list of (song_dict, score, explanation) tuples, sorted by score descending.
    """
    scored = [
        (song, _score_song(user_prefs, song), _explain_song(user_prefs, song))
        for song in songs
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
