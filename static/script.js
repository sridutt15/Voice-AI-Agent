document.addEventListener("DOMContentLoaded", async () => {
  // --- STATE AND ELEMENTS ---
  let appState = "idle"; // idle, recording, processing
  let mediaRecorder = null;
  let recordedChunks = [];
  let sessionId = null;

  const recordBtn = document.getElementById("recordBtn");
  const statusDisplay = document.getElementById("statusDisplay");
  const audioPlayer = document.getElementById("audioPlayer");
  const transcriptContainer = document.getElementById("transcriptContainer");
  const transcriptToggleBtn = document.getElementById("transcriptToggleBtn");

  const ICONS = {
    // FIXED: SVG and spinner div must be enclosed in backticks to be valid strings.
    mic: `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-mic-fill" viewBox="0 0 16 16"><path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0V3z"/><path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/></svg>`,
    spinner: `<div class="loader"></div>` // Using the custom loader class
  };

  // --- SESSION MANAGEMENT ---
  const urlParams = new URLSearchParams(window.location.search);
  sessionId = urlParams.get('session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    // FIXED: The template literal for the URL needs to be in backticks.
    window.history.replaceState({}, '', `?session_id=${sessionId}`);
  }

  // --- UI UPDATE LOGIC ---
  const updateUI = (newState) => {
    appState = newState;
    switch (appState) {
      case "idle":
        recordBtn.disabled = false;
        recordBtn.classList.remove("recording");
        recordBtn.innerHTML = ICONS.mic;
        statusDisplay.textContent = "Tap the icon to speak.";
        break;
      case "recording":
        recordBtn.disabled = false;
        recordBtn.classList.add("recording");
        recordBtn.innerHTML = ICONS.mic;
        statusDisplay.textContent = "Recording... Tap again to stop.";
        recordedChunks = [];
        break;
      case "processing":
        recordBtn.disabled = true;
        recordBtn.classList.remove("recording");
        recordBtn.innerHTML = ICONS.spinner;
        statusDisplay.textContent = "Thinking...";
        break;
      case "error":
        recordBtn.disabled = false;
        recordBtn.classList.remove("recording");
        recordBtn.innerHTML = ICONS.mic;
        break;
    }
  };

  // --- Function to add messages to the transcript ---
  const addMessageToTranscript = (sender, text) => {
    if (!text || text.trim() === "") return;

    const entry = document.createElement("div");
    entry.classList.add("transcript-entry");

    const senderElem = document.createElement("strong");
    // FIXED: The template literal for the sender text needs to be in backticks.
    senderElem.textContent = `${sender}:`;

    const textNode = document.createTextNode(` ${text}`);

    entry.appendChild(senderElem);
    entry.appendChild(textNode);
    transcriptContainer.appendChild(entry);
    transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
  };

  // --- CORE FUNCTIONS ---
  const startRecording = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      statusDisplay.textContent = "Audio recording is not supported.";
      updateUI("error");
      return;
    }
    updateUI("recording");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunks.push(event.data);
      };
      mediaRecorder.onstop = handleStopRecording;
      mediaRecorder.start();
    } catch (err) {
      console.error("Error accessing microphone:", err);
      statusDisplay.textContent = "Please enable microphone permissions.";
      updateUI("error");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
  };

  const handleStopRecording = async () => {
    updateUI("processing");
    const audioBlob = new Blob(recordedChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "user_recording.webm");

    try {
      const response = await fetch(`/agent/chat/${sessionId}`, {
        method: "POST",
        body: formData,
      });

      if (response.headers.get("X-Error") === "true") {
        statusDisplay.textContent = "Sorry, an error occurred on my end.";
        const fallbackBlob = await response.blob();
        audioPlayer.src = URL.createObjectURL(fallbackBlob);
        audioPlayer.play();
        updateUI("error"); // Better to set state to error here
        return;
      }

      // FIXED: The template literal for the error message needs to be in backticks.
      if (!response.ok) throw new Error(`Server error: ${response.statusText}`);

      const result = await response.json();
      if (result.audio_url) {
        statusDisplay.textContent = "Here's my response...";

        addMessageToTranscript("You", result.user_text);
        addMessageToTranscript("Agent", result.agent_text);

        audioPlayer.src = result.audio_url;
        audioPlayer.play();
      } else {
        throw new Error("API response did not contain an audio URL.");
      }
    } catch (error) {
      console.error("Error in conversation chain:", error);
      statusDisplay.textContent = "An error occurred. Please try again.";
      updateUI("error");
    }
  };

  // --- EVENT LISTENERS ---
  recordBtn.addEventListener("click", () => {
    if (appState === "idle" || appState === "error") {
      startRecording();
    } else if (appState === "recording") {
      stopRecording();
    }
  });

  audioPlayer.addEventListener('ended', () => {
    updateUI('idle');
  });

  audioPlayer.addEventListener('play', () => {
    recordBtn.disabled = true;
  });

  transcriptToggleBtn.addEventListener("click", () => {
    const isHidden = transcriptContainer.hasAttribute("hidden");
    if (isHidden) {
      transcriptContainer.removeAttribute("hidden");
      transcriptToggleBtn.textContent = "Hide Transcript";
    } else {
      transcriptContainer.setAttribute("hidden", true);
      transcriptToggleBtn.textContent = "Show Transcript";
    }
  });

  // --- INITIALIZE UI ---
  updateUI("idle");
});