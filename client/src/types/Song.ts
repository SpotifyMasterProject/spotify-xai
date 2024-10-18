export class Song {
    id: string
    trackName: string
    artists: string[]
    album: string
    danceability: number
    energy: number
    speechiness: number
    valence: number
    tempo: number
    scaledTempo: number
    releaseDate: string
    popularity: number
    durationMs: number
    genre: string

    constructor(data: Song) {
        this.id = data.id
        this.trackName = data.trackName
        this.artists = data.artists
        this.album = data.album
        this.danceability = data.danceability
        this.energy = data.energy
        this.speechiness = data.speechiness
        this.valence = data.valence
        this.tempo = data.tempo
        this.scaledTempo = data.scaledTempo
        this.releaseDate = data.releaseDate
        this.popularity = data.popularity
        this.durationMs = data.durationMs
        this.genre = data.genre
    }
}