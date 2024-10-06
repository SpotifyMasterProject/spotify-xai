import { User } from "./User";

export type SessionMessage = SessionMessageGuestAdded | SessionMessageGuestRemoved;


export interface SessionMessageGuestAdded {
    type: SessionMessageType.GUEST_ADDED,
    guest: User,
};

export interface SessionMessageGuestRemoved {
    type: SessionMessageType.GUEST_REMOVED,
    guestId: string,
};

export interface SessionMessageUnknown {
    type: SessionMessageType.UNKNOWN,
}

export enum SessionMessageType {
    GUEST_ADDED,
    GUEST_REMOVED,
    UNKNOWN
};