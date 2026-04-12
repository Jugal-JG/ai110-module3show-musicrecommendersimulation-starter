import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


# =============================================================================
# Data classes
# =============================================================================

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
    # --- Challenge 1: 5 new advanced attributes (defaults allow old test code to work) ---
    popularity: int = 50             # 0–100  chart/stream popularity score
    release_decade: str = "2020s"    # e.g. "2020s", "2010s", "2000s"
    mood_tags: List[str] = field(default_factory=list)  # detailed mood tags
    explicit: bool = False           # True if the track contains explicit content
    language: str = "english"        # primary language of the track


@dataclass
class UserProfile:
    """Represents a listener's taste preferences used to score songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # --- Challenge 1: extended user preferences ---
    min_popularity: int = 0         # only recommend songs at or above this popularity
    preferred_decade: str = ""      # e.g. "2020s" — bonus for era preference
    liked_mood_tags: List[str] = field(default_factory=list)  # detailed mood tag preferences
    explicit_ok: bool = True        # False = filter out explicit tracks


# =============================================================================
# OOP Recommender (used by tests)
# =============================================================================

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


# =============================================================================
# Functional API — Challenge 1: load_songs with new columns
# =============================================================================

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return dicts with all fields typed correctly.

    Challenge 1 additions:
      popularity     → int
      release_decade → str
      mood_tags      → List[str]  (split on comma from CSV)
      explicit       → bool
      language       → str
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":             int(row["id"]),
                "title":          row["title"],
                "artist":         row["artist"],
                "genre":          row["genre"],
                "mood":           row["mood"],
                "energy":         float(row["energy"]),
                "tempo_bpm":      float(row["tempo_bpm"]),
                "valence":        float(row["valence"]),
                "danceability":   float(row["danceability"]),
                "acousticness":   float(row["acousticness"]),
                # --- Challenge 1 new fields ---
                "popularity":     int(row["popularity"]),
                "release_decade": row["release_decade"],
                "mood_tags":      [t.strip() for t in row["mood_tags"].split(",")],
                "explicit":       row["explicit"].strip().lower() == "yes",
                "language":       row["language"].strip(),
            })
    return songs


# =============================================================================
# Challenge 1: score_song extended with new feature rules
# =============================================================================

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (numeric_score, reasons_list).

    Scoring recipe (max 10.5 with Challenge 1 additions):

    Original rules (max 7.5):
      +3.0  genre match
      +2.0  mood match
      +0.0–+1.5  energy proximity  =  1.5 × (1 − |target_energy − song.energy|)
      +1.0  acoustic bonus

    Challenge 1 new rules (max +3.0 additional):
      +1.0  popularity bonus  — song.popularity >= user_prefs["min_popularity"] + 20
                                rewards well-known tracks when the user prefers popular music
      +1.0  decade match      — song.release_decade == user_prefs["preferred_decade"]
      +1.0  mood tag overlap  — at least one of user_prefs["liked_mood_tags"] appears
                                in song["mood_tags"]

    Hard filters (applied before scoring — song is skipped entirely if it fails):
      explicit_ok=False  → explicit songs are excluded
      min_popularity     → songs below this threshold are excluded
    """
    total = 0.0
    reasons = []

    # --- Hard filter: explicit content ---
    if not user_prefs.get("explicit_ok", True) and song.get("explicit", False):
        return -1.0, ["filtered: explicit content"]

    # --- Hard filter: minimum popularity ---
    min_pop = user_prefs.get("min_popularity", 0)
    if song.get("popularity", 0) < min_pop:
        return -1.0, [f"filtered: popularity {song.get('popularity')} below minimum {min_pop}"]

    # --- Original scoring rules ---
    if song["genre"] == user_prefs.get("genre", ""):
        total += 3.0
        reasons.append("genre match (+3.0)")

    if song["mood"] == user_prefs.get("mood", ""):
        total += 2.0
        reasons.append("mood match (+2.0)")

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(target_energy - song["energy"])
    energy_pts = round(1.5 * (1.0 - energy_diff), 2)
    total += energy_pts
    reasons.append(f"energy proximity (+{energy_pts})")

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        total += 1.0
        reasons.append("acoustic bonus (+1.0)")

    # --- Challenge 1: popularity bonus ---
    # Reward songs that are at least 20 points above the user's minimum threshold,
    # capturing tracks that are genuinely popular (not just barely passing the filter).
    popularity_threshold = min_pop + 20
    if song.get("popularity", 0) >= popularity_threshold:
        total += 1.0
        reasons.append(f"popularity bonus (+1.0) — score {song['popularity']}")

    # --- Challenge 1: decade match ---
    preferred_decade = user_prefs.get("preferred_decade", "")
    if preferred_decade and song.get("release_decade", "") == preferred_decade:
        total += 1.0
        reasons.append(f"decade match (+1.0) — {song['release_decade']}")

    # --- Challenge 1: mood tag overlap ---
    liked_tags = set(user_prefs.get("liked_mood_tags", []))
    song_tags = set(song.get("mood_tags", []))
    matching_tags = liked_tags & song_tags
    if matching_tags:
        total += 1.0
        reasons.append(f"mood tag match (+1.0) — {', '.join(sorted(matching_tags))}")

    return round(total, 4), reasons


