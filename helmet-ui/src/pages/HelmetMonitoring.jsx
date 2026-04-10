import React, { useRef, useState, useEffect, useCallback } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8003";
const WS_BASE = "ws://localhost:8003";

// ── PiP Annotated Frame (top-right corner of feed) ────────────────────────────
function AnnotatedPiP({ src }) {
  const [expanded, setExpanded] = useState(false);

  if (!src) return null;

  return (
    <div
      onClick={() => setExpanded((p) => !p)}
      style={{
        position: "absolute",
        top: expanded ? "50%" : "12px",
        right: expanded ? "50%" : "12px",
        transform: expanded ? "translate(50%, -50%)" : "none",
        width: expanded ? "min(560px, 80%)" : "220px",
        border: expanded ? "2px solid #ff4444" : "1.5px solid #ff444488",
        borderRadius: "6px",
        background: "#000",
        boxShadow: expanded
          ? "0 0 40px rgba(255,68,68,0.4), 0 0 0 1px #222"
          : "0 0 18px rgba(255,68,68,0.2)",
        cursor: "pointer",
        zIndex: 20,
        overflow: "hidden",
        transition: "all 0.25s cubic-bezier(.4,0,.2,1)",
        flexShrink: 0,
      }}
    >
      <div style={{
        background: "#ff444422",
        borderBottom: "1px solid #ff444444",
        padding: "3px 8px",
        display: "flex",
        alignItems: "center",
        gap: "6px",
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: "50%",
          background: "#ff4444",
          boxShadow: "0 0 6px #ff4444",
          display: "inline-block",
          animation: "blink 1.4s ease-in-out infinite",
        }} />
        <span style={{ fontFamily: "monospace", fontSize: "0.6rem", color: "#ff8888", letterSpacing: "0.12em" }}>
          AI PROCESSED {expanded ? "— click to minimize" : "— click to expand"}
        </span>
      </div>
      <img
        src={src}
        alt="Annotated frame"
        style={{ display: "block", width: "100%", height: "auto", objectFit: "contain" }}
      />
    </div>
  );
}

