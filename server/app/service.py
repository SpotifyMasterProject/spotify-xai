import jwt
import os
import asyncio
import uuid
import math
import requests

from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from typing import Annotated
from models.user import User, SpotifyUser
from models.token import Token, SpotifyToken
from models.session import SessionCore, Session
from models.song import Song, SongList, Playlist
from models.recommendation import Recommendation, RecommendationList
from repository import Repository
from ws.websocket_manager import WebsocketManager

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
LOCAL_IP_ADDRESS = os.getenv("LOCAL_IP_ADDRESS")
DISCOGS_API_URL = os.getenv("DISCOGS_API_URL")
DISCOGS_API_TOKEN = os.getenv("DISCOGS_API_TOKEN")


class Service:
    def __init__(self, repository: Repository, websocket_manager: WebsocketManager):
        self.repo = repository
        self.manager = websocket_manager
        self.spotify_oauth = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="user-library-read"  # scope defines functionalities
        )
        self.spotify_api_client = Spotify(auth_manager=self.spotify_oauth)
        self.session_lock = asyncio.Lock()

    def with_session_lock(func):
        async def wrapper(self, *args):
            async with self.session_lock:
                return await func(self, *args)
        return wrapper

    def get_spotify_token(self, host: SpotifyUser) -> SpotifyToken:
        try:
            spotify_token_info = self.spotify_oauth.get_access_token(host.auth_code, check_cache=False)
            return SpotifyToken(**spotify_token_info)
        except SpotifyOauthError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code")

    @staticmethod
    def get_display_name(token: SpotifyToken) -> str:
        try:
            spotify_host_client = Spotify(auth=token.access_token)
            user_info = spotify_host_client.current_user()
            return user_info['display_name']
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request unsuccessful: {repr(e)}")

    async def create_user(self, user: User) -> User:
        user.id = str(uuid.uuid4())
        await self.repo.set_user(user)
        return user

    @staticmethod
    def generate_token(user: User, spotify_token: SpotifyToken = None) -> Token:
        to_encode = {"sub": user.id, "username": user.username}
        if spotify_token:  # additionally encode the spotify token for hosts
            to_encode["spotify_token"] = spotify_token.model_dump()
        access_token_expires = timedelta(minutes=JWT_EXPIRES_MINUTES)
        expire = datetime.now(timezone.utc) + (access_token_expires or timedelta(minutes=30))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return Token(access_token=encoded_jwt, token_type="bearer")

    @staticmethod
    def verify_token(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))]) -> str:
        auth_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized!")
        try:
            payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise auth_exception
        except InvalidTokenError:
            raise auth_exception
        # TODO: Consider also returing the spotify token.
        return user_id

    async def verify_user(self, user_id: str) -> None:
        await self.repo.verify_user_by_id(user_id)

    async def verify_session(self, session_id: str) -> None:
        await self.repo.verify_session_by_id(session_id)

    async def verify_instances(self, user_ids: str | list[str] = "", session_id: str = ""):
        if isinstance(user_ids, str) and user_ids:
            await self.verify_user(user_ids)
        elif isinstance(user_ids, list):
            for user_id in user_ids:
                await self.verify_user(user_id)
        if session_id:
            await self.verify_session(session_id)

    async def get_user(self, user_id: str) -> User:
        result = await self.repo.get_user_by_id(user_id)
        return User.model_validate_json(result)

    async def create_session(self, host_id: str, session: Session) -> Session:
        host = await self.get_user(host_id)
        session.id = str(uuid.uuid4())
        session.host_id = str(host.id)
        session.host_name = host.username
        session.creation_date = datetime.now()
        # TODO: adjust URL
        session.invite_link = f'http://{LOCAL_IP_ADDRESS}:8080/{session.id}/join'
        # session.playlist = Playlist()
        await self.repo.set_session(session)
        return session

    async def get_session(self, session_id: str) -> Session:
        result = await self.repo.get_session_by_id(session_id)
        return Session.model_validate_json(result)

    @staticmethod
    def verify_host_of_session(host_id: str, session: Session) -> None:
        if session.host_id != host_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not host of session.")

    async def end_session(self, host_id: str, session_id: str):
        session = await self.get_session(session_id)
        self.verify_host_of_session(host_id, session)
        await self.repo.delete_session_by_id(session_id)
        # TODO: create and return session artifact
        return

    @with_session_lock
    async def add_guest_to_session(self, guest_id: str, session_id: str) -> Session:
        guest = await self.get_user(guest_id)
        session = await self.get_session(session_id)

        if guest_id not in session.guests:
            session.guests[guest_id] = guest
            await self.repo.set_session(session)
            await self.manager.publish(channel=f"session:{session_id}", message=SessionCore(**session.model_dump()))
        return session

    @staticmethod
    def verify_guest_of_session(guest_id: str, session: Session) -> None:
        if guest_id not in session.guests:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guest not part of session.")

    async def remove_guest_from_session(self, host_id: str, guest_id: str, session_id: str) -> None:
        session = await self.get_session(session_id)

        if host_id:
            self.verify_host_of_session(host_id, session)

        self.verify_guest_of_session(guest_id, session)
        del session.guests[guest_id]
        await self.repo.set_session(session)
        await self.manager.publish(channel=f"session:{session_id}", message=SessionCore(**session.model_dump()))

    async def get_song_from_database(self, song_id: str) -> Song:
        result = await self.repo.get_song_by_id(song_id)
        song = Song.model_validate(dict(result))
        if not song.preview_url:
            try:
                song_info = self.spotify_api_client.track(song.id)
                song.preview_url = song_info.get('preview_url')
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request unsuccessful: {repr(e)}")
        return song

    async def add_song_to_database(self, song_id: str) -> Song:
        try:
            song_info = self.spotify_api_client.track(song_id)
            audio_features = self.spotify_api_client.audio_features(song_id)[0]
            combined_info = {**song_info, **audio_features}

            album_info = combined_info.get('album', {})
            artists_info = combined_info.get('artists', [])
            release_date_str = album_info.get('release_date')
            release_date = None
            if release_date_str:
                try:
                    release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
                except ValueError:
                    release_date = None

            filtered_song_info = {
                "id": str(combined_info.get('id', '')),
                "track_name": str(combined_info.get('name', '')),
                "album": str(album_info.get('name', '')),
                "album_id": str(album_info.get('id', '')),
                "artists": [str(artist['name']) for artist in artists_info],
                "artist_ids": [str(artist['id']) for artist in artists_info],
                "danceability": float(combined_info.get('danceability', 0.0)),
                "energy": float(combined_info.get('energy', 0.0)),
                "speechiness": float(combined_info.get('speechiness', 0.0)),
                "valence": float(combined_info.get('valence', 0.0)),
                "tempo": float(combined_info.get('tempo', 0.0)),
                "duration_ms": int(combined_info.get('duration_ms', 0)),
                "release_date": release_date,
                "popularity": float(combined_info.get('popularity', 0.0))
            }

            await self.repo.add_song_by_info(filtered_song_info)
            filtered_song_info["preview_url"] = combined_info.get('preview_url')
            return Song(**filtered_song_info)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request unsuccessful: {repr(e)}")

    # async def delete_song_from_database(self, song_id: str) -> None:
    #     await self.repo.delete_song_by_id(song_id)

    async def get_song(self, song_id: str) -> Song:
        try:
            return await self.get_song_from_database(song_id)
        except HTTPException:
            return await self.add_song_to_database(song_id)

    @staticmethod
    async def get_genre(song: Song) -> None:
        params = {
            'release_title': song.album,
            'artist': ', '.join(song.artists),
            'type': 'release',  # album/single/EP
            'token': DISCOGS_API_TOKEN
        }

        response = requests.get(DISCOGS_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]  # first result is most relevant
                genres = result.get('genre', [])
                song.genre = genres
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discogs could not be reached")

    @with_session_lock
    async def add_song_to_session(self, user_id: str, session_id: str, song_id: str) -> Playlist:
        user = await self.get_user(user_id)
        session = await self.get_session(session_id)
        if user.id not in session.guests and user.id != session.host_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not part of session")
        song = await self.get_song(song_id)
        song.added_by = user
        await self.get_genre(song)

        session.playlist.queued_songs.append(song)
        await self.repo.set_session(session)
        await self.manager.publish(channel=f"playlist:{session_id}", message=session.playlist)

        return session.playlist

    @with_session_lock
    async def remove_song_from_session(self, host_id: str, session_id: str, song_id: str) -> None:
        session = await self.get_session(session_id)
        self.verify_host_of_session(host_id, session)
        for idx, song in enumerate(session.playlist.queued_songs):
            if song.id == song_id:
                del session.playlist.queued_songs[idx]
                await self.repo.set_session(session)
                await self.manager.publish(channel=f"playlist:{session_id}", message=session.playlist)
                return

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not part of playlist")

    @with_session_lock
    async def generate_and_get_recommendations_from_database(self, session_id: str, limit: int) -> RecommendationList:
        session = await self.get_session(session_id)
        session.recommendations.clear()
        await self.repo.set_session(session)
        result = await self.repo.get_recommendations_by_songs(session.playlist.get_all_songs(), limit)
        for row in result:
            song = await self.get_song_from_database(row['id'])
            await self.get_genre(song)
            diffs = {
                'danceability': row['diff_danceability'],
                'energy': row['diff_energy'],
                'speechiness': row['diff_speechiness'],
                'valence': row['diff_valence'],
                'tempo': row['diff_tempo']
            }
            most_significant_feature = max(diffs, key=diffs.get)
            song.most_significant_feature = most_significant_feature
            song.similarity_score = (1 - (row['cosine_distance'] / math.sqrt(5)))
            session.recommendations.append(Recommendation(**song.model_dump()))
        await self.repo.set_session(session)
        await self.manager.publish(channel=f"recommendations:{session_id}", message=RecommendationList(recommendations=session.recommendations))
        return RecommendationList(recommendations=session.recommendations)

    async def get_most_popular_recommendation(self, session_id: str) -> Song:
        session = await self.get_session(session_id)
        most_popular_recommendation = max(session.recommendations, key=lambda recommendation: len(recommendation.votes))
        return await self.get_song_from_database(most_popular_recommendation.id)

    @with_session_lock
    async def add_vote_to_recommendation(self, guest_id: str, session_id: str, song_id: str) -> RecommendationList:
        session = await self.get_session(session_id)
        self.verify_guest_of_session(guest_id, session)
        curr_rec = next((rec for rec in session.recommendations if rec.id == song_id), None)
        if not curr_rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song is not recommended.")
        previous_rec = next((rec for rec in session.recommendations if guest_id in rec.votes), None)  # not None if guest has previously voted
        if previous_rec:
            previous_rec.votes.remove(guest_id)
        if guest_id in curr_rec.votes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vote already added.")
        curr_rec.votes.append(guest_id)
        await self.repo.set_session(session)
        await self.manager.publish(channel=f"recommendations:{session_id}", message=RecommendationList(recommendations=session.recommendations))
        return RecommendationList(recommendations=session.recommendations)

    @with_session_lock
    async def remove_vote_from_recommendation(self, guest_id: str, session_id: str, song_id: str) -> None:
        session = await self.get_session(session_id)
        self.verify_guest_of_session(guest_id, session)
        curr_rec = next((rec for rec in session.recommendations if rec.id == song_id), None)
        if not curr_rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song is not recommended.")
        if guest_id not in curr_rec.votes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No vote added prior.")
        curr_rec.votes.remove(guest_id)
        await self.repo.set_session(session)
        await self.manager.publish(channel=f"recommendations:{session_id}", message=RecommendationList(recommendations=session.recommendations))

    async def get_matching_songs_from_database(self, pattern: str, limit: int) -> SongList:
        result = await self.repo.get_songs_by_pattern(pattern, limit)
        songs = [Song.model_validate(dict(row)) for row in result]
        return SongList(songs=songs)
