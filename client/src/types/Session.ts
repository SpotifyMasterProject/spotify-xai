import { User } from './User';
import { Song } from './Song';

export class HostSession {
    id: string
    invitationLink: string
    guests: User[]
    playlistName: string
    playlist: Song[]
    creationDate: Date
    isRunning: boolean

    constructor(data: {
        id: string
        invitationLink: string
        guests: User[]
        playlistName: string
        playlist: Song[]
        creationDate: Date
        isRunning: boolean
    }) {
        this.id = data.id
        this.invitationLink = data.invitationLink
        this.playlistName = data.playlistName
        this.guests = data.guests
        this.playlist = data.playlist
        this.creationDate = data.creationDate
        this.isRunning = data.isRunning ?? false
    }
}
