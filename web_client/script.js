const app = {
    ws: null,
    clientId: Math.floor(Math.random() * 1000000),
    isHost: false,

    // Config - Try to detect Render URL or fallback to localhost
    // USER: IF DEPLOYED, CHANGE THIS TO YOUR RENDER URL e.g. "wss://your-app.onrender.com"
    wsUrl: window.location.hostname === "localhost"
        ? "ws://localhost:8000"
        : "wss://" + window.location.hostname,

    init: function () {
        console.log("App Initialized. Server set to: " + this.wsUrl);
        // If connecting to a remote backend from localhost (for testing):
        // this.wsUrl = "wss://edu-party-server.onrender.com"; // UNCOMMENT FOR LOCAL WEB TESTING
    },

    login: function () {
        const username = document.getElementById('username-input').value;
        if (!username) return alert("Please enter a name!");

        this.username = username;
        this.connect();
    },

    connect: function () {
        // Change status to "Connecting" visual
        document.getElementById('connection-status').className = "status-badge connecting";

        const url = `${this.wsUrl}/ws/${this.clientId}`;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            document.getElementById('connection-status').innerText = "ONLINE";
            document.getElementById('connection-status').className = "status-badge online";
            this.showView('view-menu');
        };

        this.ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            this.handleMessage(msg);
        };

        this.ws.onclose = () => {
            alert("Connection Lost!");
            location.reload();
        };
    },

    createLobby: function () {
        this.send({ command: "CREATE", username: this.username });
        this.isHost = true;
    },

    joinLobby: function () {
        const code = document.getElementById('join-code-input').value;
        if (!code) return alert("Enter Code!");
        this.send({ command: "JOIN", code: code, username: this.username });
    },

    startGame: function () {
        this.send({ command: "START_GAME" });
    },

    submitInput: function () {
        const val = document.getElementById('game-input').value;
        this.send({ command: "GAME_INPUT", input: val });
        document.getElementById('game-input').value = "";
    },

    send: function (data) {
        if (this.ws) this.ws.send(JSON.stringify(data));
    },

    handleMessage: function (msg) {
        console.log("RX:", msg);

        switch (msg.type) {
            case "LOBBY_CREATED":
            case "LOBBY_JOINED":
                this.lobbyCode = msg.code;
                document.getElementById('lobby-code-display').innerText = msg.code;
                this.showView('view-lobby');
                if (this.isHost) document.getElementById('host-controls').style.display = "block";
                break;

            case "PLAYER_LIST":
                const list = document.getElementById('player-list');
                list.innerHTML = msg.players.map(p =>
                    `<div class="player-item ${p.is_host ? 'host' : ''}">${p.username}</div>`
                ).join('');
                break;

            case "GAME_START":
                // Hide Launcher, Show Game
                document.getElementById('launcher-container').style.display = 'none';
                document.getElementById('game-container').style.display = 'flex';
                break;

            case "ROUND_START":
                document.getElementById('round-display').innerText = "Round " + msg.round;
                document.getElementById('instruction-display').innerText = msg.instruction;

                // Popup
                document.getElementById('popup-title').innerText = "Round " + msg.round;
                document.getElementById('popup-msg').innerText = msg.instruction;
                document.getElementById('game-popup').classList.add('active');
                break;

            case "gamestate":
                document.getElementById('feedback-display').innerText = msg.msg;
                // Visual feedback
                break;

            case "ELIMINATED":
                alert("YOU DIED! Game Over.");
                location.reload();
                break;

            case "GAME_OVER":
                this.showView('view-result');
                document.getElementById('winner-display').innerText = "Winner: " + msg.winner;
                break;
        }
    },

    showView: function (viewId) {
        document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
        document.getElementById(viewId).classList.add('active');
    },

    dismissPopup: function () {
        document.getElementById('game-popup').classList.remove('active');
        document.getElementById('game-input').focus();
    }
};

app.init();
