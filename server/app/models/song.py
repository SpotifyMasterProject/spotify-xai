from pydantic import model_validator
from datetime import datetime
from typing import Optional
from .camel_model import CamelModel

# Approximate values for maximum and minimum values of tempo.
MAX_TEMPO = 200
MIN_TEMPO = 60


class Song(CamelModel):
    id: Optional[str] = None
    track_name: Optional[str] = None
    album: Optional[str] = None
    album_id: Optional[str] = None
    artists: list[str] = []
    artist_ids: list[str] = []
    danceability: Optional[float] = None
    energy: Optional[float] = None
    speechiness: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    # Scaled tempo between [0, 1].
    scaled_tempo: Optional[float] = None
    duration_ms: Optional[int] = None
    release_date: Optional[datetime] = None
    popularity: Optional[float] = None
    most_significant_feature: Optional[str] = None

    @model_validator(mode='after')
    def set_scaled_tempo(self) -> 'Song':
        scaled_tempo = (self.tempo - MIN_TEMPO) / (MAX_TEMPO - MIN_TEMPO)
        # Clamp between 0 and 1
        self.scaled_tempo = max(0, min(scaled_tempo, 1))

        return self


class SongList(CamelModel):
    songs: list[Song] = []


class Playlist(CamelModel):
    played_songs: list[Song] = []
    current_song: Optional[Song] = None
    queued_songs: list[Song] = []

    def get_all_songs(self) -> list[Song]:
        songs = self.played_songs.copy()
        if self.current_song:
            songs.append(self.current_song)
        songs.extend(self.queued_songs)
        return songs
