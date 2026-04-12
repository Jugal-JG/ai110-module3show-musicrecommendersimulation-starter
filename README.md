# Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project simulates a **content-based music recommender**. Given a user's taste profile (preferred genre, mood, and target energy level), the system scores every song in the catalog and returns the top matches. It is a simplified version of the kind of "because you liked X" logic used by real streaming platforms, built to make the underlying math transparent and easy to experiment with.

---

## How The System Works

Real-world streaming platforms like Spotify or YouTube use two main strategies to surface new music. **Collaborative filtering** says "people who liked the same songs you did also liked these — so you probably will too." **Content-based filtering** says "you like energetic pop with a happy vibe, so let's find songs that actually have those attributes." This simulation uses content-based filtering because it is transparent: you can read the scoring formula and understand exactly why a song was recommended. The system prioritizes genre and mood alignment first (the strongest signals of taste), then rewards songs whose energy level is close to the user's target, and finally gives a bonus to acoustic tracks for users who prefer that texture.

### `Song` features used

| Feature | Type | Role in scoring |
|---|---|---|
| `genre` | string | +3.0 points if it matches the user's favorite genre |
| `mood` | string | +2.0 points if it matches the user's favorite mood |
| `energy` | float 0–1 | +up to 1.5 points based on proximity to user's target energy |
| `acousticness` | float 0–1 | +1.0 bonus if user likes acoustic songs and song acousticness >= 0.6 |
| `title`, `artist` | string | display only |
| `tempo_bpm`, `valence`, `danceability` | float | stored but not used in scoring (available for future experiments) |

### `UserProfile` fields

| Field | Type | Meaning |
|---|---|---|
| `favorite_genre` | string | The genre the user most wants to hear |
| `favorite_mood` | string | The mood/vibe the user is looking for |
| `target_energy` | float 0–1 | How energetic the user wants the music to feel |
| `likes_acoustic` | bool | Whether the user has a preference for acoustic-heavy tracks |

### Scoring formula (per song)

```
score = genre_match * 3.0
      + mood_match * 2.0
      + 1.5 * (1 - |target_energy - song.energy|)
      + acoustic_bonus * 1.0   # only if likes_acoustic=True and acousticness >= 0.6
```

Songs are ranked by score descending; the top `k` are returned as recommendations.

### Why we need both a Scoring Rule and a Ranking Rule

A **Scoring Rule** answers the question: *"How good is this one song for this one user?"* It takes a single song and a user profile and returns a number. On its own, a scoring rule cannot make a recommendation — it has no awareness of other songs in the catalog.

A **Ranking Rule** answers the question: *"Given all the songs, which ones should I actually show?"* It applies the scoring rule to every song in the catalog, collects all the scores, and sorts them so the best matches rise to the top. It then picks the top `k` to return.

You need both because they solve different sub-problems:

| | Scoring Rule | Ranking Rule |
|---|---|---|
| Input | one song + one user | all songs + one user |
| Output | a single number (score) | an ordered list of songs |
| Question answered | "Is this song a good match?" | "Which songs are the best matches?" |
| Code location | `Recommender._score()` / `_score_song()` | `Recommender.recommend()` / `recommend_songs()` |

Without the Scoring Rule, the Ranking Rule has nothing to sort by. Without the Ranking Rule, the Scoring Rule can only evaluate one song at a time and never produces a useful recommendation list. Together they form the complete pipeline: **score every song → sort → return top-k**.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

- **Reducing the genre weight from 3.0 to 1.0**: The top results started mixing genres more freely. A "pop/happy" user got lofi and indie pop songs almost as often as pure pop, since mood and energy now dominated. This felt less precise but more "serendipitous."
- **Adding an energy bonus for songs within 0.05 of the target**: Results became very narrow — only 2–3 songs qualified for the top slots. This showed that being too strict on one feature collapses diversity.
- **Testing a "chill/focused" lofi user**: The system correctly bubbled up *Library Rain*, *Focus Flow*, and *Midnight Coding* as top 3 — which matched intuition well.
- **Testing a high-energy gym profile (genre=pop, mood=intense, energy=0.93)**: *Gym Hero* scored 7.5/7.5 (perfect match). *Storm Runner* ranked second despite being rock, because its energy (0.91) was very close to the target. This is correct behavior — energy proximity partially compensated for the genre mismatch.

---

## Limitations and Risks

- **Tiny catalog**: With only 10 songs, results are easy to predict and there is almost no diversity pressure.
- **No collaborative signal**: The system never learns from what other users liked — a cold-start problem for new users with unusual tastes.
- **Genre mismatch penalty is hard**: If your favorite genre is not in the catalog (e.g., "country"), no song ever scores the genre bonus, skewing all recommendations toward energy/mood.
- **Binary acoustic preference**: `likes_acoustic` is a simple boolean; in reality, acoustic preference is a spectrum.
- **No novelty or diversity control**: The recommender can return very similar songs back-to-back (e.g., all lofi tracks for a chill user).
- **No temporal context**: It does not consider time of day, activity, or listening history.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this simulation made it clear that a recommender is essentially a translation machine: it converts raw attributes (numbers and labels) into a ranked opinion about what you might enjoy. The tricky part is not the math — it is deciding *which* attributes to weight and *how much*. Giving genre triple the weight of energy encodes a belief that genre is the strongest signal of taste, but that assumption may be completely wrong for someone who listens across many genres but always wants low-energy music. Every weight is a design choice, and design choices can carry bias.

The bias angle was the most surprising part. Because this catalog skews toward pop, lofi, and indie sounds, a user who prefers jazz or hip-hop will systematically receive lower-scoring (and less relevant) recommendations. The system is not explicitly biased against jazz fans, but the data gap produces the same effect. Real platforms face this too: if engagement data mostly comes from certain demographics, the model quietly learns to serve those demographics better, creating a feedback loop where underrepresented tastes are never surfaced and therefore never clicked, confirming the model's low estimate of their popularity.
