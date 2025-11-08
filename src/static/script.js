document.addEventListener("DOMContentLoaded", () => {
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const chatDisplay = document.getElementById("chat-display");
  const ttsEnabled = document.getElementById("tts-enabled");
  // Các biến cho popup cũ đã bị loại bỏ

  // Enable/disable send button based on input
  userInput.addEventListener("input", () => {
    sendButton.disabled = userInput.value.trim() === "";
  });

  // --- Core Functions ---

  const sendMessage = async () => {
    const messageText = userInput.value.trim();
    if (messageText === "") return;

    // 1. Display user message and clear input
    appendMessage("user", messageText);
    userInput.value = "";
    sendButton.disabled = true;

    // 2. Show loading indicator
    showLoadingIndicator();

    try {
      // 3. Send message to the backend API
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: messageText,
          enable_tts: ttsEnabled.checked,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // 4. Hide loading indicator
      hideLoadingIndicator();

      // 5. Append message
      const botMessageElement = appendMessage("bot", data.response);

      // 6. Chèn và phát audio nếu TTS được bật
      if (ttsEnabled.checked && data.audio_url) {
        playAudio(botMessageElement, data.audio_url);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      // 7. Hide loading indicator and display an error
      hideLoadingIndicator();
      appendMessage("bot", "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.");
    }
  };

  // --- Helper Functions ---

  const appendMessage = (sender, text) => {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);

    // Tạo nội dung văn bản (đã được đánh dấu)
    const textContent = document.createElement("div");
    textContent.classList.add("message-text-content");
    textContent.innerHTML = marked.parse(text);
    messageElement.appendChild(textContent);

    chatDisplay.appendChild(messageElement);
    scrollToBottom();
    return messageElement; // Trả về element mới tạo
  };

  const showLoadingIndicator = () => {
    const loadingElement = document.createElement("div");
    loadingElement.classList.add("message", "bot", "typing");
    loadingElement.id = "loading-indicator"; // Assign an ID to easily find and remove it

    // Create three dots for the animation
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.classList.add("typing-dot");
      loadingElement.appendChild(dot);
    }

    chatDisplay.appendChild(loadingElement);
    scrollToBottom();
  };

  const hideLoadingIndicator = () => {
    const loadingElement = document.getElementById("loading-indicator");
    if (loadingElement) {
      loadingElement.remove();
    }
  };

  const scrollToBottom = () => {
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
  };

  // --- TTS Functions ---

  const playAudio = (messageElement, audioUrl) => {
    const audioWrapper = document.createElement("div");
    audioWrapper.classList.add("inline-audio-player");

    const audioElement = document.createElement("audio");
    audioElement.setAttribute("controls", "");
    audioElement.setAttribute("autoplay", "");
    audioElement.playbackRate = 1.25;

    const audioSource = document.createElement("source");
    audioSource.setAttribute("src", audioUrl);
    audioSource.setAttribute("type", "audio/wav");

    audioElement.appendChild(audioSource);

    const separator = document.createElement("hr");
    separator.classList.add("audio-separator");

    messageElement.appendChild(separator);
    audioWrapper.appendChild(audioElement);
    messageElement.appendChild(audioWrapper);

    audioElement.load();
    audioElement.play().catch((error) => {
      console.warn("Auto-play blocked, user must manually click play:", error);
    });
  };

  // --- Event Listeners ---

  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
});
