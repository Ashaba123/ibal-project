function IBALChatXBlock(runtime, element, config) {
  let ws = null;
  let accessToken = null;
  let refreshToken = null;
  let tokenExpiry = null;
  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 5000; // 5 seconds

  // DOM elements
  const chatContainer = $('.chat-container', element);
  const messageInput = $('.message-input', element);
  const sendButton = $('.send-button', element);
  const startChatButton = $('.start-chat-button', element);

  // Initialize the XBlock
  function init() {
    // Check if we have stored tokens
    const storedTokens = localStorage.getItem('ibal_chat_tokens');
    if (storedTokens) {
      const tokens = JSON.parse(storedTokens);
      accessToken = tokens.access_token;
      refreshToken = tokens.refresh_token;
      tokenExpiry = new Date(tokens.expiry);
      
      if (tokenExpiry > new Date()) {
        connectWebSocket();
      } else {
        refreshAccessToken();
      }
    }

    // Event listeners
    startChatButton.on('click', startChat);
    sendButton.on('click', sendMessage);
    messageInput.on('keypress', function(e) {
      if (e.which === 13) {
        sendMessage();
      }
    });
  }

  // Start the chat process
  function startChat() {
    $.ajax({
      url: runtime.handlerUrl(element, 'get_auth_url'),
      type: 'POST',
      data: JSON.stringify({}),
      contentType: 'application/json'
    }).done(function(response) {
      if (response.auth_url) {
        // Open the OAuth authorization page
        window.location.href = response.auth_url;
      }
    });
  }

  // Handle OAuth callback
  function handleOAuthCallback(code) {
    $.ajax({
      url: runtime.handlerUrl(element, 'exchange_token'),
      type: 'POST',
      data: JSON.stringify({ code: code }),
      contentType: 'application/json'
    }).done(function(response) {
      if (response.status === 'success') {
        // Store tokens
        accessToken = response.access_token;
        refreshToken = response.refresh_token;
        tokenExpiry = new Date(Date.now() + (response.expires_in * 1000));
        
        localStorage.setItem('ibal_chat_tokens', JSON.stringify({
          access_token: accessToken,
          refresh_token: refreshToken,
          expiry: tokenExpiry
        }));

        // Connect to WebSocket
        connectWebSocket();
      }
    });
  }

  // Connect to WebSocket
  function connectWebSocket() {
    if (ws) {
      ws.close();
    }

    ws = new WebSocket(`${config.wsUrl}?token=${accessToken}&auth_type=oauth2`);

    ws.onopen = function() {
      console.log('WebSocket connected');
      reconnectAttempts = 0;
      chatContainer.addClass('connected');
    };

    ws.onmessage = function(event) {
      const message = JSON.parse(event.data);
      displayMessage(message);
    };

    ws.onclose = function() {
      console.log('WebSocket disconnected');
      chatContainer.removeClass('connected');
      
      // Attempt to reconnect
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        setTimeout(connectWebSocket, RECONNECT_DELAY);
      }
    };

    ws.onerror = function(error) {
      console.error('WebSocket error:', error);
    };
  }

  // Refresh access token
  function refreshAccessToken() {
    if (!refreshToken) {
      startChat();
      return;
    }

    $.ajax({
      url: runtime.handlerUrl(element, 'refresh_token'),
      type: 'POST',
      data: JSON.stringify({ refresh_token: refreshToken }),
      contentType: 'application/json'
    }).done(function(response) {
      if (response.status === 'success') {
        accessToken = response.access_token;
        refreshToken = response.refresh_token;
        tokenExpiry = new Date(Date.now() + (response.expires_in * 1000));
        
        localStorage.setItem('ibal_chat_tokens', JSON.stringify({
          access_token: accessToken,
          refresh_token: refreshToken,
          expiry: tokenExpiry
        }));

        connectWebSocket();
      } else {
        startChat();
      }
    });
  }

  // Send message
  function sendMessage() {
    const content = messageInput.val().trim();
    if (!content || !ws || ws.readyState !== WebSocket.OPEN) {
      return;
    }

    const message = {
      type: 'message',
      content: content
    };

    ws.send(JSON.stringify(message));
    messageInput.val('');
  }

  // Display message
  function displayMessage(message) {
    const messageElement = $('<div>')
      .addClass('message')
      .addClass(message.isUser ? 'user-message' : 'assistant-message')
      .text(message.content);
    
    chatContainer.append(messageElement);
    chatContainer.scrollTop(chatContainer[0].scrollHeight);
  }

  // Check for OAuth callback
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  if (code) {
    handleOAuthCallback(code);
  }

  // Initialize
  init();
}