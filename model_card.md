# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender simulation. The name reflects its goal: find songs that match the "vibe" a user is looking for right now.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *given what a user tells us about their taste, which songs from the catalog are the best match?*

It does this by taking a user's stated preferences — favorite genre, favorite mood, target energy level, and whether they like acoustic music — and suggesting the 5 songs that best fit that description. It is not trying to predict what users will click on or learn from their history. It simply finds the closest match to what they explicitly said they want.

---

## 3. Data Used

The catalog lives in `data/songs.csv` and contains **18 songs**.

Each song has 10 attributes: `id`, `title`, `artist`, `genre`, `mood`, `energy` (0–1), `tempo_bpm`, `valence`, `danceability`, and `acousticness` (0–1).

Only 4 of these are used in scoring: `genre`, `mood`, `energy`, and `acousticness`. The rest are stored but unused.

**Genre coverage:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, hip-hop, country, blues, classical, edm, folk, metal (15 genres across 18 songs — most appear only once).

**Mood coverage:** happy, chill, intense, relaxed, moody, focused, romantic, nostalgic, melancholic, peaceful, euphoric (11 distinct moods).

**Limits:**
- 18 songs is tiny. Real systems use millions of tracks.
- All songs are Western, English-language music. No non-Western styles.
- Most genres appear only once, so a genre match is an all-or-nothing gamble.
- The mood list was hand-picked — many real moods (anxious, nostalgic, heartbroken) are missing.

---

## 4. Algorithm Summary

VibeFinder scores every song against the user's profile using four rules, then returns the top 5 by score.

Think of it like a checklist with points:

1. **Genre match** → +3 points. The biggest reward. If the song's genre matches what the user said they like, they get 3 points.
2. **Mood match** → +2 points. If the song's mood matches, add 2 points.
3. **Energy closeness** → up to +1.5 points. Energy is a number from 0 (very calm) to 1 (very intense). The closer the song's energy is to what the user wants, the more points. A perfect match gives 1.5; a completely opposite energy gives 0.
4. **Acoustic bonus** → +1 point. Only applies if the user said they like acoustic music AND the song is heavily acoustic. Otherwise ignored.

The maximum possible score is **7.5**. Songs are sorted from highest to lowest and the top 5 are shown.

---

## 5. Observed Behavior / Biases

Three patterns stood out clearly from running experiments:

**Genre string-matching is blind to musical similarity.** The system treats "rock" and "metal" as totally unrelated because they are different words. When a rock fan was tested, *Iron Curtain* (metal — clearly rock-adjacent) ranked the same as *Crowd Surfer* (hip-hop), even though metal is much closer to rock in reality. The system has no concept of genre families.

**Mood silently fails when the word is missing.** In an adversarial test, the profile was set to `mood="sad"` — a mood not in the catalog. The system gave no warning. It just never awarded the mood bonus to any song, and the top results were basically random energy matches scoring around 1.4/7.5. A real user would just see bad recommendations with no explanation.

**Genre weight dominance creates a filter bubble.** Genre is worth 3 points out of 7.5 — 40% of the max score. A song that matches genre but has the completely wrong mood and wrong energy still scores 3.0, which beats most songs that match mood+energy but not genre. This means users always get genre-matched songs even when better "vibe" options exist. When the genre weight was halved in an experiment, the results immediately felt more musically appropriate for some profiles.

---

## 6. Evaluation Process

The system was tested in three ways:

**Diverse profile stress test.** Four profiles were run: High-Energy Pop, Chill Lofi, Deep Intense Rock, and an adversarial profile (metal/sad/0.95 energy). For each, the top 5 results were checked against musical intuition. Three of four profiles produced results that "felt right." The adversarial profile exposed the silent mood failure bug.

**Weight-shift experiment.** The genre weight was halved (3.0 → 1.5) and the energy weight was doubled (1.5 → 3.0). For the pop profile, *Rooftop Lights* (indie pop, happy mood) jumped from #3 to #2, swapping with *Gym Hero* (pop, wrong mood). This confirmed that genre weight is the single biggest lever in the system.

**Automated tests.** Two pytest tests check that `recommend()` returns songs sorted correctly by score, and that `explain_recommendation()` always returns a non-empty string. Both pass.

**Comparison to real apps.** Spotify would likely surface *Rooftop Lights* higher for a pop/happy user than this system does, because Spotify uses collaborative signals (other happy-pop listeners also liked it). VibeFinder misses this because it is purely content-based with no user behavior data.

---

## 7. Intended Use and Non-Intended Use

**Designed for:**
- Classroom learning — to make the math behind recommender systems visible and understandable.
- Experimentation — changing weights, adding features, or swapping profiles to see what happens.
- Demonstrating concepts like content-based filtering, scoring rules, and ranking.

**Not designed for:**
- Real users making real music decisions. The catalog is too small and the scoring is too simple.
- Personalization over time. The system has no memory — every run starts fresh.
- Any production or commercial use.
- Users who expect it to "learn" their taste — it only reads what they explicitly provide.

---

## 8. Ideas for Improvement

**Make genre matching smarter.** Instead of exact string matching, use a genre similarity map so "metal" and "rock" are recognized as related. This would fix the biggest single bias found during testing.

**Add a fallback warning when preferences are unsatisfiable.** If a user's mood or genre does not exist in the catalog, tell them instead of silently degrading. Something like: "Note: no songs in the catalog match mood='sad'. Showing best energy matches instead."

**Add valence to the scoring formula.** Valence measures musical positivity (0 = dark/sad, 1 = cheerful). It is already in the CSV but unused. Adding it would let the system separate "intense but euphoric" (EDM) from "intense and dark" (metal), which energy alone cannot do.

---

## 9. Personal Reflection

**Biggest learning moment:** The adversarial profile test. I set `mood="sad"` expecting the system to struggle — but I didn't expect it to fail completely silently. No error, no warning, no explanation. The results just looked wrong. That moment taught me that a system can be logically correct and still mislead users, because the failure is invisible. Transparency is not just about showing why a song was recommended — it is also about showing when a preference could not be satisfied.

**How AI tools helped and when I needed to double-check:** AI helped generate the initial scoring structure and suggested using `sorted()` over `.sort()` with a clear explanation of why. I verified both by running the actual output and checking that the catalog was not being mutated between profile runs. The weight-shift experiment was AI-assisted in setup but I had to manually interpret whether the results were "better" or just "different" — that judgment cannot be automated.

**What surprised me about simple algorithms:** A four-rule formula with hand-picked weights can produce results that genuinely feel like recommendations. When *Library Rain* and *Midnight Coding* surfaced back-to-back for the lofi/chill profile, it felt almost uncanny — like the system "understood" something. It did not. It just did math. The surprise was how easily a human brain pattern-matches that math into meaning.

**What I would try next:** I would add a diversity constraint — after scoring, ensure the top 5 includes no more than 2 songs from the same genre. The current system can return 3 lofi tracks in a row for a lofi user, which is technically correct but not a great listening experience. Real recommenders balance relevance with variety, and that tension is one of the most interesting unsolved problems in the field.
