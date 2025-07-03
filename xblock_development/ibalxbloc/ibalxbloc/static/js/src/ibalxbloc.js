function IbalXBlock(runtime, element) {
  const $container = $(element).find(".ibalxbloc-container");
  const clientId = $container.data("client-id") || "MISSING_CLIENT_ID";
  const clientSecret =
    $container.data("client-secret") || "MISSING_CLIENT_SECRET";
  const authEndpoint =
    $container.data("auth-url") || "http://local.openedx.io/oauth2/authorize/";
  const tokenEndpoint =
    $container.data("token-url") ||
    "http://local.openedx.io/oauth2/access_token/";
  const redirectUri =
    $container.data("redirect-uri") ||
    "http://mylocal.test:8000/api/oauth/callback/";
  const websocketUrl = "ws://localhost:8000/ws/chat/";

  // Chat state variables
  let websocket = null;
  let currentUsername = window.IBAL_USERNAME || "Unknown User";
  let isConnected = false;

  // Set the username display immediately on load
  $(element).find("#logged-username").text(currentUsername);

  // Helper to update status
  function updateStatus(msg, type = "info") {
    let statusDiv = $(element).find("#ibalxbloc-status");
    if (statusDiv.length === 0) {
      statusDiv = $('<div id="ibalxbloc-status"></div>').appendTo(element);
    }
    statusDiv.text(msg);

    // Add status styling
    statusDiv.removeClass("status-info status-success status-error");
    statusDiv.addClass(`status-${type}`);
  }

  // Helper to update connection status
  function updateConnectionStatus(status, message) {
    const $statusIndicator = $(element).find("#connection-status");
    $statusIndicator.removeClass("connecting connected disconnected error");
    $statusIndicator.addClass(status);
    $statusIndicator.text(message);
  }

  // Helper to show/hide chat interface
  function showChatInterface() {
    $(element).find("#start-chat-section").hide();
    $(element).find("#chat-interface").show();
  }

  function hideChatInterface() {
    $(element).find("#chat-interface").hide();
    $(element).find("#start-chat-section").show();
    // Clear messages
    $(element).find("#messages-list").empty();
    // Reset connection status
    updateConnectionStatus("disconnected", "Disconnected");
    isConnected = false;
  }

  // Helper to show/hide loading bubble
  function showLoadingBubble() {
    $(element).find("#loading-bubble").show();
  }
  function hideLoadingBubble() {
    $(element).find("#loading-bubble").hide();
  }

  // Helper to add message to chat
  function addMessage(message, sender, isOwnMessage = false) {
    if (!message || typeof message !== "string" || message.trim() === "") {
      return; // Don't render empty messages
    }
    // Hide loading bubble when a new message is received
    hideLoadingBubble();
    const $messagesList = $(element).find("#messages-list");
    const messageClass = isOwnMessage ? "sent" : "received";
    const currentTime = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    const messageHtml = `
      <div class="message ${messageClass}">
        <div class="message-bubble">
          <div class="message-content">${escapeHtml(message)}</div>
          <div class="message-meta">
            ${escapeHtml(sender)} • ${currentTime}
          </div>
        </div>
      </div>
    `;

    $messagesList.append(messageHtml);

    // Scroll to bottom
    const $messagesContainer = $(element).find("#messages-container");
    $messagesContainer.scrollTop($messagesContainer[0].scrollHeight);
  }

  // Helper to escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Helper to check if JWT token is expired
  function isTokenExpired(token) {
    if (!token) return true;
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      if (!payload.exp) return true;
      // exp is in seconds since epoch
      const now = Math.floor(Date.now() / 1000);
      return payload.exp < now;
    } catch (e) {
      return true; // treat as expired if any error
    }
  }

  // Helper to send message via WebSocket
  function sendMessage(message) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const messageData = {
        type: "message",
        content: message,
        sender: currentUsername,
        timestamp: new Date().toISOString(),
      };
      websocket.send(JSON.stringify(messageData));
      return true;
    }
    return false;
  }

  // Helper to connect to chat WebSocket
  function connectToChat(token) {
    if (!token) {
      updateConnectionStatus("error", "No token available");
      return;
    }

    try {
      console.log("[IbalXBlock] Using access_token for WebSocket:", token);
      console.log(
        "[IbalXBlock] Opening WebSocket connection to:",
        `${websocketUrl}?token=${token}&auth_type=oauth2`
      );

      updateConnectionStatus("connecting", "Connecting...");

      websocket = new WebSocket(
        `${websocketUrl}?token=${token}&auth_type=oauth2`
      );

      websocket.onopen = function () {
        console.log("[IbalXBlock] WebSocket connection opened");
        isConnected = true;
        updateConnectionStatus("connected", "Connected");
        updateStatus("Connected to chat!", "success");

        // Show chat interface
        showChatInterface();

        // Add welcome message
        addMessage(
          "Welcome to the chat! You can now start messaging.",
          "System",
          false
        );
      };

      websocket.onmessage = function (event) {
        console.log("[IbalXBlock] Received message:", event.data);
        try {
          const data = JSON.parse(event.data);

          if (data.type === "message") {
            const isOwnMessage = data.sender === currentUsername;
            addMessage(data.content, data.sender, isOwnMessage);
          } else if (data.type === "user_info") {
            console.log("[IbalXBlock] user_info received:", data);
            currentUsername = data.username || "Unknown User";
            $(element).find("#logged-username").text(currentUsername);
          } else if (data.type === "system") {
            addMessage(data.message, "System", false);
          }
        } catch (error) {
          console.error("[IbalXBlock] Error parsing message:", error);
          addMessage("Error processing message", "System", false);
        }
      };

      websocket.onerror = function (err) {
        console.error("[IbalXBlock] WebSocket connection error:", err);
        isConnected = false;
        updateConnectionStatus("error", "Connection Error");
        updateStatus("WebSocket connection error.", "error");
      };

      websocket.onclose = function (event) {
        console.log("[IbalXBlock] WebSocket connection closed", event);
        isConnected = false;
        updateConnectionStatus("disconnected", "Disconnected");
        updateStatus("WebSocket connection closed.", "error");
      };
    } catch (err) {
      console.error("[IbalXBlock] Error opening WebSocket:", err);
      updateConnectionStatus("error", "Connection Failed");
      updateStatus("WebSocket connection error.", "error");
    }
  }

  // Event handlers
  function handleStartChat() {
    console.log("[IbalXBlock] Start Chat button activated");
    const authUrl = `${authEndpoint}?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(
      redirectUri
    )}`;
    console.log("[IbalXBlock] Opening OAuth2 authorize popup:", authUrl);
    window.open(
      authUrl,
      "oauth2popup",
      "width=500,height=700,menubar=no,toolbar=no,location=no,status=no"
    );
  }

  function handleCloseChat() {
    console.log("[IbalXBlock] Close Chat button activated");
    if (websocket) {
      websocket.close();
    }
    hideChatInterface();
    updateStatus("Chat closed. Click Start Chat to begin again.", "info");
  }

  function handleSendMessage() {
    const $messageInput = $(element).find("#message-input");
    const message = $messageInput.val().trim();

    if (message && isConnected) {
      if (sendMessage(message)) {
        addMessage(message, currentUsername, true);
        $messageInput.val("");
        // Show loading bubble after sending a message
        showLoadingBubble();
      } else {
        updateStatus(
          "Failed to send message. Please check your connection.",
          "error"
        );
      }
    }
  }

  function handleKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }

  // Initialize event listeners
  function initializeEventListeners() {
    // Start Chat button
    $(element)
      .find("#start-chat-btn")
      .on("click keydown", function (event) {
        if (
          event.type === "click" ||
          (event.type === "keydown" &&
            (event.key === "Enter" || event.key === " "))
        ) {
          event.preventDefault();
          handleStartChat();
        }
      });

    // Close Chat button
    $(element)
      .find("#close-chat-btn")
      .on("click keydown", function (event) {
        if (
          event.type === "click" ||
          (event.type === "keydown" &&
            (event.key === "Enter" || event.key === " "))
        ) {
          event.preventDefault();
          handleCloseChat();
        }
      });

    // Send Message button
    $(element)
      .find("#send-message-btn")
      .on("click", function (event) {
        event.preventDefault();
        handleSendMessage();
      });

    // Message input key press
    $(element).find("#message-input").on("keypress", handleKeyPress);
  }

  // Initialize on page load
  $(document).ready(function () {
    // Initialize event listeners
    initializeEventListeners();

    // If we are on the callback page, handle token storage
    if (window.location.pathname.endsWith("/api/oauth/callback/")) {
      fetch(window.location.href, { credentials: "include" })
        .then((response) => response.json())
        .then((data) => {
          if (data.access_token) {
            window.localStorage.setItem("access_token", data.access_token);
            if (window.opener) {
              window.opener.postMessage(
                { type: "oauth2_token", access_token: data.access_token },
                "*"
              );
            }
            updateStatus("Token received! Closing window...");
            setTimeout(() => window.close(), 500);
          } else {
            updateStatus(
              "Failed to get token: " + (data.error_description || data.error),
              "error"
            );
          }
        })
        .catch((err) => {
          console.error(
            "[IbalXBlock] Error during token fetch from callback:",
            err
          );
          updateStatus("Token fetch error.", "error");
          setTimeout(() => window.close(), 1000);
        });
      return;
    }

    // Listen for token from popup (in main XBlock window)
    window.addEventListener("message", function (event) {
      if (event.data && event.data.type === "oauth2_token") {
        window.localStorage.setItem("access_token", event.data.access_token);
        updateStatus(
          "Token received from popup! Connecting to chat...",
          "success"
        );
        connectToChat(event.data.access_token);
      }
    });

    // Check for existing token
    const token = window.localStorage.getItem("access_token");
    if (token && !isTokenExpired(token)) {
      console.log("[IbalXBlock] Access token found in localStorage:", token);
      updateStatus("Connecting to chat...", "info");
      connectToChat(token);
    } else {
      if (token) {
        // Token exists but is expired
        window.localStorage.removeItem("access_token");
        updateStatus(
          "Session expired. Please click Start Chat to login again.",
          "error"
        );
      } else {
        updateStatus("Click Start Chat to begin.", "info");
      }
    }
  });
}
