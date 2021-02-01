import json
import urllib.request

import time
import typing

from jose import jwt
from jose.utils import base64url_decode

'''
-----------------------------------
1- Exemple of Cognito public keys
-----------------------------------
{
  "keys":[
    { "alg":"RS256",
      "e":"AQAB",
      "kid":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "kty":"RSA",
      "n":"..........................................................................................................",
      "use":"sig"
      },
    { "alg":"RS256",
      "e":"AQAB",
      "kid":"yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "kty":"RSA",
      "n":"..........................................................................................................",
      "use":"sig"
      }
  ]
}

--------------------------------
2 - Exemple of returned claims
--------------------------------
{
  "sub": "xxxxx-yyyyy-zzzzz-caf13bd0",
  "aud": "16o0810kpvch0co3n..........",
  "email_verified": true,
  "event_id": "aaaa-bbbb-ccccc-8de5-43f79dd78ec1",
  "token_use": "id",
  "auth_time": 1608406983,
  "iss": "https://cognito-idp.eu-west-3.amazonaws.com/eu-west-3_alphabeta",
  "phone_number_verified": false,
  "cognito:username": "wharouny.tp",
  "exp": 1608489191,
  "iat": 1608485591,
  "email": "wharouny.tp@gmail.com"
}
'''

class IdpConnexion :

  def __init__(self, region:str, user_pool_id:str, app_client_id:str):
    self.region         = region
    self.user_pool_id   = user_pool_id
    self.app_client_id  = app_client_id
    self.keys  = None

  def get_public_keys(self) -> dict:
    if self.keys is None :
      with urllib.request.urlopen(urllib.request.Request(
        url=f'{self.get_issuer()}/.well-known/jwks.json',
        headers={'Accept': 'application/json'},
        method='GET'),
        timeout=5) as f :
        response = f.read()
        self.keys = json.loads(response.decode('utf-8'))['keys']

      # with urllib.request.urlopen(f'{self.get_issuer()}/.well-known/jwks.json') as f:
      #   print(f"idp_connexion - Before f.read()")
      #   response = f.read()
      #   print(f"idp_connexion - After f.read()")
      #   print(f"idp_connexion - response.decode('utf-8'):{response.decode('utf-8')}")
      #   self.keys = json.loads(response.decode('utf-8'))['keys']
    return self.keys

  def get_issuer(self) -> str:
    return f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}'


  def get_claims(self, token :str, token_use:typing.Union['id','access']) -> dict:
    # self.get_public_keys()
    # 1 - Get the kid from the token headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # # 2 - Search for the kid in the downloaded public keys
    # key_index = -1
    # for i in range(len(self.get_public_keys())):
    #   if kid == self.get_public_keys()[i]['kid']:
    #     key_index = i
    #     break
    # if key_index == -1:
    #   raise Exception(f"Token Key Id not {kid} found in jwks.json")
    # # 3 - Construct the public key issued from 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'
    # cognito_public_key = jwk.construct(self.get_public_keys()[key_index])
    # 4 - Get the last two sections of the token : token_message and token_ signature (encoded in base64)
    token_message, token_encoded_signature = str(token).rsplit('.', 1)
    # 5 - Decode the signature
    token_decoded_signature = base64url_decode(token_encoded_signature.encode('utf-8'))
    # 6 - Verify the signature => compare_digest(token_decoded_signature, cognito_public_key.sign(token_message))
    # if not cognito_public_key.verify(token_message.encode("utf8"), token_decoded_signature):
    #   raise Exception(f"Signature verification failed")

    # 7 - Since we passed the verification, we can now safely use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # 7.1 - Additionally we can verify the token expiration
    if time.time() > claims['exp'] :
      raise Exception(f"Token is expired since '{claims['exp']}'")
    # 7.2 - Verify: aud, iss, token_user   (use claims['client_id'] if verifying an access token)
    if claims['aud'] != self.app_client_id: # token_aud :
      raise Exception(f"Token was issued for '{claims['aud']}': it is not the expected issuer")
    if claims['iss'] != self.get_issuer(): # token_iss :
      raise Exception(f"Token was issued by '{claims['iss']}': it is not the expected issuer")
    if claims['token_use'] != token_use :
      raise Exception(f"Token was issued for '{claims['token_use']}': it is not the expected use")

    # 8 - And finally, we can use the claims
    return claims

if __name__ == '__main__':
  token = 'eyJraWQiOiJGRVFJOHpjeE5oV29FTFJXdGxVVEE2Q1VWYk1sT1d3RW4waDdoU1hFKzNFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJjYWYxM2JkMC02YTdkLTRjN2ItYWE4Ny02YjZmMzgzM2ZlMWUiLCJhdWQiOiIxNm8wODEwa3B2Y2gwY28zbjUyZDh2azd2NSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjkxY2RjOGI2LTllODItNGQwNS04ZGU1LTQzZjc5ZGQ3OGVjMSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjA4NDA2OTgzLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtd2VzdC0zLmFtYXpvbmF3cy5jb21cL2V1LXdlc3QtM19iQWlFbTQ0dUYiLCJwaG9uZV9udW1iZXJfdmVyaWZpZWQiOmZhbHNlLCJjb2duaXRvOnVzZXJuYW1lIjoid2hhcm91bnkudHAiLCJleHAiOjE2MDg1NDM0MzIsImlhdCI6MTYwODUzOTgzMiwiZW1haWwiOiJ3aGFyb3VueS50cEBnbWFpbC5jb20ifQ.jGNm0N2wjXUoUJ-bEcuiii2HUi-ZNF8WTl7uocf2shZvZo4wSyQRUYZrLdbpOKpZSIh54ZpbTLWy0nRw2JnwnsDxGUSfsUkmJhwe50jA0ftXe7-1jW1m56LiO4GfUewYu7_zrSlIX9EbYgHBc2jaGNeKZHaVhh3wWQu0A1A-zrF1nMtmAfq0GnDvTePiIjVmAygLqWpvjjVqijr_X9gg5FIyV54LcDC6v55gkGbIoHu-oLkfreCiT_YLkrZbtsAzSMNRBR858sGtGQK9FTMU0EQSOXKmdC6gySZODJAmCuS29jSYDGYqZurlhxRmJDqDonm22W41dHfBlO2O6CZFSw'
  from covcov.infrastructure.configuration import config
  region         = config["cognito"]["COG_REGION"]
  user_pool_id   = config["cognito"]["COG_USER_POOL_ID"]
  app_client_id  = config["cognito"]["COG_APP_CLIENT_ID"]
  cognito_idp = IdpConnexion(region, user_pool_id, app_client_id)
  #
  cognito_idp.get_claims(token, "id")