import os
import logging
import pkg_resources
import requests
from webob import Response
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin
from dotenv import load_dotenv

# Load environment variables if .env file exists
env_file = os.getenv('ENV_FILE', '.env.development')
load_dotenv(env_file)

log = logging.getLogger(__name__)

class IBALChatXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An XBlock that provides a chat interface integrated with OpenEdX authentication
    and connects to a backend WebSocket server.
    """
    
    display_name = String(
        display_name="Display Name",
        default="IBAL Chat",
        scope=Scope.settings,
        help="This name appears in the horizontal navigation at the top of the page."
    )

    introduction_text = String(
        display_name="Introduction Text",
        default="Welcome to the chat interface. Click the button below to start chatting.",
        scope=Scope.settings,
        help="Text that appears above the chat button."
    )

    oauth_client_id = String(
        display_name="OAuth Client ID",
        default=os.getenv('OPENEDX_CLIENT_ID', ''),
        scope=Scope.settings,
        help="The OAuth client ID for authentication."
    )

    oauth_client_secret = String(
        display_name="OAuth Client Secret",
        default=os.getenv('OPENEDX_CLIENT_SECRET', ''),  # .env file has this value
        scope=Scope.settings,
        help="The OAuth client secret for authentication."
    )

    oauth_redirect_uri = String(
        display_name="OAuth Redirect URI",
        default=os.getenv('OPENEDX_REDIRECT_URI', 'http://mylocal.test:8000/oauth/callback/'),
        scope=Scope.settings,
        help="The OAuth redirect URI for authentication."
    )

    ws_url = String(
        display_name="WebSocket URL",
        default=os.getenv('WS_URL', 'ws://mylocal.test:8000/ws/chat/'),
        scope=Scope.settings,
        help="The WebSocket server URL for chat functionality."
    )

    editable_fields = [
        'display_name',
        'introduction_text',
        'oauth_client_id',
        'oauth_client_secret',
        'oauth_redirect_uri',
        'ws_url'
    ]

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the IBALChatXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/ibal_chat.html")
        frag = Fragment(html.format(self=self))
        
        # Add jQuery
        frag.add_javascript_url("https://code.jquery.com/jquery-3.7.1.min.js")
        
        # Add the CSS
        frag.add_css(self.resource_string("static/css/ibal_chat.css"))
        
        # Add the JavaScript
        frag.add_javascript(self.resource_string("static/js/src/ibal_chat.js"))
        
        # Initialize the JavaScript with configuration
        frag.initialize_js('IBALChatXBlock', {
            'wsUrl': self.ws_url,
            'oauthClientId': self.oauth_client_id,
            'oauthRedirectUri': self.oauth_redirect_uri
        })
        
        return frag

    @XBlock.json_handler
    def get_auth_url(self, data, suffix=''):
        """
        Handler to get the OAuth authentication URL
        """
        auth_url =f"{os.getenv('OPENEDX_AUTH_URL', 'http://local.openedx.io/oauth2/authorize/')}?client_id={self.oauth_client_id}&response_type=code&redirect_uri={self.oauth_redirect_uri}"
        return {"auth_url": auth_url}

    @XBlock.json_handler
    def exchange_token(self, data, suffix=''):
        """
        Handler to exchange the OAuth code for a token
        """
        code = data.get('code')
        if not code:
            return {"error": "No code provided"}
            
        try:
            # Make the token exchange request to your backend
            response = requests.post(
                f"{self.ws_url.replace('ws://', 'http://').replace('/ws/chat/', '/oauth2/token/')}",
                data={
                    'code': code,
                    'client_id': self.oauth_client_id,
                    'client_secret': self.oauth_client_secret
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'status': 'success',
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data['refresh_token'],
                    'expires_in': token_data['expires_in']
                }
            else:
                log.error(f"Token exchange failed: {response.text}")
                return {"error": "Token exchange failed"}
                
        except Exception as e:
            log.error(f"Error in token exchange: {str(e)}")
            return {"error": str(e)}

    @XBlock.json_handler
    def refresh_token(self, data, suffix=''):
        """
        Handler to refresh the OAuth token
        """
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return {"error": "No refresh token provided"}
            
        try:
            # Make the token refresh request to your backend
            response = requests.post(
                f"{self.ws_url.replace('ws://', 'http://').replace('/ws/chat/', '/oauth2/refresh/')}",
                data={
                    'refresh_token': refresh_token,
                    'client_id': self.oauth_client_id,
                    'client_secret': self.oauth_client_secret
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'status': 'success',
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data['refresh_token'],
                    'expires_in': token_data['expires_in']
                }
            else:
                log.error(f"Token refresh failed: {response.text}")
                return {"error": "Token refresh failed"}
                
        except Exception as e:
            log.error(f"Error in token refresh: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("IBAL Chat XBlock",
             """<ibal_chat/>
             """),
        ] 