// ── Violators Side Panel ──────────────────────────────────────────────────────
function ViolatorsPanel({ violators = [], stats }) {
  return (
    <div style={panel.wrap}>
      <div style={panel.header}>
        <span style={panel.headerDot} />
        <span style={panel.headerTitle}>VIOLATIONS</span>
        <span style={panel.headerCount}>{violators.length}</span>
      </div>

      {stats && (
        <div style={panel.statsRow}>
          <div style={panel.stat}>
            <span style={panel.statVal}>{stats.total_heads}</span>
            <span style={panel.statLabel}>Heads</span>
          </div>
          <div style={panel.statDivider} />
          <div style={panel.stat}>
            <span style={panel.statVal}>{stats.total_helmets}</span>
            <span style={panel.statLabel}>Helmets</span>
          </div>
          <div style={panel.statDivider} />
          <div style={panel.stat}>
            <span style={{
              ...panel.statVal,
              color: stats.helmet_violations > 0 ? "#ff4444" : "#44ff88",
              textShadow: stats.helmet_violations > 0 ? "0 0 12px #ff4444" : "0 0 12px #44ff88",
            }}>
              {stats.helmet_violations}
            </span>
            <span style={panel.statLabel}>Violations</span>
          </div>
        </div>
      )}

      <div style={panel.divider} />

      <div style={panel.list}>
        {violators.length === 0 ? (
          <div style={panel.empty}>
            <span style={panel.emptyIcon}>✓</span>
            <span style={panel.emptyText}>No violations detected</span>
          </div>
        ) : (
          violators.map((v, i) => (
            <div key={i} style={{
              ...panel.row,
              animation: "slideIn 0.3s ease forwards",
              animationDelay: `${i * 0.04}s`,
            }}>
              <span style={panel.rowIndex}>{String(i + 1).padStart(2, "0")}</span>
              <span style={panel.rowAlert}>⚠</span>
              <span style={panel.rowName}>{v.name}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ── Mode Selection Modal ──────────────────────────────────────────────────────
function ModeModal({ onSelect }) {
  const [rtspUrl, setRtspUrl] = useState("");
  const [screen, setScreen] = useState("pick");

  return (
    <div style={modal.overlay}>
      <style>{`
        @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
      <div style={modal.box}>
        <div style={modal.scanlines} />
        <div style={modal.header}>
          <span style={modal.icon}>⛑</span>
          <h2 style={modal.title}>Safety Monitoring</h2>
          <p style={modal.sub}>Select input source to begin</p>
        </div>

        {screen === "pick" && (
          <div style={modal.cards}>
            <button style={modal.card} onClick={() => onSelect({ mode: "webcam" })}>
              <span style={modal.cardIcon}>📷</span>
              <span style={modal.cardTitle}>Webcam</span>
              <span style={modal.cardDesc}>Use your device's built-in or USB camera</span>
              <span style={modal.cardArrow}>→</span>
            </button>
            <button style={modal.card} onClick={() => setScreen("cctv-input")}>
              <span style={modal.cardIcon}>📡</span>
              <span style={modal.cardTitle}>CCTV / IP Camera</span>
              <span style={modal.cardDesc}>Stream from an RTSP IP camera via backend</span>
              <span style={modal.cardArrow}>→</span>
            </button>
          </div>
        )}

        {screen === "cctv-input" && (
          <div style={modal.cctvForm}>
            <button style={modal.back} onClick={() => setScreen("pick")}>← Back</button>
            <label style={modal.label}>RTSP Stream URL</label>
            <input
              style={modal.input}
              type="text"
              placeholder="rtsp://user:pass@192.168.1.100:554/stream"
              value={rtspUrl}
              onChange={(e) => setRtspUrl(e.target.value)}
              autoFocus
            />
            <p style={modal.hint}>
              The backend will connect to this RTSP stream and forward annotated frames.
            </p>
            <button
              style={{ ...modal.submitBtn, ...(rtspUrl.trim() ? {} : modal.submitDisabled) }}
              disabled={!rtspUrl.trim()}
              onClick={() => onSelect({ mode: "cctv", rtspUrl: rtspUrl.trim() })}
            >
              Connect ▶
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function HelmetMonitoring({ cameraId = "camera-01" }) {
  const videoRef = useRef(null);
  const wsRef = useRef(null);
  const runningRef = useRef(false);
  const captureRunningRef = useRef(false);

  const [mode, setMode] = useState(null);
  const [rtspUrl, setRtspUrl] = useState("");
  const [running, setRunning] = useState(false);
  const [embeddingsLoaded, setEmbeddingsLoaded] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [violationData, setViolationData] = useState(null);
  const [showModal, setShowModal] = useState(true);
  const [annotatedSrc, setAnnotatedSrc] = useState(null);
  const [fullscreen, setFullscreen] = useState(false); // ← fullscreen toggle

  useEffect(() => {
    return () => { stopCapture(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── ESC key exits fullscreen ────────────────────────────────────────────────
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape" && fullscreen) setFullscreen(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [fullscreen]);

  const buildWsUrl = (selectedMode, selectedRtsp) => {
    const token = sessionStorage.getItem("token");
    const base = `${WS_BASE}/ws/helmet-monitoring/${cameraId}?token=${token}`;
    if (selectedMode === "cctv") return `${base}&rtsp_url=${encodeURIComponent(selectedRtsp)}`;
    return base;
  };

  const stopCapture = useCallback(() => {
    runningRef.current = false;
    captureRunningRef.current = false;
    wsRef.current?.close();
    wsRef.current = null;
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    setRunning(false);
    setViolationData(null);
    setAnnotatedSrc(null);
  }, []);

  const captureLoop = useCallback(async () => {
    if (captureRunningRef.current) return;
    captureRunningRef.current = true;
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    try {
      while (runningRef.current) {
        const video = videoRef.current;
        const ws = wsRef.current;
        if (!video || video.videoWidth === 0 || !ws || ws.readyState !== WebSocket.OPEN) {
          await new Promise((r) => setTimeout(r, 200));
          continue;
        }
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const base64 = canvas.toDataURL("image/jpeg", 0.7).split(",")[1];
        if (runningRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ image: base64 }));
        }
        await new Promise((r) => setTimeout(r, 1000));
      }
    } catch (err) {
      console.error("Capture loop error:", err);
    } finally {
      captureRunningRef.current = false;
    }
  }, []);

  const handleModeSelect = ({ mode: selectedMode, rtspUrl: selectedRtsp = "" }) => {
    setMode(selectedMode);
    setRtspUrl(selectedRtsp);
    setShowModal(false);
    setStatusMessage(`Mode: ${selectedMode === "webcam" ? "Webcam" : "CCTV — " + selectedRtsp}`);
  };

  const switchMode = () => {
    stopCapture();
    setMode(null);
    setRtspUrl("");
    setEmbeddingsLoaded(false);
    setStatusMessage("");
    setShowModal(true);
  };

  const start = async () => {
    if (mode === "webcam") {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      } catch {
        setStatusMessage("Camera access denied or unavailable.");
        return;
      }
    }

    const ws = new WebSocket(buildWsUrl(mode, rtspUrl));
    wsRef.current = ws;
    runningRef.current = true;
    setRunning(true);
    setStatusMessage("Connecting…");

    ws.onopen = () => {
      setStatusMessage(`Connected — ${mode === "cctv" ? "CCTV" : "Webcam"} monitoring active.`);
      if (mode === "webcam") captureLoop();
    };

    ws.onmessage = (msg) => {
      let data;
      try { data = JSON.parse(msg.data); }
      catch { console.warn("Non-JSON WS message:", msg.data); return; }

      if (data.error) {
        setStatusMessage(`Server error: ${data.error}`);
        stopCapture();
        return;
      }
      if (data.image)       setAnnotatedSrc(`data:image/jpeg;base64,${data.image}`);
      if (data.helmet_data) setViolationData(data.helmet_data);
    };

    ws.onclose = () => { setStatusMessage("Connection closed."); stopCapture(); };
    ws.onerror = (e) => {
      console.error("WebSocket error", e);
      setStatusMessage("WebSocket error — server may be unavailable.");
      stopCapture();
    };
  };

  const reload = async () => {
    const token = sessionStorage.getItem("token");
    setStatusMessage("Loading embeddings…");
    try {
      const res = await axios.post(
        `${API_BASE}/helmet-monitoring/reload_index`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setStatusMessage(res.data.message ?? "Embeddings loaded.");
      setEmbeddingsLoaded(true);
    } catch (err) {
      const detail = err.response?.data?.detail ?? err.response?.data?.message ?? err.message ?? "Unknown error";
      const status = err.response?.status;
      if (status === 401)      setStatusMessage("Unauthorized — please log in again.");
      else if (status === 403) setStatusMessage("Forbidden — SUPERVISOR role required.");
      else                     setStatusMessage(`Failed to load embeddings: ${detail}`);
      setEmbeddingsLoaded(false);
    }
  };

  // ── Container style switches between normal and fullscreen ──────────────────
  const containerStyle = fullscreen
    ? { ...styles.container, position: "fixed", inset: 0, zIndex: 999, height: "100vh" }
    : { ...styles.container };

  return (
    <div style={containerStyle}>
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; box-shadow: 0 0 6px #ff4444; }
          50% { opacity: 0.3; box-shadow: none; }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(12px); }
          to   { opacity: 1; transform: translateX(0); }
        }
        .feed-video::-webkit-media-controls { display: none !important; }
        .feed-video { object-fit: cover; }
      `}</style>

      {showModal && <ModeModal onSelect={handleModeSelect} />}

      {/* ── Title bar ── */}
      <div style={styles.titleBar}>
        <div style={styles.titleLeft}>
          <span style={styles.titleDot} />
          <span style={styles.titleText}>⛑ SAFETY MONITOR</span>
          <span style={styles.titleCam}>{cameraId}</span>
        </div>

        <div style={styles.titleRight}>
          {mode && (
            <>
              <span style={styles.modeBadge}>
                {mode === "webcam" ? "📷 Webcam" : "📡 CCTV"}
              </span>
              {mode === "cctv" && (
                <span style={styles.rtspTag} title={rtspUrl}>{rtspUrl}</span>
              )}
              <button
                style={{ ...styles.btn, ...styles.btnGhost }}
                onClick={switchMode}
                disabled={running}
              >
                ⇄ Switch
              </button>
            </>
          )}

          {/* ── Fullscreen toggle button ── */}
          <button
            onClick={() => setFullscreen(p => !p)}
            title={fullscreen ? "Exit fullscreen (Esc)" : "Enter fullscreen"}
            style={{
              ...styles.btn,
              ...styles.btnGhost,
              padding: "0.3rem 0.6rem",
              fontSize: "1rem",
              lineHeight: 1,
              color: fullscreen ? "#f59e0b" : "#555",
              borderColor: fullscreen ? "#f59e0b55" : "#2a2a2a",
              background: fullscreen ? "rgba(245,158,11,0.08)" : "transparent",
            }}
          >
            {fullscreen ? "⊠" : "⛶"}
          </button>
        </div>
      </div>

      {/* ── Feed + panel ── */}
      <div style={{
        ...styles.feedRow,
        height: fullscreen ? "calc(100vh - 110px)" : "calc(100vh - 150px)",
      }}>
        {/* Camera feed area */}
        <div style={styles.feedWrap}>
          {mode === "webcam" ? (
            <video
              ref={videoRef}
              className="feed-video"
              autoPlay muted playsInline
              style={styles.liveVideo}
            />
          ) : (
            <div style={styles.cctvPlaceholder}>
              {!running && (
                <span style={styles.placeholderText}>
                  CCTV frames will appear once connected
                </span>
              )}
              {annotatedSrc && (
                <img
                  src={annotatedSrc}
                  alt="CCTV annotated feed"
                  style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
                />
              )}
            </div>
          )}

          {mode === "webcam" && <AnnotatedPiP src={annotatedSrc} />}

          {running && <div style={styles.scanOverlay} />}

          {/* HUD top-left */}
          <div style={styles.hudTL}>
            <span style={{ ...styles.hudDot, background: running ? "#44ff88" : "#555" }} />
            <span style={styles.hudLabel}>{running ? "LIVE" : "STANDBY"}</span>
          </div>

          {/* HUD bottom-left stats */}
          {violationData && (
            <div style={styles.hudBL}>
              <span style={styles.hudStat}>👁 {violationData.total_heads} heads</span>
              <span style={styles.hudStat}>⛑ {violationData.total_helmets} helmets</span>
              {violationData.helmet_violations > 0 && (
                <span style={{ ...styles.hudStat, color: "#ff4444" }}>
                  ⚠ {violationData.helmet_violations} violations
                </span>
              )}
            </div>
          )}
        </div>

        <ViolatorsPanel
          violators={violationData?.violators ?? []}
          stats={violationData}
        />
      </div>

      {/* ── Status + controls ── */}
      {statusMessage && <p style={styles.status}>{statusMessage}</p>}

      <div style={styles.controls}>
        <button
          onClick={start}
          disabled={running || !embeddingsLoaded || !mode}
          style={{ ...styles.btn, ...(running || !embeddingsLoaded || !mode ? styles.btnDisabled : styles.btnGreen) }}
        >
          ▶ Start
        </button>
        <button
          onClick={stopCapture}
          disabled={!running}
          style={{ ...styles.btn, ...(!running ? styles.btnDisabled : styles.btnRed) }}
        >
          ■ Stop
        </button>
        <button
          onClick={reload}
          disabled={running || !mode}
          style={{ ...styles.btn, ...(running || !mode ? styles.btnDisabled : styles.btnBlue) }}
        >
          {embeddingsLoaded ? "↺ Reload Index" : "⬇ Load Embeddings"}
        </button>
      </div>
    </div>
  );
}

// ── Panel Styles ──────────────────────────────────────────────────────────────
const panel = {
  wrap: {
    width: "280px",
    background: "#0d0d0d",
    border: "1px solid #1e1e1e",
    borderLeft: "none",
    display: "flex",
    flexDirection: "column",
    fontFamily: "monospace",
    flexShrink: 0,
  },
  header: {
    display: "flex", alignItems: "center", gap: "0.5rem",
    padding: "0.75rem 0.9rem",
    borderBottom: "1px solid #1a1a1a",
  },
  headerDot: {
    width: "7px", height: "7px", borderRadius: "50%",
    background: "#ff4444", boxShadow: "0 0 6px #ff2222", flexShrink: 0,
    animation: "blink 1.4s ease-in-out infinite",
  },
  headerTitle: { fontSize: "0.68rem", color: "#555", letterSpacing: "0.15em", flex: 1 },
  headerCount: { fontSize: "0.78rem", color: "#ff4444", fontWeight: 700 },
  statsRow: {
    display: "flex", justifyContent: "space-around", alignItems: "center",
    padding: "0.6rem 0.5rem", borderBottom: "1px solid #1a1a1a",
  },
  stat: { display: "flex", flexDirection: "column", alignItems: "center", gap: "2px" },
  statVal: { fontSize: "1rem", fontWeight: 700, color: "#e0e0e0" },
  statLabel: { fontSize: "0.6rem", color: "#444", letterSpacing: "0.08em" },
  statDivider: { width: "1px", height: "28px", background: "#1e1e1e" },
  divider: { height: "1px", background: "#141414" },
  list: { flex: 1, overflowY: "auto", padding: "0.5rem 0" },
  empty: {
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", padding: "2rem 1rem", gap: "0.4rem",
  },
  emptyIcon: { fontSize: "1.4rem", color: "#1a4a2a" },
  emptyText: { fontSize: "0.7rem", color: "#333", textAlign: "center" },
  row: {
    display: "flex", alignItems: "center", gap: "0.5rem",
    padding: "0.45rem 0.9rem", borderBottom: "1px solid #111",
  },
  rowIndex: { fontSize: "0.65rem", color: "#333", minWidth: "18px" },
  rowAlert: { fontSize: "0.75rem", color: "#ff4444" },
  rowName: { fontSize: "0.78rem", color: "#cc8888", flex: 1, wordBreak: "break-word" },
};

// ── Modal Styles ──────────────────────────────────────────────────────────────
const modal = {
  overlay: {
    position: "fixed", inset: 0, zIndex: 1000,
    background: "rgba(0,0,0,0.88)", backdropFilter: "blur(6px)",
    display: "flex", alignItems: "center", justifyContent: "center",
  },
  box: {
    position: "relative", background: "#0f0f0f",
    border: "1px solid #2a2a2a", borderRadius: "12px",
    padding: "2.5rem 2rem", width: "min(480px, 92vw)",
    boxShadow: "0 0 60px rgba(0,0,0,0.8), 0 0 0 1px #1a1a1a", overflow: "hidden",
  },
  scanlines: {
    position: "absolute", inset: 0, pointerEvents: "none",
    backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px)",
    borderRadius: "12px",
  },
  header: { textAlign: "center", marginBottom: "2rem" },
  icon: { fontSize: "2.5rem", display: "block", marginBottom: "0.5rem" },
  title: {
    margin: 0, fontSize: "1.3rem", fontFamily: "monospace",
    letterSpacing: "0.12em", color: "#ffffff", fontWeight: 700,
  },
  sub: { margin: "0.4rem 0 0", color: "#555", fontSize: "0.8rem", fontFamily: "monospace" },
  cards: { display: "flex", flexDirection: "column", gap: "0.75rem" },
  card: {
    display: "grid", gridTemplateColumns: "2.5rem 1fr auto",
    gridTemplateRows: "auto auto", alignItems: "center", gap: "0 0.75rem",
    background: "#141414", border: "1px solid #222", borderRadius: "8px",
    padding: "1rem 1.2rem", cursor: "pointer", textAlign: "left",
    color: "#e0e0e0", fontFamily: "monospace",
  },
  cardIcon: { fontSize: "1.5rem", gridRow: "1 / 3" },
  cardTitle: { fontWeight: 700, fontSize: "0.95rem", color: "#fff" },
  cardDesc: { fontSize: "0.75rem", color: "#555", gridColumn: "2" },
  cardArrow: { fontSize: "1.2rem", color: "#444", gridRow: "1 / 3" },
  cctvForm: { display: "flex", flexDirection: "column", gap: "0.75rem" },
  back: {
    background: "none", border: "none", color: "#555", cursor: "pointer",
    fontFamily: "monospace", fontSize: "0.8rem", alignSelf: "flex-start", padding: 0,
  },
  label: { color: "#888", fontSize: "0.8rem", fontFamily: "monospace" },
  input: {
    background: "#0a0a0a", border: "1px solid #2a2a2a", borderRadius: "6px",
    color: "#e0e0e0", fontFamily: "monospace", fontSize: "0.85rem",
    padding: "0.65rem 0.9rem", outline: "none",
  },
  hint: { color: "#444", fontSize: "0.75rem", fontFamily: "monospace", margin: 0 },
  submitBtn: {
    background: "#1a4a2a", color: "#fff", border: "none", borderRadius: "6px",
    padding: "0.65rem", fontFamily: "monospace", fontWeight: 700,
    fontSize: "0.9rem", cursor: "pointer",
  },
  submitDisabled: { background: "#1a1a1a", color: "#333", cursor: "not-allowed" },
};

// ── Component Styles ──────────────────────────────────────────────────────────
const styles = {
  container: {
    fontFamily: "monospace",
    padding: "0.75rem 1rem",
    background: "#0a0a0a",
    color: "#e0e0e0",
    boxSizing: "border-box",
    display: "flex",
    flexDirection: "column",
    minHeight: "100%",
  },
  titleBar: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem",
  },
  titleLeft: { display: "flex", alignItems: "center", gap: "0.5rem" },
  titleDot: {
    width: 8, height: 8, borderRadius: "50%",
    background: "#ff4444", boxShadow: "0 0 8px #ff4444",
    animation: "blink 1.4s ease-in-out infinite",
  },
  titleText: { fontSize: "1.1rem", letterSpacing: "0.12em", color: "#fff", fontWeight: 700 },
  titleCam: {
    fontSize: "0.72rem", color: "#444", background: "#111",
    border: "1px solid #222", borderRadius: "3px", padding: "1px 6px",
  },
  titleRight: { display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" },
  modeBadge: {
    background: "#1a1a1a", border: "1px solid #2a2a2a",
    borderRadius: "4px", padding: "0.2rem 0.6rem",
    fontSize: "0.78rem", color: "#aaa",
  },
  rtspTag: {
    background: "#0a0a0a", border: "1px solid #222",
    borderRadius: "4px", padding: "0.2rem 0.6rem",
    fontSize: "0.72rem", color: "#555",
    maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
  },
  feedRow: {
    display: "flex",
    alignItems: "stretch",
    width: "100%",
    flex: 1,
    minHeight: 0,
    border: "1px solid #1e1e1e",
    boxSizing: "border-box",
  },
  feedWrap: {
    position: "relative",
    flex: 1,
    background: "#050505",
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  liveVideo: {
    position: "absolute", inset: 0,
    width: "100%", height: "100%",
    objectFit: "cover", display: "block",
    background: "#000",
  },
  cctvPlaceholder: {
    position: "absolute", inset: 0,
    display: "flex", alignItems: "center", justifyContent: "center",
    background: "#050505",
  },
  placeholderText: {
    color: "#2a2a2a", fontSize: "0.8rem",
    fontFamily: "monospace", letterSpacing: "0.08em",
  },
  scanOverlay: {
    position: "absolute", inset: 0, pointerEvents: "none", zIndex: 5,
    backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,255,100,0.012) 3px, rgba(0,255,100,0.012) 4px)",
  },
  hudTL: {
    position: "absolute", top: 10, left: 12, zIndex: 10,
    display: "flex", alignItems: "center", gap: "5px",
  },
  hudDot: { width: 7, height: 7, borderRadius: "50%", transition: "background 0.3s" },
  hudLabel: { fontFamily: "monospace", fontSize: "0.62rem", letterSpacing: "0.15em", color: "#555" },
  hudBL: {
    position: "absolute", bottom: 10, left: 12, zIndex: 10,
    display: "flex", flexDirection: "column", gap: "3px",
  },
  hudStat: {
    fontFamily: "monospace", fontSize: "0.65rem",
    color: "#888", background: "rgba(0,0,0,0.6)",
    padding: "2px 6px", borderRadius: "3px", letterSpacing: "0.06em",
  },
  status: {
    color: "#555", fontSize: "0.82rem",
    margin: "0.5rem 0", minHeight: "1.2em", textAlign: "center",
  },
  controls: {
    display: "flex", justifyContent: "center",
    gap: "0.75rem", marginTop: "0.75rem", flexWrap: "wrap",
  },
  btn: {
    padding: "0.5rem 1.2rem", border: "none", borderRadius: "4px",
    cursor: "pointer", fontFamily: "monospace", fontWeight: "bold",
    fontSize: "0.9rem", transition: "opacity 0.15s",
  },
  btnGreen:    { background: "#1a7a3a", color: "#fff" },
  btnRed:      { background: "#7a1a1a", color: "#fff" },
  btnBlue:     { background: "#1a3a7a", color: "#fff" },
  btnGhost:    { background: "transparent", border: "1px solid #2a2a2a", color: "#555", fontSize: "0.8rem" },
  btnDisabled: { background: "#151515", color: "#333", cursor: "not-allowed" },
};