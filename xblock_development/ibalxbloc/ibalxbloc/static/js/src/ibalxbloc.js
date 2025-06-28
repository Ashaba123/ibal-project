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
  const websocketUrl = "ws://localhost:8000/ws/chat/"; // Your backend WebSocket endpoint

  // Helper to update status
  function updateStatus(msg) {
    let statusDiv = $(element).find("#ibalxbloc-status");
    if (statusDiv.length === 0) {
      statusDiv = $('<div id="ibalxbloc-status"></div>').appendTo(element);
    }
    statusDiv.text(msg);
  }

  // On Start Chat button click or keyboard activation, begin OAuth2 flow in a popup
  $(element)
    .find("#start-chat-btn")
    .on("click keydown", function (event) {
      if (
        event.type === "click" ||
        (event.type === "keydown" &&
          (event.key === "Enter" || event.key === " "))
      ) {
        event.preventDefault();
        console.log("[IbalXBlock] Start Chat button activated");
        // Open popup to Open edX OAuth2 authorize endpoint
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
    });

  // On page load, check if we have a token in localStorage
  $(document).ready(function () {
    // If we are on the callback page, handle token storage
    if (window.location.pathname.endsWith("/api/oauth/callback/")) {
      // The backend should return JSON with the token
      fetch(window.location.href, { credentials: "include" })
        .then((response) => response.json())
        .then((data) => {
          if (data.access_token) {
            window.localStorage.setItem("access_token", data.access_token);
            // Notify the opener (main XBlock window) and close the popup
            if (window.opener) {
              window.opener.postMessage(
                { type: "oauth2_token", access_token: data.access_token },
                "*"
              );
            }
            updateStatus("Token received! Closing window...");
            setTimeout(() => window.close(), 500); // Give time for message to send
          } else {
            updateStatus(
              "Failed to get token: " + (data.error_description || data.error)
            );
          }
        })
        .catch((err) => {
          console.error(
            "[IbalXBlock] Error during token fetch from callback:",
            err
          );
          updateStatus("Token fetch error.");
          setTimeout(() => window.close(), 1000);
        });
      return; // Do not run chat logic on callback page
    }

    // Listen for token from popup (in main XBlock window)
    window.addEventListener("message", function (event) {
      if (event.data && event.data.type === "oauth2_token") {
        window.localStorage.setItem("access_token", event.data.access_token);
        updateStatus("Token received from popup! Connecting to chat...");
        // Connect to chat WebSocket directly, do not reload the page
        connectToChat(event.data.access_token);
      }
    });

    // Helper to connect to chat WebSocket
    function connectToChat(token) {
      if (!token) return;
      try {
        console.log("[IbalXBlock] Using access_token for WebSocket:", token);
        console.log(
          "[IbalXBlock] Opening WebSocket connection to:",
          `${websocketUrl}?token=${token}&auth_type=oauth2`
        );
        const ws = new WebSocket(
          `${websocketUrl}?token=${token}&auth_type=oauth2`
        );
        ws.onopen = function () {
          console.log("[IbalXBlock] WebSocket connection opened");
          updateStatus("Connected to chat!");
        };
        ws.onerror = function (err) {
          console.error("[IbalXBlock] WebSocket connection error:", err);
          updateStatus("WebSocket connection error.");
        };
        ws.onclose = function (event) {
          console.log("[IbalXBlock] WebSocket connection closed", event);
          updateStatus("WebSocket connection closed.");
        };
      } catch (err) {
        console.error("[IbalXBlock] Error opening WebSocket:", err);
        updateStatus("WebSocket connection error.");
      }
    }

    const token = window.localStorage.getItem("access_token");
    if (token) {
      console.log("[IbalXBlock] Access token found in localStorage:", token);
      updateStatus("Connecting to chat...");
      connectToChat(token);
    } else {
      console.log("[IbalXBlock] No access token found in localStorage");
      updateStatus("Click Start Chat to begin.");
    }
  });
}