# =============================================================================
# Challenge 2: Multiple Scoring Modes — Strategy Pattern
# =============================================================================
# A "scoring mode" is a strategy that re-weights the four core factors
# (genre, mood, energy, acousticness) differently depending on what the user
# cares about most.  Adding a new mode means adding one entry to SCORING_MODES
# — no changes needed anywhere else in the codebase.

SCORING_MODES = {
    "genre-first": {
        # Default mode. Genre is the strongest signal — good for users who
        # exclusively listen to one or two genres.
        "genre_weight":  3.0,
        "mood_weight":   2.0,
        "energy_weight": 1.5,
        "acoustic_weight": 1.0,
        "description": "Genre-First: genre=3.0, mood=2.0, energy=1.5, acoustic=1.0",
    },
    "mood-first": {
        # Mood is the dominant factor. Good for users who hop between genres
        # but always want a specific emotional vibe (e.g. always want "chill"
        # regardless of whether it is lofi, jazz, or ambient).
        "genre_weight":  1.5,
        "mood_weight":   3.5,
        "energy_weight": 1.5,
        "acoustic_weight": 1.0,
        "description": "Mood-First: mood=3.5, genre=1.5, energy=1.5, acoustic=1.0",
    },
    "energy-focused": {
        # Energy proximity drives everything. Good for activity-based listening
        # (gym, study, sleep) where the physical feel of the music matters more
        # than genre or mood labels.
        "genre_weight":  1.0,
        "mood_weight":   1.0,
        "energy_weight": 4.0,
        "acoustic_weight": 1.0,
        "description": "Energy-Focused: energy=4.0, genre=1.0, mood=1.0, acoustic=1.0",
    },
}


def score_song_with_mode(user_prefs: Dict, song: Dict, mode: str = "genre-first") -> Tuple[float, List[str]]:
    """Score one song using the weights defined by the chosen scoring mode.

    Challenge 2 — Strategy Pattern:
      Accepts a mode key from SCORING_MODES. Each mode re-weights the four core
      factors without changing the structure of the scoring logic. This keeps the
      code modular: the caller (main.py) picks a strategy; the scorer applies it.

    Args:
        user_prefs: user preference dict
        song: song dict from load_songs()
        mode: one of "genre-first", "mood-first", "energy-focused"

    Returns:
        (score, reasons_list) tuple
    """
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown scoring mode '{mode}'. Choose from: {list(SCORING_MODES.keys())}")

    weights = SCORING_MODES[mode]
    total = 0.0
    reasons = []

    # Hard filters still apply regardless of mode
    if not user_prefs.get("explicit_ok", True) and song.get("explicit", False):
        return -1.0, ["filtered: explicit content"]
    min_pop = user_prefs.get("min_popularity", 0)
    if song.get("popularity", 0) < min_pop:
        return -1.0, [f"filtered: popularity {song.get('popularity')} below minimum {min_pop}"]

    # Core scoring with mode-specific weights
    gw = weights["genre_weight"]
    mw = weights["mood_weight"]
    ew = weights["energy_weight"]
    aw = weights["acoustic_weight"]

    if song["genre"] == user_prefs.get("genre", ""):
        total += gw
        reasons.append(f"genre match (+{gw})")

    if song["mood"] == user_prefs.get("mood", ""):
        total += mw
        reasons.append(f"mood match (+{mw})")

    target_energy = user_prefs.get("energy", 0.5)
    energy_diff = abs(target_energy - song["energy"])
    energy_pts = round(ew * (1.0 - energy_diff), 2)
    total += energy_pts
    reasons.append(f"energy proximity (+{energy_pts})")

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        total += aw
        reasons.append(f"acoustic bonus (+{aw})")

    # Challenge 1 bonus rules still apply in all modes
    popularity_threshold = min_pop + 20
    if song.get("popularity", 0) >= popularity_threshold:
        total += 1.0
        reasons.append(f"popularity bonus (+1.0) — score {song['popularity']}")

    preferred_decade = user_prefs.get("preferred_decade", "")
    if preferred_decade and song.get("release_decade", "") == preferred_decade:
        total += 1.0
        reasons.append(f"decade match (+1.0) — {song['release_decade']}")

    liked_tags = set(user_prefs.get("liked_mood_tags", []))
    song_tags = set(song.get("mood_tags", []))
    matching_tags = liked_tags & song_tags
    if matching_tags:
        total += 1.0
        reasons.append(f"mood tag match (+1.0) — {', '.join(sorted(matching_tags))}")

    return round(total, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = "genre-first") -> List[Tuple[Dict, float, List[str]]]:
    """Score every song with the chosen mode, filter negatives, sort descending, return top-k.

    Uses sorted() so the original catalog list is never mutated.
    """
    scored = [
        (song, *score_song_with_mode(user_prefs, song, mode))
        for song in songs
    ]
    # Remove songs that were hard-filtered (score == -1)
    scored = [(s, sc, r) for s, sc, r in scored if sc >= 0]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
