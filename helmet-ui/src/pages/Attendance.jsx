import  { useRef, useState, useEffect, useCallback } from "react";
import axios from "axios";
import whCode from "../assets/wh_code.jpeg";
import "../css/Attendance.css";

const API_BASE = "http://54.89.130.2:8001";
const WS_BASE = "ws://54.89.130.2:8001";

const ATTENDANCE_SETUP_STEPS = [
  "Scan the WH code at shift start to open attendance verification.",
  "Ensure the stream has clear face visibility and stable lighting.",
  "Use the same identity used during employee face registration.",
];

// ─────────────────────────────────────────────────────────────────────────────
// Source Selection Modal
// ─────────────────────────────────────────────────────────────────────────────
function SourceModal({ onSelect }) {
  const [screen,  setScreen]  = useState("pick");
  const [rtspUrl, setRtspUrl] = useState("");

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 1000,
      background: "rgba(8,10,16,0.92)", backdropFilter: "blur(10px)",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "var(--font)",
    }}>
      <div style={{
        background: "var(--surface)", border: "1px solid var(--border2)",
        borderRadius: 12, padding: "32px 28px", width: "min(420px, 92vw)",
        boxShadow: "0 40px 80px rgba(0,0,0,0.6)",
        animation: "fade-up 0.28s ease",
        position: "relative", overflow: "hidden",
      }}>
        {/* scanlines */}
        <div style={{
          position: "absolute", inset: 0, pointerEvents: "none",
          backgroundImage: "repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(255,255,255,0.012) 2px,rgba(255,255,255,0.012) 4px)",
          borderRadius: 12,
        }} />

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 26 }}>
          <div style={{
            width: 46, height: 46, borderRadius: 10,
            background: "var(--blue-lo)", border: "1px solid rgba(59,130,246,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 20, margin: "0 auto 12px",
          }}>👁</div>
          <h2 style={{ fontSize: 17, fontWeight: 600, color: "var(--text)", marginBottom: 5 }}>
            Attendance Monitor
          </h2>
          <p style={{ fontSize: 12, color: "var(--muted)", fontFamily: "var(--mono)" }}>
            Select input source to begin
          </p>

          
        </div>
        

        {screen === "pick" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { mode: "webcam", icon: "📷", label: "Webcam",           desc: "Device built-in or USB camera" },
              { mode: "cctv",   icon: "📡", label: "CCTV / IP Camera", desc: "RTSP stream via backend" },
            ].map(({ mode, icon, label, desc }) => (
              <button
                key={mode}
                onClick={() => mode === "webcam" ? onSelect({ mode }) : setScreen("cctv")}
                style={{
                  display: "flex", alignItems: "center", gap: 12,
                  background: "var(--bg)", border: "1px solid var(--border)",
                  borderRadius: "var(--r)", padding: "13px 15px",
                  cursor: "pointer", textAlign: "left", width: "100%",
                  transition: "border-color 0.15s, background 0.15s",
                  fontFamily: "var(--font)",
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--border2)"; e.currentTarget.style.background = "#1a1f2e"; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border)";  e.currentTarget.style.background = "var(--bg)"; }}
              >
                <span style={{ fontSize: 18 }}>{icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text)", marginBottom: 2 }}>{label}</div>
                  <div style={{ fontSize: 11, color: "var(--muted)" }}>{desc}</div>
                </div>
                <span style={{ color: "var(--dim)", fontSize: 18 }}>›</span>
              </button>
            ))}
          </div>
        )}

        {screen === "cctv" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <button
              onClick={() => setScreen("pick")}
              style={{
                background: "none", border: "none", color: "var(--muted)",
                cursor: "pointer", fontFamily: "var(--font)", fontSize: 13,
                textAlign: "left", padding: 0,
              }}
            >← Back</button>
            <div>
              <label style={{
                fontSize: 10, color: "var(--muted)", display: "block",
                marginBottom: 6, letterSpacing: "0.08em", textTransform: "uppercase",
                fontFamily: "var(--mono)",
              }}>
                RTSP Stream URL
              </label>
              <input
                type="text"
                placeholder="rtsp://user:pass@192.168.1.100:554/stream"
                value={rtspUrl}
                onChange={e => setRtspUrl(e.target.value)}
                autoFocus
                style={{
                  width: "100%", background: "var(--bg)",
                  border: "1px solid var(--border2)", borderRadius: 6,
                  color: "var(--text)", fontFamily: "var(--mono)",
                  fontSize: 12, padding: "10px 12px", outline: "none",
                }}
              />
              <p style={{ fontSize: 11, color: "var(--muted)", marginTop: 7, lineHeight: 1.55, fontFamily: "var(--mono)" }}>
                Backend will connect and forward processed frames.
              </p>
            </div>

            <button
              disabled={!rtspUrl.trim()}
              onClick={() => onSelect({ mode: "cctv", rtspUrl: rtspUrl.trim() })}
              style={{
                background: rtspUrl.trim() ? "var(--blue)" : "var(--dim)",
                color: rtspUrl.trim() ? "#fff" : "var(--muted)",
                border: "none", borderRadius: 6, padding: 11,
                fontFamily: "var(--font)", fontWeight: 600, fontSize: 13,
                cursor: rtspUrl.trim() ? "pointer" : "not-allowed",
                transition: "all 0.15s",
              }}
            >Connect</button>
          </div>
        )}

        
      </div>
      
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Control Button
// ─────────────────────────────────────────────────────────────────────────────
function Btn({ onClick, disabled, variant = "ghost", children, title }) {
  const map = {
    green:  { bg: "#1a7a3a", fg: "#fff",           border: "none" },
    red:    { bg: "#7a1a1a", fg: "#fff",            border: "none" },
    blue:   { bg: "#1a3a7a", fg: "#fff",            border: "none" },
    amber:  { bg: "rgba(245,158,11,0.12)", fg: "var(--amber)", border: "1px solid rgba(245,158,11,0.35)" },
    ghost:  { bg: "transparent", fg: "var(--muted)", border: "1px solid var(--border)" },
  };
  const c = disabled
    ? { bg: "#151515", fg: "#333", border: "1px solid var(--border)" }
    : map[variant];

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      style={{
        padding: "0.45rem 1rem",
        background: c.bg, color: c.fg, border: c.border,
        borderRadius: 5, cursor: disabled ? "not-allowed" : "pointer",
        fontFamily: "var(--font)", fontWeight: 600, fontSize: 13,
        opacity: disabled ? 0.45 : 1, transition: "opacity 0.15s",
        whiteSpace: "nowrap",
      }}
    >{children}</button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────
export default function AttendanceViewer() {
  const videoRef   = useRef(null);
  const imgRef     = useRef(null);
  const wsRef      = useRef(null);
  const runningRef = useRef(false);
  const capRef     = useRef(false);

  const [running,    setRunning]    = useState(false);
  const [status,     setStatus]     = useState("");
  const [fullscreen, setFullscreen] = useState(false);
  const [showModal,  setShowModal]  = useState(true);
  const [mode,       setMode]       = useState(null);   // "webcam" | "cctv"
  const [rtspUrl,    setRtspUrl]    = useState("");
  const [frameCount, setFrameCount] = useState(0);
  const [fps,        setFps]        = useState(1);   // frames per second
  const [isWhExpanded, setIsWhExpanded] = useState(false);
  const fpsRef       = useRef(1);                    // always-current value for loop

  // ESC exits fullscreen
  useEffect(() => {
    const fn = (e) => {
      if (e.key !== "Escape") return;
      if (isWhExpanded) {
        setIsWhExpanded(false);
        return;
      }
      if (fullscreen) setFullscreen(false);
    };
    window.addEventListener("keydown", fn);
    return () => window.removeEventListener("keydown", fn);
  }, [fullscreen, isWhExpanded]);

  // Cleanup on unmount
  useEffect(() => () => stopCapture(), []);

  // Keep ref in sync so captureLoop reads latest without re-creating
  useEffect(() => { fpsRef.current = fps; }, [fps]);

  const buildWsUrl = useCallback((m, r) => {
    const token = sessionStorage.getItem("token");
    const base = `${WS_BASE}/ws/attendance?token=${token}`;
    if (m === "cctv") return `${base}&rtsp_url=${encodeURIComponent(r)}`;
    return base;
  }, []);

  const stopCapture = useCallback(() => {
    runningRef.current = false;
    capRef.current = false;
    wsRef.current?.close();
    wsRef.current = null;
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      videoRef.current.srcObject = null;
    }
    if (imgRef.current) imgRef.current.src = "";
    setRunning(false);
    setStatus("Stopped.");
  }, []);

  const captureLoop = useCallback(async () => {
    if (capRef.current) return;
    capRef.current = true;
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    try {
      while (runningRef.current) {
        const video = videoRef.current;
        const ws    = wsRef.current;
        if (!video || video.videoWidth === 0 || !ws || ws.readyState !== WebSocket.OPEN) {
          await new Promise(r => setTimeout(r, 200));
          continue;
        }
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const b64 = canvas.toDataURL("image/jpeg", 0.7).split(",")[1];
        if (runningRef.current && wsRef.current?.readyState === WebSocket.OPEN)
          wsRef.current.send(JSON.stringify({ image: b64 }));
        await new Promise(r => setTimeout(r, 1000 / fpsRef.current));
      }
    } finally { capRef.current = false; }
  }, []);

  const handleSelect = ({ mode: m, rtspUrl: r = "" }) => {
    setMode(m);
    setRtspUrl(r);
    setShowModal(false);
    setStatus(`Source: ${m === "webcam" ? "Webcam" : r}`);
  };

  const switchSource = () => {
    stopCapture();
    setMode(null); setRtspUrl("");
    setStatus(""); setShowModal(true);
    setFrameCount(0);
    setFps(1); fpsRef.current = 1;
    setIsWhExpanded(false);
  };

  const start = async () => {
    if (mode === "webcam") {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      } catch {
        setStatus("Camera access denied."); return;
      }
    }

    const ws = new WebSocket(buildWsUrl(mode, rtspUrl));
    wsRef.current = ws;
    runningRef.current = true;
    setRunning(true);
    setFrameCount(0);
    setStatus("Connecting…");

    ws.onopen = () => {
      setStatus(`Connected — ${mode === "cctv" ? "CCTV stream" : "Webcam"} active`);
      if (mode === "webcam") captureLoop();
    };

    ws.onmessage = (msg) => {
      let data;
      try { data = JSON.parse(msg.data); } catch { return; }
      if (data.error) {
        setStatus(`Error: ${data.error}`);
        stopCapture(); return;
      }
      if (data.image && imgRef.current) {
        imgRef.current.src = `data:image/jpeg;base64,${data.image}`;
        setFrameCount(p => p + 1);
      }
    };

    ws.onclose = () => { setStatus("Connection closed."); stopCapture(); };
    ws.onerror = () => { setStatus("Connection failed — server unavailable."); stopCapture(); };
  };

  const reload = async () => {
    const token = sessionStorage.getItem("token");
    setStatus("Reloading face index…");
    try {
      const res = await axios.post(
        `${API_BASE}/attendance/reload_index`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setStatus(res.data.message ?? "Index reloaded.");
    } catch (err) {
      const s = err.response?.status;
      setStatus(
        s === 401 ? "Unauthorized — please log in." :
        s === 403 ? "Forbidden — insufficient permissions." :
        `Failed: ${err.response?.data?.detail ?? err.message}`
      );
    }
  };

  // Container style: partial vs fullscreen
  const containerStyle = {
    fontFamily: "var(--font)",
    background: "var(--bg)",
    color: "var(--text)",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    height: "100%",
    ...(fullscreen
      ? { position: "fixed", inset: 0, zIndex: 999, height: "100vh" }
      : {}
    ),
  };

  return (
    <div style={containerStyle}>
      {showModal && <SourceModal onSelect={handleSelect} />}

      {/* ── Top bar ── */}
      <header style={{
        display: "flex", alignItems: "center",
        justifyContent: "space-between",
        padding: "11px 18px",
        background: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        gap: 12, flexShrink: 0, flexWrap: "wrap",
      }}>
        
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 7,
            background: "var(--blue-lo)",
            border: "1px solid rgba(59,130,246,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 15, flexShrink: 0,
          }}>👁</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", lineHeight: 1.2 }}>
              Attendance Monitor
            </div>
            <div style={{ fontFamily: "var(--mono)", fontSize: 9, color: "var(--muted)" }}>
              FACE RECOGNITION
            </div>
          </div>
        </div>

        {/* Live badge + source */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {running ? (
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <span style={{
                width: 6, height: 6, borderRadius: "50%",
                background: "var(--green)",
                animation: "pulse-dot 1.4s ease infinite", flexShrink: 0,
              }} />
              <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--green)", letterSpacing: "0.08em" }}>
                LIVE
              </span>
            </div>
          ) : mode ? (
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--muted)", flexShrink: 0 }} />
              <span style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--muted)", letterSpacing: "0.08em" }}>
                STANDBY
              </span>
            </div>
          ) : null}

          {mode && (
            <span style={{
              fontFamily: "var(--mono)", fontSize: 9, color: "var(--muted)",
              background: "var(--bg)", border: "1px solid var(--border)",
              borderRadius: 4, padding: "2px 7px",
            }}>
              {mode === "webcam" ? "WEBCAM" : "CCTV"}
            </span>
          )}

          {running && (
            <span style={{
              fontFamily: "var(--mono)", fontSize: 9, color: "var(--dim)",
              background: "var(--bg)", border: "1px solid var(--border)",
              borderRadius: 4, padding: "2px 7px",
            }}>
              {frameCount} frames
            </span>
          )}
        </div>

        {/* Controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginLeft: "auto" }}>

          {/* FPS control */}
          <div style={{
            display: "flex", alignItems: "center", gap: 7,
            background: "var(--bg)", border: "1px solid var(--border)",
            borderRadius: 5, padding: "4px 10px",
          }}>
            <span style={{ fontFamily: "var(--mono)", fontSize: 9, color: "var(--muted)", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>
              FPS
            </span>
            <input
              type="range"
              min={1} max={10} step={1}
              value={fps}
              disabled={running}
              onChange={e => { const v = Number(e.target.value); setFps(v); fpsRef.current = v; }}
              title={`${fps} frame${fps > 1 ? "s" : ""} per second`}
              style={{
                width: 72, accentColor: "var(--blue)",
                cursor: running ? "not-allowed" : "pointer",
                opacity: running ? 0.4 : 1,
              }}
            />
            <span style={{
              fontFamily: "var(--mono)", fontSize: 11, fontWeight: 500,
              color: "var(--text)", minWidth: 18, textAlign: "right",
            }}>
              {fps}
            </span>
          </div>

          <Btn onClick={reload}      disabled={!mode}    variant="blue">
            ↺ Reload Index
          </Btn>
          <Btn onClick={start}       disabled={running || !mode} variant="green">
            ▶ Start
          </Btn>
          <Btn onClick={stopCapture} disabled={!running} variant="red">
            ■ Stop
          </Btn>
          {mode && (
            <Btn onClick={switchSource} disabled={running} variant="ghost">⇄</Btn>
          )}

          {/* Fullscreen toggle */}
          <button
            onClick={() => setFullscreen(p => !p)}
            title={fullscreen ? "Exit fullscreen (Esc)" : "Enter fullscreen"}
            style={{
              padding: "0.4rem 0.55rem",
              background: fullscreen ? "rgba(245,158,11,0.1)" : "transparent",
              border: `1px solid ${fullscreen ? "rgba(245,158,11,0.35)" : "var(--border)"}`,
              borderRadius: 5, cursor: "pointer",
              color: fullscreen ? "var(--amber)" : "var(--muted)",
              fontSize: 14, lineHeight: 1,
              transition: "all 0.15s",
            }}
          >
            {fullscreen ? "⊠" : "⛶"}
          </button>
        </div>
      </header>

      {/* ── Status strip ── */}
      {status && (
        <div style={{
          padding: "4px 18px",
          background: "var(--surface)",
          borderBottom: "1px solid var(--border)",
          fontFamily: "var(--mono)", fontSize: 10,
          color: "var(--muted)", letterSpacing: "0.03em",
          flexShrink: 0,
        }}>
          {status}
        </div>
      )}

      {/* ── Feed ── */}
      <div style={{ flex: 1, display: "flex", background: "#07090f", overflow: "hidden" }}>

        <div style={{ flex: 1, minWidth: 0, position: "relative", background: "#07090f", overflow: "hidden" }}>
          {/* Hidden live webcam video (used for capture only) */}
          <video ref={videoRef} autoPlay muted playsInline style={{ display: "none" }} />

          {/* Annotated frame from backend */}
          <img
            ref={imgRef}
            alt="Attendance feed"
            style={{
              position: "absolute", inset: 0,
              width: "100%", height: "100%",
              objectFit: "contain", display: "block",
            }}
          />

          {/* Empty state */}
          {!running && (
            <div style={{
              position: "absolute", inset: 0,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              gap: 10, pointerEvents: "none",
              background: "rgba(7,9,15,0.7)",
            }}>
              <div style={{ fontSize: 36, opacity: 0.1 }}>👁</div>
              <span style={{
                fontFamily: "var(--mono)", fontSize: 11,
                color: "var(--dim)", letterSpacing: "0.12em",
              }}>
                {mode ? "READY — PRESS START" : "SELECT A SOURCE"}
              </span>
            </div>
          )}

          {/* HUD — top left live/standby */}
          <div style={{
            position: "absolute", top: 12, left: 14,
            display: "flex", alignItems: "center", gap: 5, zIndex: 10,
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: "50%",
              background: running ? "var(--green)" : "var(--dim)",
              animation: running ? "pulse-dot 1.4s ease infinite" : "none",
              transition: "background 0.3s",
            }} />
            <span style={{
              fontFamily: "var(--mono)", fontSize: 9,
              color: running ? "var(--green)" : "var(--dim)",
              letterSpacing: "0.12em",
            }}>
              {running ? "LIVE" : "STANDBY"}
            </span>
          </div>

          {/* HUD — bottom left frame counter */}
          {running && (
            <div style={{
              position: "absolute", bottom: 12, left: 14, zIndex: 10,
              display: "flex", gap: 6,
            }}>
              <span style={{
                fontFamily: "var(--mono)", fontSize: 10,
                color: "var(--muted)",
                background: "rgba(7,9,15,0.8)",
                border: "1px solid var(--border)",
                borderRadius: 4, padding: "3px 8px",
                backdropFilter: "blur(4px)",
              }}>
                {mode === "webcam" ? "📷" : "📡"} {mode === "webcam" ? "Webcam" : "CCTV"}
              </span>
            </div>
          )}

          {/* Subtle scanline overlay when live */}
          {running && (
            <div style={{
              position: "absolute", inset: 0, pointerEvents: "none", zIndex: 2,
              backgroundImage: "repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(255,255,255,0.007) 3px,rgba(255,255,255,0.007) 4px)",
            }} />
          )}
        </div>

        {mode && (
          <aside style={{
            width: fullscreen ? 360 : 300,
            maxWidth: "35vw",
            minWidth: 240,
            borderLeft: "1px solid var(--border)",
            background: "var(--surface)",
            padding: 14,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}>
            <img
              src={whCode}
              alt="Warehouse QR attendance code"
              style={{
                width: "100%",
                maxHeight: fullscreen ? 260 : 210,
                borderRadius: 8,
                border: "1px solid var(--border2)",
                objectFit: "contain",
                background: "#fff",
              }}
            />
            <button
              onClick={() => setIsWhExpanded(true)}
              style={{
                border: "1px solid var(--border)",
                background: "var(--bg)",
                color: "var(--text)",
                borderRadius: 6,
                padding: "7px 10px",
                cursor: "pointer",
                fontFamily: "var(--font)",
                fontSize: 12,
                fontWeight: 600,
                width: "fit-content",
              }}
            >
              ⛶ Maximize Image
            </button>
            <div>
              <p style={{
                fontSize: 10,
                color: "var(--muted)",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                fontFamily: "var(--mono)",
                marginBottom: 6,
              }}>
                Setup Instructions
              </p>
              <ol style={{
                margin: 0,
                paddingLeft: 18,
                color: "var(--text)",
                fontSize: 12,
                lineHeight: 1.5,
              }}>
                {ATTENDANCE_SETUP_STEPS.map((step) => (
                  <li key={step} style={{ marginBottom: 5 }}>{step}</li>
                ))}
              </ol>
            </div>
          </aside>
        )}
      </div>

      {isWhExpanded && (
        <div
          onClick={() => setIsWhExpanded(false)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1200,
            background: "rgba(6,8,12,0.92)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <button
            onClick={() => setIsWhExpanded(false)}
            style={{
              position: "absolute",
              top: 18,
              right: 18,
              border: "1px solid var(--border2)",
              background: "var(--surface)",
              color: "var(--text)",
              borderRadius: 8,
              padding: "7px 11px",
              cursor: "pointer",
              fontFamily: "var(--font)",
              fontSize: 12,
            }}
          >
            ✕ Close
          </button>
          <img
            src={whCode}
            alt="Warehouse QR attendance code expanded"
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: "min(96vw, 920px)",
              maxHeight: "90vh",
              width: "100%",
              objectFit: "contain",
              borderRadius: 12,
              border: "1px solid var(--border2)",
              background: "#fff",
              boxShadow: "0 24px 70px rgba(0,0,0,0.55)",
            }}
          />
        </div>
      )}
    </div>
  );
}