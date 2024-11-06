import logging

from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from core.config import config
from core.google.user_service import get_user

log = logging.getLogger(__name__)

flow = Flow.from_client_secrets_file(
    client_secrets_file=config['auth']['google']['client_secret_file'],
    scopes=[
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid'
    ]
)
flow.redirect_uri = config['auth']['google']['redirect_uri']

def start_authentication():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    return authorization_url, state


def complete_oauth_flow(code: str, db: Session):
    # fetch user_service info
    flow.fetch_token(code=code)
    credentials = flow.credentials
    google_user = get_user(credentials)
'''
    # check if user exists
    user = authentication.auth_methods_service.find_user(google_user.id, OAuthMethods.GOOGLE, db)

    if user is None:
        log.debug("Google user not found. Creating new user. google_id=\"{google_id}\", email=\"{email}\"".format(google_id=google_user.id, email=google_user.email))
        user = User(
            uname = google_user.uname,
            email = google_user.email,
            email_verified = google_user.email_verified
        )
        user = user_service.add_user(user, OAuthMethods.GOOGLE, {'google_id': google_user.id}, db)
    else:
        log.debug("Google user found. google_id=\"{google_id}\", email=\"{email}\"".format(google_id=google_user.id, email=google_user.email))
        user.last_login = datetime.now()

    jwt_token = jwt.create_token(user.uid, user.role)
    return jwt_token
'''
