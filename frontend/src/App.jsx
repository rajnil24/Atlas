import { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");

  if (!refreshToken) {
    return false;
  }

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
  });

  if (!response.ok) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return false;
  }

  const data = await response.json();

  localStorage.setItem("access_token", data.access_token);

  return true;
}

async function authenticatedFetch(url, options = {}) {
  let accessToken = localStorage.getItem("access_token");

  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (response.status !== 401) {
    return response;
  }

  const refreshed = await refreshAccessToken();

  if (!refreshed) {
    return response;
  }

  accessToken = localStorage.getItem("access_token");

  response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return response;
}

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [sessionId, setSessionId] = useState("");
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");

  const [loggedIn, setLoggedIn] = useState(
    Boolean(localStorage.getItem("access_token"))
  );

  const [status, setStatus] = useState("");

  async function login() {
    setStatus("Logging in...");

    try {
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
        setStatus(`Login failed: ${data.detail || "Unknown error"}`);
        return;
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      setLoggedIn(true);
      setStatus("Login successful!");
    } catch (error) {
      setStatus(`Network error: ${error.message}`);
    }
  }

  async function sendMessage() {
    setStatus("Sending...");

    try {
      const response = await authenticatedFetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setStatus(`Request failed: ${data.detail || "Unknown error"}`);
        return;
      }

      setReply(data.message);
      setMessage("");
      setStatus("Message sent successfully!");
    } catch (error) {
      setStatus(`Network error: ${error.message}`);
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    setLoggedIn(false);
    setReply("");
    setStatus("Logged out");
  }

  if (!loggedIn) {
    return (
      <div className="container">
        <h1>Atlas</h1>
        <h2>Login</h2>

        <input
          type="email"
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

        <p>{status}</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Atlas</h1>

      <button onClick={logout}>Logout</button>

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

      <p>{status}</p>

      <div className="reply">
        <strong>Atlas:</strong>
        <p>{reply}</p>
      </div>
    </div>
  );
}

export default App;