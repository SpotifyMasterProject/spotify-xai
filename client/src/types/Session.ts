import { User } from './User';
import { Song } from './Song';

export class Session {
    id: string
    name: string
    hostName: string
    inviteLink: string
    guests: {[key: string]: User}
    playlist: Song[]
    creationDate: Date
    isRunning: boolean

    constructor(data: {
        id: string
        name: string
        hostName: string
        inviteLink: string
        guests:  {[key: string]: User}
        playlistName: string
        playlist: Song[]
        creationDate: Date
        isRunning: boolean
    }) {
        this.id = data.id
        this.name = data.name
        this.hostName = data.hostName
        this.inviteLink = data.inviteLink
        this.guests = data.guests
        this.playlist = data.playlist
        this.creationDate = data.creationDate
        this.isRunning = data.isRunning ?? true
    }
}

