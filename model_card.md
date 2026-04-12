# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender simulation built for classroom exploration.

---

## 2. Intended Use

This system suggests up to 5 songs from a small 10-song catalog based on a user's preferred genre, mood, and energy level. It is designed for **classroom exploration only** — to make the logic of a recommender system transparent and easy to experiment with. It is not intended for production use or real users.

Assumptions the model makes:
- The user can be described by a single genre preference, a single mood preference, and a target energy level.
- All songs in the catalog are equally "available" to recommend (no licensing, popularity, or recency weighting).
- A higher score always means a better recommendation for that user.

---

## 3. How the Model Works

Imagine you walk into a record store and tell the clerk: "I love pop music, I'm in a happy mood, and I want something high-energy." The clerk mentally scans the shelves and picks records that best match your description.

VibeFinder 1.0 does the same thing with numbers. For each song in the catalog, it calculates a **score** between 0 and 7.5 by asking four questions:

1. **Does the genre match?** If yes, add 3 points. Genre is weighted highest because it is the strongest signal of musical taste.
2. **Does the mood match?** If yes, add 2 points. Mood is the second-strongest signal — you generally know whether you want something upbeat or melancholy.
3. **How close is the energy?** Energy runs from 0 (very quiet/calm) to 1 (very intense). The closer the song's energy is to what the user wants, the more points it earns — up to 1.5 points for a perfect match.
4. **Does the user like acoustic music?** If yes and the song has a strong acoustic character, add 1 bonus point.

After scoring every song, the system sorts them from highest to lowest score and returns the top results.

---

## 4. Data

The catalog is stored in `data/songs.csv` and contains **10 songs**.

| Attribute | Values present |
|---|---|
| Genres | pop (2), lofi (2), rock (1), ambient (1), jazz (1), synthwave (1), indie pop (1) |
| Moods | happy (2), chill (2), intense (2), relaxed (1), moody (1), focused (1) |
| Energy range | 0.28 (Spacewalk Thoughts) – 0.93 (Gym Hero) |

No songs were added or removed from the starter dataset.

**Gaps in the data:**
- No hip-hop, R&B, classical, country, or electronic dance music.
- Only one jazz track and one ambient track — these genres are severely underrepresented.
- All songs appear to reflect a Western, English-speaking music perspective. Non-Western music styles are absent entirely.
- The mood vocabulary is limited; nuanced moods like "nostalgic," "anxious," or "romantic" are missing.
- Whose taste shaped this catalog is unclear, but the genre distribution suggests a bias toward a younger, Western listener.

---

## 5. Strengths

- **Transparency**: The scoring formula is simple enough to explain in one sentence. A user or auditor can always understand *why* a song was recommended.
- **Deterministic**: Given the same user profile, the system always returns the same results — no randomness or unexplained variation.
- **Works well for mainstream profiles**: A pop/happy/high-energy user receives highly relevant results (e.g., *Sunrise City*, *Gym Hero*) that clearly match their stated preferences.
- **Energy proximity is nuanced**: Rather than a binary "energy matches / doesn't match," the formula rewards closeness on a continuous scale, which captures the gradual nature of energy preference well.
- **Good for chill/lofi users**: The catalog has a solid cluster of low-energy tracks, so a "chill/focused/lofi" user profile gets well-differentiated, relevant top results.

---

## 6. Limitations and Bias

**Functional limitations:**
- Only 10 songs — real systems operate on millions of tracks.
- No learning: the model never updates based on what users actually liked or skipped.
- No diversity control: the top-5 results can all be nearly identical songs if the catalog clusters around one style.
- Binary acoustic flag is an oversimplification.

**Bias risks:**
- **Genre coverage bias**: Users who prefer jazz, hip-hop, classical, or any genre not in the catalog will never receive a genre-match bonus. Their recommendations are systematically weaker and less relevant than pop or lofi users.
- **Mood vocabulary mismatch**: If a user's actual mood does not map to one of the 9 moods in the catalog, they lose the mood bonus entirely.
- **Energy as a proxy for intensity**: High energy scores correlate with "intense" and "gym" vibes. Calm users who also want high-valence (cheerful) music may get pushed toward intense tracks instead of happy-but-mellow ones.
- **No representation of listening context**: The system treats a late-night wind-down session identically to a morning workout session.
- **If used at scale, feedback loops**: If VibeFinder were deployed and users only clicked on pop results (because pop dominates the catalog), a learning system trained on those clicks would double down on pop, further marginalizing other genres.

---

## 7. Evaluation

**User profiles tested:**

| Profile | Expected top result | Actual top result | Match? |
|---|---|---|---|
| genre=pop, mood=happy, energy=0.82 | Sunrise City | Sunrise City (7.5/7.5) | Yes |
| genre=lofi, mood=chill, energy=0.40 | Library Rain or Midnight Coding | Library Rain (6.93) | Yes |
| genre=pop, mood=intense, energy=0.93 | Gym Hero | Gym Hero (7.5/7.5) | Yes |
| genre=jazz, mood=relaxed, energy=0.37 | Coffee Shop Stories | Coffee Shop Stories (7.43) | Yes |
| genre=ambient, mood=chill, energy=0.28 | Spacewalk Thoughts | Spacewalk Thoughts (7.5/7.5) | Yes |

**What surprised me:** Even profiles for underrepresented genres (jazz, ambient) scored perfectly *within their genre*, because the catalog happened to include exactly one track matching each. The problem would become visible only when a user's genre is completely absent from the catalog.

**Tests:** The starter tests in `tests/test_recommender.py` verify that:
1. `recommend()` returns songs sorted so the best genre+mood match comes first.
2. `explain_recommendation()` returns a non-empty string for any song.

Both tests pass with the implemented scoring logic.

---

## 8. Future Work

- **Expand the catalog**: 10 songs is too small to surface meaningful diversity. Even 100 songs would reveal real ranking trade-offs.
- **Add valence and danceability to scoring**: These features are stored but unused. Valence (musical positivity) would help distinguish "intense but cheerful" from "intense and dark."
- **Continuous acoustic preference**: Replace the boolean `likes_acoustic` with a float `acoustic_preference` (0–1) and score it like energy.
- **Diversity injection**: After scoring, re-rank results to ensure no more than 2 songs share the same genre, preventing monotonous recommendation lists.
- **Collaborative filtering layer**: Track which songs users skip or replay and use that signal to adjust weights over time.
- **Context-awareness**: Allow users to specify a listening context (workout, study, sleep) and adjust feature weights accordingly.
- **Explainability dashboard**: Show the user a breakdown of each song's score so they can tune their own profile.

---

## 9. Personal Reflection

Building VibeFinder 1.0 made the abstraction of a recommender system concrete in a way that reading about it never quite did. The moment I had to pick a number — "is genre worth 3 points or 2 points?" — I realized that every recommender embeds a set of opinions about what matters most to listeners. Those opinions are not neutral: they reflect whoever designed the weights, and if the designer's taste does not match a user's, the system quietly fails that user without any error message.

The most thought-provoking realization was about the feedback loop problem. A real platform's model learns from engagement data, and engagement data is shaped by what the platform shows. If the catalog (or the initial weights) underserves jazz fans, they engage less, the model learns jazz is less popular, it shows jazz even less — and the gap widens. The bias does not need to be intentional to cause real harm; it just needs to be unexamined. That is the part I would want anyone using a real recommender system — as a user or a designer — to keep in mind.
