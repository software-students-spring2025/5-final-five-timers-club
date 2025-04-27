const ML_BASE = 'http://localhost:6001';

const video     = document.querySelector("#video");
const startBtn  = document.querySelector("#startBtn");
const stopBtn   = document.querySelector("#stopBtn");
const resultBox = document.querySelector("#result-box");
const playerEl  = document.querySelector("#player");

let captureInterval;
let firstEmotion;

startBtn.addEventListener("click", () => {
  firstEmotion = true;
  resultBox.innerHTML = "";
  playerEl.innerHTML   = "";

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      video.play();
      captureInterval = setInterval(() => captureAndSendImage(video), 5000);
    })
    .catch(err => console.error("Camera error:", err));
});

stopBtn.addEventListener("click", () => {
  if (video.srcObject) video.srcObject.getTracks().forEach(t => t.stop());
  clearInterval(captureInterval);
});

async function captureAndSendImage(videoEl) {
  if (!videoEl.videoWidth) return;

  // grabbing frame
  const canvas = document.createElement("canvas");
  canvas.width  = videoEl.videoWidth;
  canvas.height = videoEl.videoHeight;
  canvas.getContext("2d").drawImage(videoEl, 0, 0);
  const imgBase64 = canvas.toDataURL("image/jpeg");

  try {
    // sending web-app to detect emotion + emoji
    const res  = await fetch("/submit-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imgBase64 })
    });
    const data = await res.json();

    if (!data.emotion || !data.emoji) {
      resultBox.textContent = "Could not detect emotion 😕";
      return;
    }

    // showing detected emoji + text
    resultBox.innerHTML = `
      <span style="font-size:8rem">${data.emoji}</span>
      <p>Detected: ${data.emotion}</p>
    `;

    // on the very first time stop polling and fetch playlist!
    if (firstEmotion) {
      firstEmotion = false;
      clearInterval(captureInterval);

      // getting a client-credentials token for Web Playback SDK
      const tkRes = await fetch(`${ML_BASE}/token`);
      const { token } = await tkRes.json();

      // getting the playlist URI for this emotion
      const plRes = await fetch(`${ML_BASE}/playlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imgBase64 })
      });

      // checking for HTTP errors first!
      if (!plRes.ok) {
        console.error("❌ /playlist failed:", plRes.status, await plRes.json());
        return;
      }

      // now safely parsing and pulling out playlist_uri
      const plData      = await plRes.json();
      const playlist_uri = plData.playlist_uri;
      if (!playlist_uri) {
        console.warn("⚠️ no playlist_uri in /playlist response", plData);
        return;
      }

      // “open.spotify.com/embed” fallback
      const embedUri = playlist_uri
        .replace(/:/g, "/")
        .replace(/^spotify/, "open.spotify.com/embed");
      playerEl.innerHTML = `
        <iframe
          src="https://${embedUri}"
          width="300" height="380" frameborder="0"
          allow="encrypted-media">
        </iframe>`;

      // initializing the Web Playback SDK to actually playyyyy
      const initPlayer = () => {
        const player = new Spotify.Player({
          name: "Emotion DJ",
          getOAuthToken: cb => cb(token)
        });
        player.connect().then(_ => {
          player._options.getOAuthToken(access_token => {
            fetch("https://api.spotify.com/v1/me/player/play", {
              method: "PUT",
              headers: {
                "Authorization": `Bearer ${access_token}`,
                "Content-Type":   "application/json"
              },
              body: JSON.stringify({ context_uri: playlist_uri })
            });
          });
        });
      };

      if (window.Spotify && Spotify.Player) {
        initPlayer();
      } else {
        const tag = document.createElement("script");
        tag.src   = "https://sdk.scdn.co/spotify-player.js";
        tag.onload = initPlayer;
        document.head.appendChild(tag);
      }
    }

  } catch (err) {
    console.error("Error in captureAndSendImage:", err);
    resultBox.textContent = "Error detecting emotion 😕";
  }
}



