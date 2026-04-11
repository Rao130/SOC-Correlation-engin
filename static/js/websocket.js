// WebSocket functionality completely disabled
// No WebSocket connections will be made
console.log('WebSocket functionality disabled');

// Empty stub to prevent errors
class DisabledWebSocket {
    constructor() {
        this.isConnected = false;
    }
    
    connect() {
        console.log('WebSocket connection disabled');
        return false;
    }
    
    disconnect() {
        console.log('WebSocket already disconnected');
    }
    
    handleMessage() {
        // No messages will be handled
    }
}

// Create disabled instance
window.wsManager = new DisabledWebSocket();

// No automatic connections
document.addEventListener('DOMContentLoaded', () => {
    console.log('WebSocket auto-connect disabled');
});
