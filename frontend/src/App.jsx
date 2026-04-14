import React, { useState, useEffect, useRef } from 'react';
import './index.css';

const AGENTS = [
  { id: 'manager', name: 'Manager Agent', icon: '🧠' },
  { id: 'planner', name: 'Planner Agent', icon: '🟣' },
  { id: 'executor', name: 'Executor Agent', icon: '🔧' },
  { id: 'critic', name: 'Critic Agent', icon: '🛡️' }
];

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Ready to assist! Describe what you want to create in Blender.', type: 'welcome' }
  ]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState({}); // { manager: { status: '...', state: 'DONE' }, ... }
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const ws = useRef(null);
  const sessionId = 'blender_user_1'; // In real use, this would be passed from Blender

  useEffect(() => {
    connectWS();
    return () => { if (ws.current) ws.current.close(); };
  }, []);

  const connectWS = () => {
    ws.current = new WebSocket(`ws://localhost:8000/ws/progress/${sessionId}`);
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => {
      setIsConnected(false);
      setTimeout(connectWS, 2000); // Auto-reconnect
    };
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.agent) {
        setStatus(prev => ({
          ...prev,
          [data.agent.toLowerCase()]: { status: data.status, state: data.state }
        }));
      }
    };
  };

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;
    
    setIsProcessing(true);
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setStatus({}); // Reset agent statuses

    try {
      const response = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: userMsg,
          api_key: 'sk-experimental-key', // Placeholder: logic to get this from Blender prefs
          session_id: sessionId
        })
      });

      const result = await response.json();
      if (response.ok) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          text: result.status === 'NEEDS_APPROVAL' ? `⚠️ SECURITY CHECK: I need your approval to execute this system command.` : `Task completed! I've generated the logic.`,
          code: result.code,
          isResult: true,
          needsApproval: result.status === 'NEEDS_APPROVAL',
          reason: result.reason
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${result.detail || 'Failed to generate code.'}`, isError: true }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Backend offline. Please launch the AI Backend from Blender.', isError: true }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExecute = async (code) => {
    try {
      await fetch(`http://localhost:8000/submit_execution/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      // Optionally show a toast that it's sent to Blender
    } catch (err) {
      console.error('Failed to bridge code:', err);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo-section">
          <div className="logo-icon">B</div>
          <div className="logo-text">
            <h1>BlendAI Assistant</h1>
            <p>Assistant for Blender</p>
          </div>
        </div>
        <div>
          <div className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'CONNECTED' : 'OFFLINE'}
          </div>
          <div className="backend-info">Backend: http://localhost:8000</div>
        </div>
      </header>

      <div className="main-panel">
        <div className="chat-history">
          {messages.map((msg, i) => (
            <div key={i} className={`message-bubble ${msg.role}`}>
              <div className="message-content">
                {msg.text}
                {msg.code && (
                  <div className="result-card">
                    <div className="preview-placeholder">
                      <div className="code-snippet-title">Generated Logic:</div>
                      <pre><code>{msg.code.substring(0, 100)}...</code></pre>
                    </div>
                    <div className="result-actions">
                      {msg.needsApproval ? (
                        <div className="approval-block">
                          <p className="approval-reason">{msg.reason}</p>
                          <div className="approval-row">
                            <button className="danger-btn" onClick={() => setMessages(prev => prev.filter((_, idx) => idx !== i))}>DENY</button>
                            <button className="primary-btn" onClick={() => { handleExecute(msg.code); msg.needsApproval = false; setMessages([...messages]); }}>APPROVE & RUN</button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <button className="secondary-btn" onClick={() => handleExecute(msg.code)}>VIEW IN 3D</button>
                          <button className="primary-btn">REFINE</button>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="agent-status-card">
              {AGENTS.map(agent => {
                const state = status[agent.id]?.state || 'WAITING';
                return (
                  <div key={agent.id} className={`agent-item ${state.toLowerCase()}`}>
                    <div className="agent-icon">{agent.icon}</div>
                    <div className="agent-info">
                      <h4>{agent.name}</h4>
                      <p>{status[agent.id]?.status || 'Waiting for mission start...'}</p>
                    </div>
                    <div className={`agent-badge ${state.toLowerCase()}`}>{state}</div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="input-section">
          <div className="input-wrapper">
            <textarea 
              placeholder="Describe what you want to create..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
            />
            <div className="input-actions">
              <div className="char-count">{input.length} / 2000</div>
              <button className="send-btn" onClick={handleSend} disabled={isProcessing}>
                {isProcessing ? 'PROCESSING...' : 'SEND'}
              </button>
            </div>
          </div>

          <div className="quick-actions">
            <span className="action-chip">⚡ Add Lighting</span>
            <span className="action-chip">🎥 Add Camera</span>
            <span className="action-chip">🏠 Create Room</span>
            <span className="action-chip">📦 Import Model</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
