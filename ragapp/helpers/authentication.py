from requests import Session
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException


class AuthHelper:
    session = Session()
    authority = (
        f"https://login.microsoftonline.com/6e75cca6-47f0-47a3-a928-9d5315750bd9"
    )
    key_url = f"{authority}/discovery/v2.0/keys"
    jwk_client = PyJWKClient(key_url)

    @staticmethod
    def get_user(auth_header: str):
        return jwt.decode(auth_header, options={"verify_signature": False}).get(
            "unique_name"
        )

    @staticmethod
    def _get_auth_token(auth_header: str):
        return auth_header.split("Bearer ")[-1]

    @staticmethod
    def check_valid_token(auth_header: str):

        jwt_token = AuthHelper._get_auth_token(auth_header)

        unverified_claims = jwt.decode(jwt_token, options={"verify_signature": False})
        signing_key = AuthHelper.jwk_client.get_signing_key_from_jwt(jwt_token).key

        try:

            jwt.decode(
                jwt_token,
                signing_key,
                algorithms=["RS256"],
                audience=unverified_claims.get("aud"),
                issuer=unverified_claims.get("iss"),
            )

            return True

        except jwt.ExpiredSignatureError as jwt_expired_exc:
            return False

        except (jwt.InvalidAudienceError, jwt.InvalidIssuerError) as jwt_claims_exc:
            return False
        except Exception as exc:
            return False
