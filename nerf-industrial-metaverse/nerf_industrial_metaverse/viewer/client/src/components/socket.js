import { io } from 'socket.io-client';

export const socket = io('localhost:5000', {
    cors: {
        origin: "localhost:3000",
        methods: ["GET", "POST"],
        credentials: true,
        transports: ['websocket', 'polling'],
    },
    allowEIO3: true,
    reconnection: true,         // Aktiviere die automatische Reconnect-Funktion
    reconnectionAttempts: 10,    // Anzahl der Reconnect-Versuche
    reconnectionDelay: 10000,    // Verzögerung zwischen Reconnect-Versuchen in Millisekunden
    reconnectionDelayMax: 50000, // Maximale Verzögerung zwischen Reconnect-Versuchen
});