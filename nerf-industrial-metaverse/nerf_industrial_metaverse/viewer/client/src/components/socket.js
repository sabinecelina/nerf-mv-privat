import { io } from 'socket.io-client';

export const socket = io('http://localhost:5000', {
    cors: {
        origin: "http://localhost:3000",
        methods: ["GET", "POST"],
        credentials: true,
        transports: ['websocket', 'polling'],
    },
    allowEIO3: true
});
