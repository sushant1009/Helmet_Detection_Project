import React, { useRef, useState, useEffect } from "react";
import axios from "axios";

export default function HelmetMonitoring() {
  const videoRef = useRef(null);
  const imgRef = useRef(null);
  const wsRef = useRef(null);
  const [running, setRunning] = useState(false);
  const runningRef = useRef(false);
  const captureRunningRef = useRef(false);
  const[embeddingsLoaded, setembeddingsLoaded] = useState(false)

  useEffect(() => {
  return () => {
    stop(); 
  };
}, []);

  const WS_URL = `ws://localhost:8003/ws/helmet-monitoring?token=${sessionStorage.getItem("token")}`;
  const start = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  videoRef.current.srcObject = stream;
  await videoRef.current.play();

  wsRef.current = new WebSocket(WS_URL);
    setRunning(true);      
    runningRef.current = true;  
 wsRef.current.onopen = () => {
  captureLoop(); 
};
wsRef.current.onclose = () => {
  stopCapture();
  alert("Connection closed !!!");
};

wsRef.current.onerror = (e) => {
  console.error("WebSocket error", e);
  stopCapture();
  alert("Server Unavailable")
};


  wsRef.current.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    if (data.image) {
      imgRef.current.src = `data:image/jpeg;base64,${data.image}`;
    }
    if (data.error) {
        alert("WS Error: " + data.error);
        ws.close();
    }
  };
};



 const stopCapture = () => {
  setRunning(false);
  runningRef.current = false;

  wsRef.current?.close();

  if (videoRef.current?.srcObject) {
    videoRef.current.srcObject.getTracks().forEach(t => t.stop());
    videoRef.current.srcObject = null; 
  }

  if (imgRef.current) {
    imgRef.current.src =
      "https://placehold.co/640x480/222222/FFFFFF?text=Click+Start+to+Begin+Streaming";
  }

};



 const captureLoop = async () => {
  if (captureRunningRef.current) return; 
  captureRunningRef.current = true;

  const fps = 1;
  const interval = 1000 / fps;

  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  try {
    while (runningRef.current) {
      const video = videoRef.current;
      const ws = wsRef.current;

      if (
        !video ||
        video.videoWidth === 0 ||
        !ws ||
        ws.readyState !== WebSocket.OPEN
      ) {
        await new Promise(r => setTimeout(r, 200));
        continue;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

     
      const dataURL = canvas.toDataURL("image/jpeg", 0.7);
      const base64 = dataURL.split(",")[1];

      // Final guard before send
      if (
        runningRef.current &&
        wsRef.current &&
        wsRef.current.readyState === WebSocket.OPEN
      ) {
        ws.send(JSON.stringify({ image: base64 }));
      }

      await new Promise(r => setTimeout(r, interval));
    }
  } catch (err) {
    console.error("Capture loop error:", err);
  } finally {
    captureRunningRef.current = false;
   
  }
};

const reload = async() =>{
 const token = sessionStorage.getItem("token");
try{
  
const res = await axios.post(
  "http://localhost:8003/helmet-monitoring/reload_index",
  {}, 
  {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
 

);
console.log(res.data)
if(res.data.status_code == 401)
{
  alert(res.data.detail)
}else if(res.data.status_code == 403)
{
  alert(res.data.detail)
}
alert(res.data.message)
setembeddingsLoaded(true)
}catch(err){

}
 
}


  return (
    <div style={{ textAlign: "center" }}>
      <h2>Safety First</h2>
      <video ref={videoRef} style={{ display: "none" }} autoPlay muted />
      <img ref={imgRef} width="640" height="480" style={{ border: "1px solid black" }} />
      <div>
        <button onClick={start} disabled={running || !embeddingsLoaded}>Start</button>
        <button onClick={stopCapture} disabled={!running}>Stop</button>
      </div>
      <button onClick={reload} >{embeddingsLoaded?"Reload Index":"Load Embbedings"}</button>
    </div>
  );
}
