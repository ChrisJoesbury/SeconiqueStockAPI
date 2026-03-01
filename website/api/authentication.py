# =============================================================================
# SeconiqueStockAPI | authentication.py
# =============================================================================
# Custom DRF authentication class that validates API keys from the Authorization
# header (format: Api-Key <key>) and resolves the associated Django User from
# the key name, which follows the format: {cust_id}_{username}.
# =============================================================================

#Get Rest Framework files
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.models import APIKey

#Get Django files
from django.contrib.auth.models import User


class CustomAPIKeyAuthentication(BaseAuthentication):
    """
    Authenticates requests using an API key in the Authorization header.
    Expected format: Authorization: Api-Key <key>

    API key names follow the format {cust_id}_{username}, allowing the
    authenticated user to be resolved from the key name.
    """
    keyword = "Api-Key"

    def authenticate(self, request):
        """Validate an API key from the Authorization header and resolve the user.

        Args:
            request (HttpRequest): The incoming DRF request containing HTTP headers.

        Returns:
            tuple[User, None]: A two-tuple of (user, None) on successful
                authentication, where None is the auth token (unused here).
            tuple[None, None]: If the key is valid but no matching User is found,
                or if the key name does not follow the expected format.
            None: If the Authorization header is absent or does not start with
                'Api-Key ', signalling DRF to try the next authenticator.

        Raises:
            AuthenticationFailed: If the key string is present but not found
                in the database — the request is rejected immediately.

        Contract:
            - Key name must follow the format '{cust_id}_{username}'. The split
              is limited to the first underscore, so usernames containing
              underscores are handled correctly.
            - Returning None (not a tuple) tells DRF this authenticator does not
              apply; returning (None, None) means authentication was attempted
              but could not resolve a user.
        """
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith(self.keyword + " "):
            return None

        key = auth[len(self.keyword) + 1:].strip()
        try:
            api_key = APIKey.objects.get_from_key(key)

            # Extract username from key name format: {cust_id}_{username}
            # Split only on the first underscore so usernames containing underscores are handled correctly
            if api_key.name and '_' in api_key.name:
                parts = api_key.name.split('_', 1)
                if len(parts) == 2:
                    username = parts[1]
                    try:
                        user = User.objects.get(username=username)
                        return (user, None)
                    except User.DoesNotExist:
                        return (None, None)

            return (None, None)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key.")
