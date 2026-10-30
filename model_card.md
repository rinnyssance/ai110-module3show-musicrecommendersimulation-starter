# Model Card: Vibe Compass 1.0

## 1. Model Name

Vibe Compass 1.0: a transparent, rule-based music recommender.

## 2. Intended Use

A classroom simulation that suggests five songs for an explicitly supplied genre, mood, and energy target. It assumes a profile describes one listening context. It is intended for exploring features, weights, rankings, and bias. It is not intended for production personalization, psychological inference, judging artists, or claiming to know a person's actual taste.

## 3. How the Model Works

Each song earns two points for matching the preferred genre and one for matching the mood. It earns up to one more point for being close to the target energy. An optional acoustic preference adds up to half a point. The recommender sorts the totals and explains every contribution, including mismatches. Both the object and dictionary interfaces use the same scoring function. The starter returned the first songs without scoring; this version actually ranks them and loads validated numeric CSV data.

## 4. Data

The catalog has 18 songs: the 10 starter rows plus 8 AI-generated fictional tracks. The additions cover folk, EDM, R&B, reggae, classical, hip hop, country, and metal, with reflective, euphoric, sad, hopeful, serene, confident, nostalgic, and angry moods. Original genres include pop, lofi, rock, ambient, jazz, synthwave, and indie pop. Original moods include happy, chill, intense, relaxed, moody, and focused.

The fields are ID, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. Values are teaching examples, not measured audio features. No starter tracks were removed. No real listening histories or personal data were added. The dataset is small and not representative of global music or any listener population.

## 5. Strengths

The rules are reproducible and easy to inspect. The pop, lofi, and rock profiles each produce a different first result that matches both requested genre and mood. Energy closeness distinguishes tracks without assuming high energy is always preferable. Explanations show why weaker matches still enter the top five.

## 6. Limitations and Bias

The conflicting sad/high-energy pop profile puts Gym Hero first even though its mood is intense, because the two-point genre reward dominates the sad-mood reward. The lofi profile has three matching-genre songs available, while the rock profile has only one, so catalog coverage affects how well preferences can be satisfied. Exact genre labels separate pop from indie pop and can hide related music. The unseen opera/triumphant profile receives songs based only on energy, with no warning threshold or guarantee of relevance. Repeated artists, fixed weights, and no exploration mechanism can reduce diversity and reinforce filter bubbles.

## 7. Evaluation

Actual terminal outputs for all five profiles and the weight experiment are in the README. Automated tests cover numeric CSV parsing, invalid CSV data, score arithmetic, explanations, energy symmetry, acoustic preferences, ranking, object/function agreement, stable ties, k boundaries, invalid energies, expected leading tracks, and the experiment's ranking change. These are behavioral checks, not a measured listener-satisfaction score; no ground-truth preference labels were collected.

### Main profiles and all pairwise comparisons

- Pop vs lofi: Sunrise City leads pop (3.98); Library Rain leads lofi (4.43). Pop rewards happy, energetic music; lofi rewards chill, quiet, acoustic music. Their top-five lists do not overlap.
- Pop vs rock: Storm Runner leads rock (4.44), while Sunrise City leads pop. Gym Hero appears second for both, earning genre credit for pop and mood credit for rock. City Resolve is also shared because its high energy fits both contexts.
- Lofi vs rock: Library Rain and Storm Runner reflect opposite energy and acoustic preferences. Their top-five lists do not overlap, supporting the intended distinction between quiet study music and intense music.

### Adversarial profiles

The conflicting profile requests pop, sad, and energy 0.95. Gym Hero wins at 2.98, while the only sad track, Blue Window, is third at 1.53. This exposes genre dominance rather than an error in the arithmetic. The unseen profile asks for opera and triumphant, neither present in the catalog; Blue Window wins at 0.98 only because its energy is close to 0.5. A first-place result is not necessarily a good match.

For completeness, comparisons involving the edge profiles: conflicting shares Sunrise City and Gym Hero with pop but reverses their order; compared with lofi, it has no top-five overlap because its energy target is much higher; compared with rock, it shares Gym Hero, Neon Footwork, and Midnight Sparks because all favor high energy. Unseen shares no top-five tracks with pop or rock, but shares Midnight Coding and Focus Flow with lofi because of moderate energy. Unseen and conflicting both include Blue Window, but rank it first and third respectively because one ignores unavailable labels while the other prioritizes pop.

### Weight-shift experiment

Halving genre and doubling energy moves Rooftop Lights above Gym Hero for pop. Sunrise City remains first because it satisfies both labels and is close to the energy target. The change better reflects the stated happy mood in second place, but no accuracy improvement can be established without user feedback. It illustrates how the same data supports different predictions under different objectives.

### Intuition check

As a feature-based sanity check, Library Rain looks appropriate for quiet study: it exactly matches lofi, chill, and energy 0.35, with high acousticness. This is a comparison against the metadata, not a claim that the author listened to fictional songs or personally enjoyed them.

## 8. Future Work

1. Collect consented listener feedback and evaluate held-out likes instead of relying only on hand-designed examples.
2. Expand and audit genre/language coverage; support several preferences and related genre labels.
3. Add a diversity reranker and a low-match notice, then compare relevance and variety before adopting them.

## 9. Personal Reflection

*AI-assisted draft for the author to review and personalize; no human listening or manual verification is claimed.*

The clearest lesson from this project is that ranking choices encode priorities. Gym Hero can be a reasonable suggestion for an intense profile and a weaker mood match for happy pop, yet still rank second in both. Changing the weights made that tradeoff visible. A small formula can feel personalized because it reacts to a profile, even though it has not learned anything about a real listener.

AI assistance handled the implementation, catalog expansion, documentation, and automated verification. The parts that deserve close review are the score arithmetic, whether explanations match the formula, and whether a changed ranking really implies improved recommendations. The next experiment I would consider is collecting ratings and adding a diversity rule, so improvements can be evaluated against something beyond the scoring rule itself.
