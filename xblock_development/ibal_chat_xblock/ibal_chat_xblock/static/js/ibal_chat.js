function IBALChatXBlock(runtime, element) {
  console.log("Initializing IBALChatXBlock");

  // State management
  let state = {
    currentPage: "initial",
    authCode: null,
    token: null,
    isConnected: false,
    backendStatus: {
      isAvailable: false,
      lastCheck: null,
    },
  };

  // DOM Elements
  const $element = $(element);
  const $startChatBtn = $element.find(".start-chat-btn");
  const $newChatBtn = $element.find(".new-chat-btn");
  const $sendBtn = $element.find(".send-btn");
  const $messageInput = $element.find(".message-input");
  const $chatMessages = $element.find(".chat-messages");
  const $errorMessage = $element.find(".error-message");
  const $connectionStatus = $element.find(".connection-status");
  const $pages = $element.find(".page");
  const $checkStatusBtn = $element.find(".check-status-btn");
  const $serviceStatus = $element.find(".service-status");
  const $backendStatus = $element.find(".backend-status");
  const $lastCheckTime = $element.find(".last-check-time");

  // Helper functions
  function showPage(pageName) {
    console.log(`Showing page: ${pageName}`);
    $pages.hide();
    $(`.page-${pageName}`).show();
    state.currentPage = pageName;
  }

  function showError(message) {
    console.error("Error:", message);
    $errorMessage.text(message).show();
    setTimeout(() => $errorMessage.fadeOut(), 5000);
  }

  function updateConnectionStatus(isConnected) {
    console.log(
      `Connection status: ${isConnected ? "connected" : "disconnected"}`
    );
    state.isConnected = isConnected;
    $connectionStatus
      .text(isConnected ? "Connected" : "Disconnected")
      .toggleClass("connected", isConnected)
      .toggleClass("disconnected", !isConnected);
  }

  function addMessage(content, isUser = false) {
    console.log(`Adding message: ${content} (user: ${isUser})`);
    const $message = $("<div>")
      .addClass("message")
      .addClass(isUser ? "user" : "bot")
      .text(content);
    $chatMessages.append($message);
    $chatMessages.scrollTop($chatMessages[0].scrollHeight);
  }

  // Backend service status checking
  async function checkBackendStatus() {
    console.log("Checking backend service status");
    $backendStatus.text("Checking...").addClass("checking");
    $serviceStatus.show();

    try {
      const response = await $.ajax({
        url: runtime.handlerUrl(element, "check_backend_status"),
        type: "POST",
        data: JSON.stringify({}),
        contentType: "application/json",
      });

      console.log("Backend status response:", response);
      state.backendStatus.isAvailable = response.isAvailable;
      state.backendStatus.lastCheck = new Date();

      $backendStatus
        .text(response.isAvailable ? "Available" : "Unavailable")
        .removeClass("checking")
        .addClass(response.isAvailable ? "available" : "unavailable");

      $lastCheckTime.text(state.backendStatus.lastCheck.toLocaleTimeString());

      if (!response.isAvailable) {
        showPage("backend-error");
      }

      return response.isAvailable;
    } catch (error) {
      console.error("Backend status check error:", error);
      state.backendStatus.isAvailable = false;
      state.backendStatus.lastCheck = new Date();

      $backendStatus
        .text("Unavailable")
        .removeClass("checking")
        .addClass("unavailable");

      $lastCheckTime.text(state.backendStatus.lastCheck.toLocaleTimeString());
      showPage("backend-error");
      return false;
    }
  }

  // Authentication process
  async function startAuthentication() {
    console.log("Starting authentication process");

    // Check backend status before proceeding
    const isBackendAvailable = await checkBackendStatus();
    if (!isBackendAvailable) {
      console.log("Backend service unavailable, cannot start authentication");
      return;
    }

    showPage("auth-code");

    try {
      const response = await $.ajax({
        url: runtime.handlerUrl(element, "get_auth_code"),
        type: "POST",
        data: JSON.stringify({}),
        contentType: "application/json",
      });

      console.log("Auth code response:", response);
      if (response.success) {
        state.authCode = response.auth_code;
        showPage("token-exchange");
        await exchangeToken();
      } else {
        throw new Error(response.error || "Failed to get authorization code");
      }
    } catch (error) {
      console.error("Authentication error:", error);
      showError("Failed to start authentication process");
      showPage("error");
    }
  }

  async function exchangeToken() {
    console.log("Exchanging token");
    try {
      const response = await $.ajax({
        url: runtime.handlerUrl(element, "exchange_token"),
        type: "POST",
        data: JSON.stringify({
          auth_code: state.authCode,
        }),
        contentType: "application/json",
      });

      console.log("Token exchange response:", response);
      if (response.success) {
        state.token = response.token;
        updateConnectionStatus(true);
        showPage("chat");
      } else {
        throw new Error(response.error || "Failed to exchange token");
      }
    } catch (error) {
      console.error("Token exchange error:", error);
      showError("Failed to exchange token");
      showPage("error");
    }
  }

  // Event handlers
  $startChatBtn.on("click", function () {
    console.log("Start chat button clicked");
    startAuthentication();
  });

  $newChatBtn.on("click", function () {
    console.log("New chat button clicked");
    showPage("initial");
    state = {
      currentPage: "initial",
      authCode: null,
      token: null,
      isConnected: false,
      backendStatus: {
        isAvailable: false,
        lastCheck: null,
      },
    };
    updateConnectionStatus(false);
  });

  $checkStatusBtn.on("click", async function () {
    console.log("Check status button clicked");
    await checkBackendStatus();
  });

  $sendBtn.on("click", async function () {
    const message = $messageInput.val().trim();
    if (!message) return;

    // Check backend status before sending message
    const isBackendAvailable = await checkBackendStatus();
    if (!isBackendAvailable) {
      console.log("Backend service unavailable, cannot send message");
      return;
    }

    console.log("Sending message:", message);
    addMessage(message, true);
    $messageInput.val("");

    try {
      const response = await $.ajax({
        url: runtime.handlerUrl(element, "send_message"),
        type: "POST",
        data: JSON.stringify({
          message: message,
          token: state.token,
        }),
        contentType: "application/json",
      });

      console.log("Message response:", response);
      if (response.success) {
        addMessage(response.reply);
      } else {
        throw new Error(response.error || "Failed to send message");
      }
    } catch (error) {
      console.error("Message error:", error);
      showError("Failed to send message");
      updateConnectionStatus(false);
      showPage("error");
    }
  });

  // Initialize
  console.log("IBALChatXBlock initialized");
  showPage("initial");
  updateConnectionStatus(false);
  checkBackendStatus(); // Initial backend status check
}
