import React, { useRef, useState, useEffect } from "react";

export default function AttendanceViewer() {
  const videoRef = useRef(null);
  const imgRef = useRef(null);
  const wsRef = useRef(null);
  const [running, setRunning] = useState(false);
  const runningRef = useRef(false);
  
  const WS_URL = `ws://localhost:8000/ws/attendance?token=${sessionStorage.getItem("token")}`;

  const start = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  videoRef.current.srcObject = stream;
  await videoRef.current.play();

  wsRef.current = new WebSocket(WS_URL);
    setRunning(true);      // for UI
    runningRef.current = true;   // for loop
  wsRef.current.onopen = () => {
    console.log("WebSocket connected");


    captureLoop();
  };

  wsRef.current.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    if (data.image) {
      imgRef.current.src = `data:image/jpeg;base64,${data.image}`;
    }
     if (data.error) {
    stop()
    alert(data.error);   // "Token expired"
    ws.close();
  }
  };
};



 const stop = () => {
  setRunning(false);
  runningRef.current = false;

  wsRef.current?.close();

  if (videoRef.current?.srcObject) {
    videoRef.current.srcObject.getTracks().forEach(t => t.stop());
    videoRef.current.srcObject = null; // ⭐ important
  }

  if (imgRef.current) {
    imgRef.current.src =
      "https://placehold.co/640x480/222222/FFFFFF?text=Click+Start+to+Begin+Streaming";
  }

  console.log("Stopped & cleared UI");
};



 const captureLoop = async () => {
  const fps = 1;
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  while (runningRef.current) {   // <-- instant updated value
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise(r => canvas.toBlob(r, "image/jpeg", 0.7));
    const reader = new FileReader();

    reader.onloadend = () => {
      const base64data = reader.result.split(",")[1];
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ image: base64data }));
      }
    };

    reader.readAsDataURL(blob);
    await new Promise(r => setTimeout(r, 1000 / fps));
  }

  console.log("Capture loop stopped");
};

  useEffect(() => stop, []);
  useEffect(() => {
  if (imgRef.current) {
    imgRef.current.src =
      "https://placehold.co/640x480/222222/FFFFFF?text=Click+Start+to+Begin+Streaming";
  }
}, []);


  return (
    <div style={{ textAlign: "center" }}>
      <h2>Face Recognition Attendance</h2>
      <video ref={videoRef} style={{ display: "none" }} autoPlay muted />
      <img ref={imgRef} width="640" height="480" style={{ border: "1px solid black" }} />
      <div>
        <button onClick={start} disabled={running}>Start</button>
        <button onClick={stop} disabled={!running}>Stop</button>
      </div>
    </div>
  );
}
