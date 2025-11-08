document.addEventListener("DOMContentLoaded", () => {
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const chatDisplay = document.getElementById("chat-display");
  const languageToggle = document.getElementById("language-toggle-checkbox");
  const clearButton = document.getElementById("clear-button");

  let currentLanguage = "vi"; // Default language

  const translations = {
    vi: {
      placeholder: "Nhập câu hỏi của bạn...",
      greeting:
        "Xin chào! Tôi là trợ lý IT ảo. Bạn cần hỗ trợ vấn đề gì hôm nay?",
      errorMessage: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
      clearConfirm: "Bạn có chắc chắn muốn xóa toàn bộ hội thoại?",
    },
    en: {
      placeholder: "Type your question here...",
      greeting:
        "Hello! I am your virtual IT assistant. What issue do you need assistance with today?",
      errorMessage: "Sorry, an error occurred. Please try again later.",
      clearConfirm: "Are you sure you want to clear the entire conversation?",
    },
  };

  const setLanguage = (lang) => {
    currentLanguage = lang;
    userInput.placeholder = translations[lang].placeholder;

    // Show/hide initial greeting messages
    document.querySelectorAll(".message.bot p[lang]").forEach((p) => {
      p.style.display = p.getAttribute("lang") === lang ? "block" : "none";
    });
  };

  languageToggle.addEventListener("change", () => {
    const lang = languageToggle.checked ? "en" : "vi";
    setLanguage(lang);
  });

  // Initialize default language on load
  setLanguage(currentLanguage);

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
          language: currentLanguage, // Send current language to backend
          enable_tts: false, // TTS is removed
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // 4. Hide loading indicator
      hideLoadingIndicator();

      // 5. Append message
      appendMessage("bot", data.response);
    } catch (error) {
      console.error("Failed to send message:", error);
      // 7. Hide loading indicator and display an error
      hideLoadingIndicator();
      appendMessage("bot", translations[currentLanguage].errorMessage);
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

  const clearChat = () => {
    if (confirm(translations[currentLanguage].clearConfirm)) {
      // Clear all messages
      chatDisplay.innerHTML = "";

      // Add back the initial greeting message
      const greetingElement = document.createElement("div");
      greetingElement.classList.add("message", "bot");

      const viGreeting = document.createElement("p");
      viGreeting.setAttribute("lang", "vi");
      viGreeting.textContent = translations.vi.greeting;
      viGreeting.style.display = currentLanguage === "vi" ? "block" : "none";

      const enGreeting = document.createElement("p");
      enGreeting.setAttribute("lang", "en");
      enGreeting.textContent = translations.en.greeting;
      enGreeting.style.display = currentLanguage === "en" ? "block" : "none";

      greetingElement.appendChild(viGreeting);
      greetingElement.appendChild(enGreeting);
      chatDisplay.appendChild(greetingElement);
    }
  };

  // --- Event Listeners ---

  sendButton.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
  clearButton.addEventListener("click", clearChat);
});
