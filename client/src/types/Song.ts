export class Song {
    id: string
    name: string
    artists: string[]

    constructor(data: {
        id: string
        name: string
        artists: string[]
    }) {
        this.id = data.id
        this.name = data.name
        this.artists = data.artists
    }
}
