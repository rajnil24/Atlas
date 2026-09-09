import { useState } from "react";
import "./App.css";

const API_URL = "http://13.204.159.23:8000";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);

  async function login() {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "Login failed");
      return;
    }

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);

    setLoggedIn(true);
  }

  async function sendMessage() {
    const token = localStorage.getItem("access_token");

    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        session_id: sessionId,
        message,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.detail || "Request failed");
      return;
    }

    setReply(data.message);
    setMessage("");
  }

  if (!loggedIn) {
    return (
      <div className="container">
        <h1>Atlas</h1>

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={login}>Login</button>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Atlas</h1>

      <input
        placeholder="Session ID"
        value={sessionId}
        onChange={(e) => setSessionId(e.target.value)}
      />

      <textarea
        placeholder="Ask Atlas something..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      <button onClick={sendMessage}>Send</button>

      <div className="reply">
        <strong>Atlas:</strong>
        <p>{reply}</p>
      </div>
    </div>
  );
}

export default App;