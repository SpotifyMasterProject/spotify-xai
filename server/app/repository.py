from databases import Database
from databases.interfaces import Record
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import Column, Table, MetaData, Integer, String, ARRAY, Float, Date, insert, select, func
from typing import Optional

from models.session import Session
from models.user import User
from models.song import Song

metadata = MetaData()
songs = Table(
    "songs",
    metadata,
    Column("id", String, primary_key=True),
    Column("track_name", String),
    Column("album", String),
    Column("album_id", String),
    Column("artists", ARRAY(String)),
    Column("artist_ids", ARRAY(String)),
    Column("danceability", Float),
    Column("energy", Float),
    Column("speechiness", Float),
    Column("valence", Float),
    Column("tempo", Float),
    Column("duration_ms", Integer),
    Column("release_date", Date),
    Column("popularity", Float, nullable=True)
)


class Repository:
    def __init__(self, postgres: Database, redis: Redis):
        self.redis = redis
        self.postgres = postgres

    @staticmethod
    def get_user_key(user_id) -> str:
        return f'user:{user_id}'

    @staticmethod
    def get_session_key(session_id) -> str:
        return f'session:{session_id}'

    async def set_user(self, user: User) -> None:
        await self.redis.set(self.get_user_key(user.id), user.model_dump_json())

    async def get_user_by_id(self, user_id: str) -> Optional[bytes]:
        return await self.redis.get(self.get_user_key(user_id))

    async def verify_user_by_id(self, user_id: str) -> None:
        if await self.redis.exists(self.get_user_key(user_id)) == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized! Invalid user ID.")

    async def set_session(self, session: Session) -> None:
        await self.redis.set(self.get_session_key(session.id), session.model_dump_json())

    async def get_session_by_id(self, session_id: str) -> Optional[bytes]:
        return await self.redis.get(self.get_session_key(session_id))

    async def get_session_by_key(self, session_key: str) -> Optional[bytes]:
        return await self.redis.get(session_key)

    def get_all_sessions_by_pattern(self):
        return self.redis.scan_iter(match='session:*')

    async def verify_session_by_id(self, session_id: str) -> None:
        if await self.redis.exists(self.get_session_key(session_id)) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid session ID.")

    async def add_song_by_info(self, song_info: dict) -> None:
        query = insert(songs).values(song_info)
        await self.postgres.execute(query)

    async def get_song_by_id(self, song_id: str) -> Record:
        query = select(songs).where(songs.c.id == song_id)
        result = await self.postgres.fetch_one(query)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
        return result

    async def get_songs_by_pattern(self, pattern: str, limit: int) -> list[Record]:
        regex_pattern = f'\\m{pattern}'

        query = select(songs).where(
            songs.c.track_name.op('~*')(regex_pattern) |
            func.array_to_string(songs.c.artists, ' ').op('~*')(regex_pattern)
        ).limit(limit)
        result = await self.postgres.fetch_all(query, {'pattern': f'%{pattern}%'})
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching songs found")
        return result

    # async def delete_song_by_id(self, song_id: str) -> None:
    #     query = delete(songs).where(songs.c.id == song_id)
    #     await self.postgres.execute(query)

    async def get_recommendations_by_song_id(self, playlist: list[Song], limit: int = 3) -> list[Record]:
        if not playlist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Playlist is empty")

        create_extension_query = "CREATE EXTENSION IF NOT EXISTS cube;"
        await self.postgres.execute(create_extension_query)

        song_ids = [song.id for song in playlist]

        query = """
            WITH tempo_stats AS (
                SELECT 
                    MIN(tempo) AS min_tempo,
                    MAX(tempo) AS max_tempo
                FROM songs
            ),
            target_songs AS (
                SELECT 
                    AVG(s.danceability) AS avg_danceability, 
                    AVG(s.energy) AS avg_energy,
                    AVG(s.speechiness) AS avg_speechiness,
                    AVG(s.valence) AS avg_valence,
                    AVG((s.tempo - ts.min_tempo) / (ts.max_tempo - ts.min_tempo)) AS avg_tempo  -- Normalize tempo
                FROM songs s, tempo_stats ts
                WHERE id = ANY(:song_ids)  -- match multiple song IDs
            ),
            song_distances AS (
                -- calculate cosine distance between the averaged vector and each song
                SELECT 
                    s.id,
                    cube_distance(
                        cube(array[s.danceability, s.energy, s.speechiness, s.valence, (s.tempo - ts.min_tempo) / (ts.max_tempo - ts.min_tempo)]),
                        cube(array[t.avg_danceability, t.avg_energy, t.avg_speechiness, t.avg_valence, t.avg_tempo])
                    ) AS cosine_distance
                FROM songs s, target_songs t, tempo_stats ts
                WHERE s.id != ALL(:song_ids)  -- exclude the target songs
            )
            -- return the 3 closest songs
            SELECT * FROM song_distances
            ORDER BY cosine_distance
            LIMIT :limit;
        """

        result = await self.postgres.fetch_all(query, {"song_ids": song_ids, "limit": limit})
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recommendations found")
        return result

    async def delete_session_by_id(self, session_id: str) -> None:
        await self.redis.delete(self.get_session_key(session_id))
