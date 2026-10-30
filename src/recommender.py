"""Transparent, weighted content-based music recommendations."""
import csv
import math
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple


@dataclass
class Song:
    """A catalog track and its descriptive features."""
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
    """A single listening context, rather than a complete musical identity."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


@dataclass(frozen=True)
class ScoreWeights:
    """Configurable feature weights for reproducible comparisons."""
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 1.0
    acoustic: float = 0.5

    def __post_init__(self):
        if any(not math.isfinite(v) or v < 0 for v in asdict(self).values()):
            raise ValueError("Weights must be finite and nonnegative")


DEFAULT_WEIGHTS = ScoreWeights()
ENERGY_WEIGHTS = ScoreWeights(genre=1.0, energy=2.0)


def unit_value(value, name):
    """Convert and validate a feature on the inclusive zero-to-one scale."""
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return number


def load_songs(csv_path: str) -> List[Dict]:
    """Load CSV rows, converting and validating numeric song features."""
    songs = []
    seen = set()
    with open(csv_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not set(Song.__dataclass_fields__).issubset(reader.fieldnames or []):
            raise ValueError("Song CSV is missing required columns")
        for line, row in enumerate(reader, start=2):
            try:
                song = {field: row[field] for field in Song.__dataclass_fields__}
                song["id"] = int(song["id"])
                if song["id"] in seen:
                    raise ValueError("Duplicate song ID")
                for field in ("title", "artist", "genre", "mood"):
                    song[field] = song[field].strip()
                    if not song[field]:
                        raise ValueError(f"Empty {field}")
                for field in ("energy", "valence", "danceability", "acousticness"):
                    song[field] = unit_value(song[field], field)
                song["tempo_bpm"] = float(song["tempo_bpm"])
                if not math.isfinite(song["tempo_bpm"]) or song["tempo_bpm"] <= 0:
                    raise ValueError("Tempo must be positive and finite")
            except (ValueError, TypeError, AttributeError) as exc:
                raise ValueError(f"Invalid song on CSV line {line}: {exc}") from exc
            seen.add(song["id"])
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict,
               weights: ScoreWeights = DEFAULT_WEIGHTS) -> Tuple[float, List[str]]:
    """Return a weighted similarity score and its feature contributions."""
    genre = user_prefs.get("genre", user_prefs.get("favorite_genre"))
    mood = user_prefs.get("mood", user_prefs.get("favorite_mood"))
    energy = user_prefs.get("energy", user_prefs.get("target_energy"))
    if not isinstance(genre, str) or not genre.strip() or not isinstance(mood, str) or not mood.strip():
        raise ValueError("A nonempty genre and mood are required")
    target = unit_value(energy, "target energy")
    actual = unit_value(song["energy"], "song energy")
    score = 0.0
    reasons = []
    for label, desired, weight in (("genre", genre, weights.genre), ("mood", mood, weights.mood)):
        match = song[label].strip().casefold() == desired.strip().casefold()
        points = weight if match else 0.0
        score += points
        reasons.append(f"{label} {'match' if match else 'mismatch'} (+{points:.2f})")
    points = weights.energy * (1 - abs(actual - target))
    score += points
    reasons.append(f"energy {actual:.2f} vs target {target:.2f} (+{points:.2f})")
    acoustic = user_prefs.get("likes_acoustic")
    if acoustic is not None:
        if not isinstance(acoustic, bool):
            raise ValueError("likes_acoustic must be a boolean")
        value = unit_value(song["acousticness"], "acousticness")
        points = weights.acoustic * (value if acoustic else 1 - value)
        score += points
        reasons.append(f"{'acoustic' if acoustic else 'non-acoustic'} preference (+{points:.2f})")
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    weights: ScoreWeights = DEFAULT_WEIGHTS) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k, preserving input order on ties."""
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("k must be a nonnegative integer")
    ranked = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        ranked.append((song, score, "; ".join(reasons)))
    return sorted(ranked, key=lambda item: item[1], reverse=True)[:k]


class Recommender:
    """Object interface sharing the functional scoring and ranking rules."""
    def __init__(self, songs: List[Song], weights: ScoreWeights = DEFAULT_WEIGHTS):
        self.songs = list(songs)
        self.weights = weights

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return typed songs in descending preference score."""
        rows = recommend_songs(asdict(user), [asdict(s) for s in self.songs], k, self.weights)
        return [Song(**row) for row, _, _ in rows]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain the same contributions used for ranking."""
        score, reasons = score_song(asdict(user), asdict(song), self.weights)
        return f"Score {score:.2f}: " + "; ".join(reasons)
