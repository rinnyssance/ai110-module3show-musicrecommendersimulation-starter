"""Run example profiles and a reproducible weight-shift experiment."""
import argparse
from pathlib import Path
from .recommender import DEFAULT_WEIGHTS, ENERGY_WEIGHTS, load_songs, recommend_songs

CATALOG = Path(__file__).resolve().parents[1] / "data" / "songs.csv"
PROFILES = {
    "pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    "conflicting": {"genre": "pop", "mood": "sad", "energy": 0.95},
    "unseen": {"genre": "opera", "mood": "triumphant", "energy": 0.5},
}


def main():
    """Print top-five recommendations with their exact scoring reasons."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=[*PROFILES, "all"], default="pop")
    parser.add_argument("--experiment", action="store_true", help="Halve genre and double energy weights")
    args = parser.parse_args()
    songs = load_songs(CATALOG)
    print(f"Loaded songs: {len(songs)}")
    weights = ENERGY_WEIGHTS if args.experiment else DEFAULT_WEIGHTS
    print(f"Weights: genre={weights.genre}, mood={weights.mood}, energy={weights.energy}, acoustic={weights.acoustic}")
    names = PROFILES if args.profile == "all" else [args.profile]
    for name in names:
        profile = PROFILES[name]
        print(f"\nProfile: {name} {profile}\nTop recommendations:")
        for rank, (song, score, explanation) in enumerate(recommend_songs(profile, songs, weights=weights), 1):
            print(f"{rank}. {song['title']} - {song['artist']} | Score: {score:.2f}")
            print(f"   Because: {explanation}")


if __name__ == "__main__":
    main()
