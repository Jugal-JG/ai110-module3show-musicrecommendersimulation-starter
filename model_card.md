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

The catalog is stored in `data/songs.csv` and contains **18 songs** (10 starter + 8 added to cover missing genres).

| Attribute | Values present |
|---|---|
| Genres | pop (2), lofi (3), rock (1), ambient (1), jazz (1), synthwave (1), indie pop (1), r&b (1), hip-hop (1), country (1), blues (1), classical (1), edm (1), folk (1), metal (1) |
| Moods | happy (2), chill (2), intense (3), relaxed (1), moody (1), focused (1), romantic (1), nostalgic (2), melancholic (1), peaceful (1), euphoric (1) |
| Energy range | 0.22 (Velvet Morning) – 0.97 (Iron Curtain) |

8 songs were added to broaden genre and mood coverage. Despite this, the catalog still skews toward Western pop-adjacent styles.

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
- Only 18 songs — real systems operate on millions of tracks.
- No learning: the model never updates based on what users actually liked or skipped.
- No diversity control: the top-5 results can all be nearly identical songs if the catalog clusters around one style.
- Binary acoustic flag is an oversimplification.

**Bias risks discovered during experiments:**

- **Genre string-match blindness**: The system treats "rock" and "metal" as completely unrelated because they are different strings. In the Deep Intense Rock stress test, *Iron Curtain* (metal, clearly rock-adjacent) ranked 4th tied with *Crowd Surfer* (hip-hop), despite metal being far closer to rock culturally and sonically. A real system would use genre embeddings or a genre hierarchy to handle this.

- **Silent mood vocabulary failure**: When a user sets `mood="sad"` — a mood that does not exist in the catalog — the system never fires the mood bonus and gives no warning. The adversarial profile test exposed this completely: results 2–5 all scored ~1.4/7.5, separated only by tiny energy differences, because the system silently fell back to energy-only scoring. Users have no way to know their preference was ignored.

- **Genre weight dominance creates a filter bubble**: With genre weighted at 3.0 out of a max 7.5, a song that merely matches genre but has the wrong mood and wrong energy still scores 3.0 — higher than any mood+energy combination without a genre match (max 3.5 but rare). This means non-pop users always get one pop song in their top 5 just because energy happens to be close. The weight-shift experiment confirmed this: halving the genre weight immediately reshuffled results toward mood-aligned songs.

- **Mood vocabulary mismatch**: If a user's actual mood does not map to one of the catalog moods, they lose the mood bonus entirely with no fallback.

- **No representation of listening context**: The system treats a late-night wind-down session identically to a morning workout session.

- **If used at scale, feedback loops**: If VibeFinder were deployed and users only clicked on pop results (because pop dominates the catalog), a learning system trained on those clicks would double down on pop, further marginalizing other genres.

---

## 7. Evaluation

**User profiles tested (stress test with diverse profiles):**

| Profile | Top result | Score | Intuition match? | Surprise |
|---|---|---|---|---|
| High-Energy Pop (pop/happy/0.90) | Sunrise City | 6.38/7.5 | Yes | *Rooftop Lights* (indie pop) ranks #3 via mood+energy despite no genre match |
| Chill Lofi (lofi/chill/0.38/acoustic) | Library Rain | 7.46/7.5 | Yes | *Rainy Blues* (blues) sneaks into #5 via acoustic bonus alone |
| Deep Intense Rock (rock/intense/0.91) | Storm Runner | 6.50/7.5 | Yes | *Iron Curtain* (metal) ranks #4 tied with *Crowd Surfer* (hip-hop) — metal/rock adjacency invisible to string matching |
| Adversarial (metal/sad/0.95) | Iron Curtain | 4.47/7.5 | Partial | Mood bonus never fires — "sad" not in catalog — system silently degrades to energy-only scoring |

**Weight-shift experiment (genre=1.5, energy=3.0):**

| Profile | Original #2 | Shifted #2 | Change |
|---|---|---|---|
| High-Energy Pop | Gym Hero (pop, wrong mood) | Rooftop Lights (indie pop, right mood) | Mood now wins over same-genre wrong-mood |
| Deep Intense Rock | Gym Hero | Gym Hero (unchanged #2) | Top 3–4 reshuffled by tiny energy margins |

**What surprised me:** The adversarial profile was the most revealing test. Setting `mood="sad"` exposed that the system has no fallback behavior when a preference is unsatisfiable — it just silently scores lower across the board. A user would have no idea their mood was ignored. This is a silent failure mode that would be unacceptable in a production system.

**Tests:** The starter tests in `tests/test_recommender.py` verify that:
1. `recommend()` returns songs sorted so the best genre+mood match comes first.
2. `explain_recommendation()` returns a non-empty string for any song.

Both tests pass.

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
