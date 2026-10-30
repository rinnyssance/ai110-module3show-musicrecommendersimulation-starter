from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""

import csv
from dataclasses import asdict
from pathlib import Path

import pytest
from src.recommender import load_songs, score_song, recommend_songs, ENERGY_WEIGHTS
from src.main import PROFILES, CATALOG


def test_csv_has_expanded_diverse_numeric_catalog():
    songs = load_songs(CATALOG)
    assert len(songs) == 18
    assert len({s['genre'] for s in songs}) >= 10
    assert all(isinstance(s['id'], int) for s in songs)
    assert all(isinstance(s['energy'], float) for s in songs)


def test_score_math_and_explanations():
    song = asdict(make_small_recommender().songs[0])
    score, reasons = score_song({'genre': ' POP ', 'mood': 'Happy', 'energy': 0.8}, song)
    assert score == pytest.approx(4)
    assert 'genre match (+2.00)' in reasons
    assert 'mood match (+1.00)' in reasons
    assert len(reasons) == 3


def test_energy_rewards_closeness_not_loudness():
    song = asdict(make_small_recommender().songs[0])
    prefs = {'genre': 'pop', 'mood': 'happy', 'energy': 0.5}
    near = score_song(prefs, dict(song, energy=0.5))[0]
    low = score_song(prefs, dict(song, energy=0.25))[0]
    high = score_song(prefs, dict(song, energy=0.75))[0]
    assert near > low
    assert low == high


def test_acoustic_preference_changes_score():
    song = asdict(make_small_recommender().songs[1])
    prefs = dict(PROFILES['lofi'])
    acoustic = score_song(prefs, song)[0]
    prefs['likes_acoustic'] = False
    assert acoustic > score_song(prefs, song)[0]


def test_ranking_and_object_interface_agree_without_mutation():
    rec = make_small_recommender()
    user = UserProfile('lofi', 'chill', 0.4, True)
    rows = [asdict(s) for s in rec.songs]
    result = recommend_songs(asdict(user), rows, 9)
    assert [r[0]['id'] for r in result] == [s.id for s in rec.recommend(user, 9)]
    assert result[0][0]['genre'] == 'lofi'
    assert rows[0]['genre'] == 'pop'
    assert result[0][1] > result[1][1]


def test_ties_preserve_catalog_order():
    song = asdict(make_small_recommender().songs[0])
    songs = [dict(song, id=2), dict(song, id=1)]
    assert [r[0]['id'] for r in recommend_songs(PROFILES['pop'], songs)] == [2, 1]


def test_empty_and_zero_results():
    assert recommend_songs(PROFILES['pop'], []) == []
    assert recommend_songs(PROFILES['pop'], load_songs(CATALOG), 0) == []


@pytest.mark.parametrize('k', [-1, 1.5, True])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        recommend_songs(PROFILES['pop'], [], k)


@pytest.mark.parametrize('energy', [-0.1, 1.1, float('nan'), float('inf')])
def test_invalid_energy(energy):
    with pytest.raises(ValueError):
        score_song(dict(PROFILES['pop'], energy=energy), asdict(make_small_recommender().songs[0]))


def test_bad_csv_reports_line(tmp_path):
    path = tmp_path / 'bad.csv'
    path.write_text(CATALOG.read_text().replace('0.82', 'invalid', 1))
    with pytest.raises(ValueError, match='line 2'):
        load_songs(path)


def test_missing_columns_rejected(tmp_path):
    path = tmp_path / 'bad.csv'
    path.write_text('id,title\n1,Example\n')
    with pytest.raises(ValueError, match='columns'):
        load_songs(path)


def test_profiles_and_weight_experiment():
    songs = load_songs(CATALOG)
    expected = {'pop': 'Sunrise City', 'lofi': 'Library Rain', 'rock': 'Storm Runner',
                'conflicting': 'Gym Hero', 'unseen': 'Blue Window'}
    for name, title in expected.items():
        ranked = recommend_songs(PROFILES[name], songs)
        assert len(ranked) == 5
        assert ranked[0][0]['title'] == title
    baseline = recommend_songs(PROFILES['pop'], songs)
    shifted = recommend_songs(PROFILES['pop'], songs, weights=ENERGY_WEIGHTS)
    assert baseline[1][0]['title'] == 'Gym Hero'
    assert shifted[1][0]['title'] == 'Rooftop Lights'
