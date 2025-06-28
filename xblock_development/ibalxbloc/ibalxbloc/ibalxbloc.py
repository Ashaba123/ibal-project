from importlib.resources import files
from xblock.core import XBlock
from xblock.fields import Scope, String
from web_fragments.fragment import Fragment



# Define the IbalXBlock class
class IbalXBlock(XBlock):
    """A simple XBlock that displays a welcome message and a Start Chat button."""


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        return files(__package__).joinpath(path).read_text(encoding="utf-8")

    def student_view(self, context=None):
        """
        The primary view of the IBALXBlock, shown to students
        when viewing courses.
        """
        # Updated OAuth2 values for production
        client_id = "n9svQOtyYCkUZLLvPgH1LpEMuSynpO7VMSVeoFl5"
        client_secret = "HuGrd4T9qmCPvZxkvcHehLYrn4mnYrRAyoN9VHb9ZqNM9aRY3msrrsUX5cQ0gyQR0pyWxz44zXKGHNGXQVxUwnRLdYxrGcaN6xOpf0ia5cAn2J8yUBi2HbikyJqA8cUG"
        auth_url = "http://local.openedx.io/oauth2/authorize/"
        token_url = "http://local.openedx.io/oauth2/access_token/"
        redirect_uri = "http://mylocal.test:8000/api/oauth/callback/"
        html_str = self.resource_string('static/html/ibalxbloc.html')
        html_str = html_str.replace(
            '<div class="ibalxbloc-container"',
            f'<div class="ibalxbloc-container" data-client-id="{client_id}" data-client-secret="{client_secret}" data-auth-url="{auth_url}" data-token-url="{token_url}" data-redirect-uri="{redirect_uri}"',
            1
        )
        frag = Fragment(html_str.format(self=self))
        frag.add_css(self.resource_string('static/css/ibalxbloc.css'))
        frag.add_javascript(self.resource_string('static/js/src/ibalxbloc.js'))
        frag.initialize_js('IbalXBlock')
        return frag

    # this function is used to display the block in the workbench
    @staticmethod
    def workbench_scenarios():
        """A set of scenarios for display in the workbench."""
        return [
            ("IbalXBlock - Simple scenario",
             "<vertical_demo><ibalxbloc/></vertical_demo>"),
        ]