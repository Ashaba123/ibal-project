# XBLOCK

Create your xblocks here and test them out with the xblock-sdk

Follow instructions of xblock sdk and xblock creation:

<https://docs.openedx.org/projects/xblock/en/latest/xblock-tutorial/getting_started/prereqs.html>

->xblock-env/Scripts/activate
->(xblock-env)  pip install -e ibal_chat_xblock
->(xblock-env)  python xblock-sdk/manage.py migrate
->(xblock-env)  python xblock-sdk/manage.py runserver --noreload

Run Tutor local start - dont use launch coz it erases container

First run use two terminals
docker exec -u root -it tutor_local-cms-1 bash

docker cp "C:\Coding Projects\ibal-project\xblock_development\testxbloc" tutor_local-cms-1:/openedx/testxbloc

cd /openedx/testxbloc && pip install -e .

docker exec -u root -it tutor_local-lms-1 bash

docker cp "C:\Coding Projects\ibal-project\xblock_development\testxbloc" tutor_local-lms-1:/openedx/testxbloc

cd /openedx/testxbloc && pip install -e .

tutor local stop and then start.
Add it in Studio.local -> Advanced Settings ->["xbloc1","xbloc2"]

Then run below command in docker execute

cd /openedx/shinblock && pip install -e .

## OAuth2 Flow: From Button Click to WebSocket Connection (Updated)

1. **User Clicks the Start Chat Button in the XBlock**
   - The XBlock frontend JavaScript opens a popup to the Open edX OAuth2 authorization URL (`OPENEDX_AUTH_URL`), passing the `client_id` and `redirect_uri` (which points to your backend).

2. **User Authorizes the Application in Open edX**
   - The user logs in (if not already) and authorizes the application on the Open edX OAuth2 page.

3. **Open edX Redirects Back to Backend with Authorization Code**
   - After authorization, Open edX (the OAuth2 provider) redirects the browser to your backend's callback URL (e.g., `/api/oauth/callback/`) with a `?code=...` parameter.

4. **Backend Exchanges Code for Access Token with Open edX**
   - The backend's callback endpoint receives the code and makes a POST request to Open edX's `/oauth2/access_token/` endpoint, using the `client_id`, `client_secret`, and `redirect_uri` registered in Open edX admin.
   - If successful, the backend receives an access token from Open edX.

5. **Backend Returns the Access Token to the Frontend**
   - The backend responds to the callback request with the access token (typically as JSON).

6. **Frontend Stores the Access Token**
   - The callback page's JavaScript stores the access token (e.g., in `localStorage`).
   - The user is prompted to return to the chat/XBlock.

7. **XBlock JavaScript Uses the Access Token**
   - When the user returns to the XBlock, the frontend JavaScript retrieves the access token from storage.
   - The token is used to authenticate and open a WebSocket connection to the backend for chat or other real-time features.

**Summary:**
- Button click → OAuth2 authorize (Open edX) → redirect with code → backend exchanges code for token (with Open edX) → backend returns token to frontend → token stored → token used for WebSocket authentication.

**Important:**
- Open edX is the OAuth2 provider.
- The backend is an OAuth2 client (not a provider).
- The XBlock is the frontend client.
- The backend must not issue tokens or codes itself; it only exchanges the code for a token with Open edX.
- The `client_id`, `client_secret`, and `redirect_uri` must match what is registered in Open edX admin.
- The `redirect_uri` must match exactly in both the Open edX admin and the backend's token exchange request.
