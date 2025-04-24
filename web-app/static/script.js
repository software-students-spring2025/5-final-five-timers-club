const video = document.querySelector("#video");
const startBtn = document.querySelector("#startBtn");
const stopBtn = document.querySelector("#stopBtn");
const container = document.querySelector(".home-container");
const resultBox = document.querySelector("#result-box");
const modal = document.getElementById("playlist-modal");
const iframe = document.getElementById("playlist-iframe");
const closeBtn = document.getElementById("modal-close");

let captureInterval;
let lastImage = null;

//const resultDisplay = document.querySelector("#result-box");
//const box = document.querySelector(".result")

//start webcam + capture every 5s
startBtn.addEventListener("click", () => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        video.srcObject = stream;
        video.play();
        container.style.display = "flex";
        captureInterval = setInterval(() => captureAndSendImage(video), 5000);
      })
      .catch(console.error);
});

// end webcam
stopBtn.addEventListener("click", () => {
    //const video = document.querySelector('video');
    //const mediaStream = video.srcObject;
    let tracks = video.srcObject?.getTracks() || [];
    tracks.forEach(t => t.stop());
    //tracks.forEach(track => track.stop())
    clearInterval(captureInterval);

    /*if (captureInterval) {
        clearInterval(captureInterval);
        captureInterval = null;
    }*/

});

// 
// core capture happens here + emotion display + "this song" link
function captureAndSendImage(videoElem) {
    if (!videoElem.videoWidth) return;
  
    const canvas = document.createElement("canvas");
    canvas.width  = videoElem.videoWidth;
    canvas.height = videoElem.videoHeight;
    canvas.getContext("2d").drawImage(videoElem, 0, 0);
  
    lastImage = canvas.toDataURL("image/jpeg");
  
    fetch("/submit-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: lastImage })
    })
    .then(r => r.json())
    .then(data => {
      if (data.emotion && data.emoji) {
        resultBox.innerHTML = `
          You seem ${data.emoji} <strong>${data.emotion}</strong>,
          we recommend <a id="playlist-link">this song</a>.
        `;
        document
          .getElementById("playlist-link")
          .addEventListener("click", onPlaylistClick);
      } else {
        resultBox.textContent = "Could not detect emotion 😕";
      }
    })
    .catch(err => {
      console.error(err);
      resultBox.textContent = "Error detecting emotion 😕";
    });
}

// When user clicks “this song”
async function onPlaylistClick(e) {
    e.preventDefault();
    try {
      const resp = await fetch("/get-playlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: lastImage })
      });
      const pl = await resp.json();
      if (pl.playlist_uri) {
        // spotify:playlist:ID  →  ID
        const id = pl.playlist_uri.split(":").pop();
        iframe.src = `https://open.spotify.com/embed/playlist/${id}`;
        modal.classList.remove("hidden");
      } else {
        alert("No playlist found for that mood.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to load playlist.");
    }
  }
  
  // Close button on the modal
  closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
    iframe.src = "";
});


// send image to deepface server and update our site
async function sendImageToServer(base64Image) {
    const response = await fetch("/submit-video", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ image: base64Image })
    });
  
    const data = await response.json();
    console.log("Detected Emotion:", data.emotion, "Emoji:", data.emoji);
  
    // Update the emoji in the DOM
    const resultDisplay = document.getElementById("result-box");
    if (resultDisplay) {
        resultDisplay.textContent = data.emoji;
    }
}
