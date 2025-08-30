// static/script.js
document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const recordBtn = document.getElementById("recordBtn");
    const statusDisplay = document.getElementById("statusDisplay");
    const chatLog = document.getElementById('chat-log');
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const saveKeysBtn = document.getElementById('saveKeysBtn');

    // API Key Inputs
    const assemblyaiKeyInput = document.getElementById('assemblyaiKey');
    const geminiKeyInput = document.getElementById('geminiKey');
    const murfKeyInput = document.getElementById('murfKey');
    const serpapiKeyInput = document.getElementById('serpapiKey');

    // State
    let isRecording = false;
    let ws = null;
    let audioContext;
    let mediaStream;
    let processor;
    let audioQueue = [];
    let isPlaying = false;
    
    // --- API Key Management ---
    const loadKeys = () => {
        assemblyaiKeyInput.value = localStorage.getItem('assemblyai_key') || '';
        geminiKeyInput.value = localStorage.getItem('gemini_key') || '';
        murfKeyInput.value = localStorage.getItem('murf_key') || '';
        serpapiKeyInput.value = localStorage.getItem('serpapi_key') || '';
    };

    const saveKeys = () => {
        localStorage.setItem('assemblyai_key', assemblyaiKeyInput.value);
        localStorage.setItem('gemini_key', geminiKeyInput.value);
        localStorage.setItem('murf_key', murfKeyInput.value);
        localStorage.setItem('serpapi_key', serpapiKeyInput.value);
        alert('API Keys saved successfully!');
        settingsModal.style.display = 'none';
    };
    
    // --- Modal Control ---
    settingsBtn.addEventListener('click', () => settingsModal.style.display = 'flex');
    closeModalBtn.addEventListener('click', () => settingsModal.style.display = 'none');
    saveKeysBtn.addEventListener('click', saveKeys);
    
    // --- UI Helpers ---
    const addMessage = (text, type) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`; // 'user' or 'assistant'
        messageDiv.textContent = text;
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    // --- Audio Playback Logic ---
    const playNextInQueue = async () => {
        if (isPlaying || audioQueue.length === 0) {
            if (audioQueue.length === 0 && !isPlaying) {
                // All audio has finished playing
                statusDisplay.textContent = "Tap the mic to speak again.";
                recordBtn.disabled = false;
            }
            return;
        }
        isPlaying = true;

        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }
        
        const base64Audio = audioQueue.shift();
        try {
            const audioData = Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0)).buffer;
            const buffer = await audioContext.decodeAudioData(audioData);
            const source = audioContext.createBufferSource();
            source.buffer = buffer;
            source.connect(audioContext.destination);
            source.onended = () => {
                isPlaying = false;
                playNextInQueue();
            };
            source.start();
        } catch (e) {
            console.error("Error playing audio:", e);
            isPlaying = false;
            playNextInQueue();
        }
    };
    
    // --- Core Recording Logic ---
    const startRecording = async () => {
        const assemblyaiKey = localStorage.getItem('assemblyai_key');
        const geminiKey = localStorage.getItem('gemini_key');
        const murfKey = localStorage.getItem('murf_key');

        if (!assemblyaiKey || !geminiKey || !murfKey) {
            alert("Please set your AssemblyAI, Gemini, and Murf.ai API keys in the settings first!");
            settingsModal.style.display = 'flex';
            return;
        }

        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
            }

            const source = audioContext.createMediaStreamSource(mediaStream);
            processor = audioContext.createScriptProcessor(4096, 1, 1);
            source.connect(processor);
            processor.connect(audioContext.destination);

            processor.onaudioprocess = (e) => {
                const inputData = e.inputBuffer.getChannelData(0);
                const pcmData = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 32767;
                }
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(pcmData.buffer);
                }
            };

            const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            const queryParams = new URLSearchParams({
                assemblyai_key: assemblyaiKey,
                gemini_key: geminiKey,
                murf_key: murfKey,
                serpapi_key: localStorage.getItem('serpapi_key') || ''
            }).toString();

            ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws?${queryParams}`);

            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.type === "final") {
                    addMessage(msg.text, "user");
                    statusDisplay.textContent = "Thinking...";
                    recordBtn.disabled = true;
                } else if (msg.type === "assistant") {
                    addMessage(msg.text, "assistant");
                    statusDisplay.textContent = "Speaking...";
                } else if (msg.type === "audio") {
                    audioQueue.push(msg.b64);
                    playNextInQueue();
                } else if (msg.type === "error") {
                    console.error("Error from server:", msg.message);
                    addMessage(`Error: ${msg.message}`, "assistant");
                    stopRecording();
                }
            };
            
            ws.onopen = () => {
                isRecording = true;
                recordBtn.classList.add("recording");
                statusDisplay.textContent = "Listening...";
            };

            ws.onclose = () => {
                console.log("WebSocket connection closed.");
                if (isRecording) stopRecording(false); // Don't try to close ws again
            };
            
            ws.onerror = (error) => {
                console.error("WebSocket error:", error);
                if (isRecording) stopRecording();
            };

        } catch (error) {
            console.error("Could not start recording:", error);
            alert("Microphone access is required. Please grant permission and try again.");
        }
    };

    const stopRecording = (closeWs = true) => {
        if (processor) processor.disconnect();
        if (mediaStream) mediaStream.getTracks().forEach(track => track.stop());
        if (closeWs && ws && ws.readyState === WebSocket.OPEN) ws.close();
        
        isRecording = false;
        recordBtn.classList.remove("recording");
        statusDisplay.textContent = "Processing...";
    };

    recordBtn.addEventListener("click", () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    // Initialize
    loadKeys();
});