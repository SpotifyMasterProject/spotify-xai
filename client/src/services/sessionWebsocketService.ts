import { SessionMessageType } from "@/types/SessionMessage";
import type { SessionMessage } from "@/types/SessionMessage";

export class SessionWebsocketService {
    socket: WebSocket | null
    reconnectTimeout: number;
    maxReconnectAttempts: number;
    reconnectAttempts: number;

    constructor() {
        this.reconnectTimeout = 2000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        this.socket = null;
    }

    connect(sessionId: string, handler: ((message: SessionMessage) => void)) {
        this.socket = new WebSocket(`ws://${import.meta.env.VITE_LOCAL_IP_ADDRESS}:8000/ws/${sessionId}`)

        this.socket.onopen = () => {
            console.log('Websocket connection established!')
            this.reconnectAttempts = 0;
        }

        this.socket.onmessage = (event) => {
            console.log('Message received:' + event.data);
            handler(convertMessage(event.data));
        }

        this.socket.onclose = (event) => {
            console.log('Websocket disconnected! Attempting to reconnect.')
            if (event.code !== 1000) { // Do not attempt to reconnect if the connection was closed normally (code 1000)
                this.attemptReconnect(sessionId, handler);
            }
        }

        this.socket.onerror = (event) => {
            console.log('Websocket error:' + event)
            this.socket?.close()
        }
    }

    attemptReconnect(sessionId: string, handler: ((message: SessionMessage) => void)) {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                console.log('Attempting to reconnect to WebSocket...');
                this.reconnectAttempts++;
                this.connect(sessionId, handler);
            }, this.reconnectTimeout);
            this.reconnectTimeout *= 2; // Exponential backoff
        } else {
            console.log('Max reconnection attempts reached. Could not reconnect to WebSocket.');
        }
    }

    sendMessage(message: string) {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket?.send(message);
        } else {
            console.log('WebSocket is not open. Cannot send message.');
        }
    }

    close() {
        this.socket?.close(1000, 'Client closed connection.'); // Close with normal closure code 1000
    }
}

function convertMessage(message: string): SessionMessage {
  const guestAddedRegex = /Guest ([0-9a-f\-]*):(.*) has joined the session/i;
  const guestRemovedRegex = /Guest ([0-9a-f\-]*) was removed from session by host/i;

  const guestAdded = message.match(guestAddedRegex);
  const guestRemoved = message.match(guestRemovedRegex);

  if (guestAdded) {
    const id = guestAdded[1];
    const username = guestAdded[2];

    return {
      type: SessionMessageType.GUEST_ADDED,
      guest: {
        id, username, isHost: false, sessions: []
      }
    };
  } else if (guestRemoved) {
    const guestId = guestRemoved[1];
    return {
      type: SessionMessageType.GUEST_REMOVED,
      guestId
    };
  }

  return {
    type: SessionMessageType.UNKNOWN
  };
}