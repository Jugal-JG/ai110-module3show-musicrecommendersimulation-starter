# Reflection: Profile Comparisons and What They Revealed

This file documents observations from running VibeFinder 1.0 against four distinct user profiles, comparing pairs to understand what the scoring logic is actually measuring — and where it fails.

---

## Pair 1: High-Energy Pop vs Chill Lofi

**High-Energy Pop** (genre=pop, mood=happy, energy=0.90, likes_acoustic=False)  
**Chill Lofi** (genre=lofi, mood=chill, energy=0.38, likes_acoustic=True)

These two profiles produced completely different top-5 lists with no overlap — exactly what you'd hope for. The pop profile surfaced upbeat, danceable tracks while the lofi profile surfaced quiet, acoustic study music. The system clearly separated these two vibes.

**What changed between outputs and why it makes sense:**  
The pop profile's top songs all have energy above 0.75 and a pop or adjacent genre. The lofi profile's top songs are all below 0.45 energy and carry high acousticness. Because genre, mood, and energy all point in opposite directions for these two users, the scoring formula amplified the difference rather than blending it. This is the system working correctly.

**Interesting detail:** *Chill Lofi* at #4 surfaced *Spacewalk Thoughts* (ambient/chill), not a lofi song at all. This is because mood=chill matches and acousticness is 0.92 (acoustic bonus fires). A human would probably agree that ambient/chill and lofi/chill share a similar vibe, so this feels like an acceptable recommendation even across genre lines.

---

## Pair 2: Deep Intense Rock vs Adversarial (High Energy + Sad Mood)

**Deep Intense Rock** (genre=rock, mood=intense, energy=0.91, likes_acoustic=False)  
**Adversarial** (genre=metal, mood=sad, energy=0.95, likes_acoustic=False)

Both profiles want high-energy, aggressive music. But their outputs diverged significantly:

- Rock profile: top result scored 6.50/7.5, clear winner, clean separation between #1 and the rest
- Adversarial profile: top result scored only 4.47/7.5, and results 2–5 all scored between 1.35 and 1.48 — basically identical

**What changed and why:**  
The rock profile hit genre + mood + energy perfectly in *Storm Runner*, giving it a big score gap over the field. The adversarial profile got the genre match for *Iron Curtain* (metal) but the mood "sad" does not exist in the catalog, so the mood bonus never fired for any song. This cut the maximum achievable score from 7.5 to 5.5, and the remaining songs were separated only by tiny energy differences (~0.1 apart).

**Plain language explanation (why does "Gym Hero" keep appearing for people who just want intense music):**  
Imagine the system as a checklist: genre match? mood match? energy close enough? If your genre is rare in the catalog and your mood isn't recognized, the checklist only gets to "energy close enough." *Gym Hero* has energy 0.93, which is close to almost any high-energy target. So it keeps appearing because it wins the only contest still running. It is not that the system thinks *Gym Hero* is a great match — it is that every other tie-breaker has already been eliminated.

---

## Pair 3: High-Energy Pop — Original Weights vs Weight-Shift Experiment

**Original** (genre=3.0, mood=2.0, energy=1.5)  
**Shifted** (genre=1.5, mood=2.0, energy=3.0)

| Rank | Original | Shifted |
|---|---|---|
| #1 | Sunrise City (pop/happy) | Sunrise City (pop/happy) |
| #2 | Gym Hero (pop/intense) | Rooftop Lights (indie pop/happy) |
| #3 | Rooftop Lights (indie pop/happy) | Gym Hero (pop/intense) |

**What changed and why it makes sense:**  
*Gym Hero* and *Rooftop Lights* swapped positions. In the original, *Gym Hero* ranked higher because it is pop (genre match +3.0) even though mood=intense doesn't match. In the shifted version, genre is only worth 1.5 points, so *Rooftop Lights* (mood=happy match +2.0 + close energy +2.58 = 4.58) beats *Gym Hero* (genre match +1.5 + energy +2.91 = 4.41).

**What this teaches:** The genre weight is the single biggest lever in the system. A high genre weight makes the recommender "genre-loyal" — it will always prefer a same-genre song even if the mood is wrong. A lower genre weight makes it "vibe-driven" — mood and energy together can overcome a genre mismatch. Neither is universally better; it depends on what matters more to the listener.

---

## Overall Takeaway

Running these comparisons revealed that VibeFinder 1.0 behaves logically when profiles are well-matched to the catalog, but degrades silently when they are not. The system never raises an error, never warns the user, and never explains what it could not satisfy. In a real product, that silent degradation would be a serious design flaw — users would just see "bad recommendations" with no understanding of why. The most important improvement would not be better weights; it would be better feedback to the user about which preferences were and were not satisfied.
