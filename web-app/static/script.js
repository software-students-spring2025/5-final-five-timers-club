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

  // Grabbing frame from the video element
  const canvas = document.createElement("canvas");
  canvas.width  = videoEl.videoWidth;
  canvas.height = videoEl.videoHeight;
  canvas.getContext("2d").drawImage(videoEl, 0, 0);
  const imgBase64 = canvas.toDataURL("image/jpeg");

  try {
    // Sending the image for emotion and emoji detection
    const res = await fetch("/submit-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imgBase64 })
    });
    const data = await res.json();

    if (!data.emotion || !data.emoji) {
      resultBox.textContent = "Could not detect emotion 😕";
      return;
    }

    // Displaying the detected emoji and emotion
    resultBox.innerHTML = `
      <span style="font-size:8rem">${data.emoji}</span>
      <p>Detected: ${data.emotion}</p>
    `;

    // On the very first time, stop polling and fetch the playlist
    if (firstEmotion) {
      firstEmotion = false;
      clearInterval(captureInterval);

      // Getting a client-credentials token for Web Playback SDK
      const tkRes = await fetch(`${ML_BASE}/token`);
      const { token } = await tkRes.json();

      console.log("Spotify Token:", token); // debug

      // Getting the playlist URI for this emotion
      const plRes = await fetch(`${ML_BASE}/playlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imgBase64 })
      });

      // Checking for HTTP errors first!
      if (!plRes.ok) {
        console.error("❌ /playlist failed:", plRes.status, await plRes.json());
        return;
      }

      // Safely parsing and pulling out playlist_uri
      const plData = await plRes.json();
      console.log("Playlist Data:", plData);
      if (!plData.song || !plData.song.uri) {
        console.warn("⚠️ No playlist_uri in /playlist response", plData);
        return;
      }

      const playlist_uri = plData.song.uri;
      console.log("Song URI:", playlist_uri);

      // Generating the embed URL for the playlist
      const embedUri = playlist_uri
        .replace(/:/g, "/")
        .replace(/^spotify/, "open.spotify.com/embed");
      console.log("Embed URI:", embedUri);
      playerEl.innerHTML = `
        <iframe
          src="https://${embedUri}"
          width="300" height="380" frameborder="0"
          allow="encrypted-media">
        </iframe>`;

      // Initializing the Web Playback SDK to actually play the playlist
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

      // Loading the Spotify Web Playback SDK script if not already loaded
      if (window.Spotify && Spotify.Player) {
        initPlayer();
      } else {
        const tag = document.createElement("script");
        tag.src   = "https://sdk.scdn.co/spotify-player.js";
        tag.onload = () => {
          console.log("Spotify Player SDK loaded");  // Debugging SDK load
          initPlayer();
        };
        document.head.appendChild(tag);
      }
    }

  } catch (err) {
    console.error("Error in captureAndSendImage:", err);
    resultBox.textContent = "Error detecting emotion 😕";
  }
}
