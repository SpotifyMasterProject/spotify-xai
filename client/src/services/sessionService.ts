import apiClient from '@/services/axios';
import { Session } from '@/types/Session';
import { Song } from '@/types/Song';
import { SongFeatureCategory } from '@/types/SongFeature';
import type { SongFeature } from '@/types/SongFeature';

export const sessionService = {

    async joinSession(sessionId: string): Promise<Session> {
        return apiClient.post(`/sessions/${sessionId}/guests`).then((response) => {
            return response.data;
        })
    },
    async getSessions(): Promise<Session[]> {
        return apiClient.get('/sessions').then((response) => {
            return response.data;
        })
    },
    async getSessionById(sessionId: string): Promise<Session> {
        return apiClient.get(`/sessions/${sessionId}`).then((response) => {
            return response.data;
        })
    },
    async getSongs(pattern: string): Promise<Song[]> {
        return apiClient.get(`/songs`, {params: {pattern}}).then((response) => {
            return response.data['songs'];
        })
    },
    async createNewSession(session: Session): Promise<Session> {
        return apiClient.post(`/sessions`, {...session}).then((response) => {
            return response.data;
        })
    },
    async getRecommendations(sessionId: string): Promise<Song[]> {
        return apiClient.patch(`/sessions/${sessionId}/recommendations`).then((response) => {
            return response.data['songs'];
        })
    },
    async addSong(sessionId: string, songId: string): Promise<Session> {
        return apiClient.patch(
            `/sessions/${sessionId}/songs`, null,
            {params: {songId}}).then((response) => {
            return response.data;
        })
    }
};

export const getSongFeatures = (song: Song): SongFeature[] => {
    return [
        {
            category: SongFeatureCategory.TEMPO,
            value: song.scaledTempo
        },
        {
            category: SongFeatureCategory.ENERGY,
            value: song.energy
        },
        {
            category: SongFeatureCategory.VALENCE,
            value: song.valence
        },
            {
            category: SongFeatureCategory.DANCEABILITY,
            value: song.danceability
        },
        {
            category: SongFeatureCategory.SPEECHINESS,
            value: song.speechiness
        },
    ];
}