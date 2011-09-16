import base64
import hashlib
import hmac
import json

def base64_url_decode(data):
    data = data.encode(u'ascii')
    data += '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data)

def unpack_signed_request(signed_request, app_secret):
    """Upacks a 'signed_request' the base64url encoded JSON object,
    signed with the 'app_secret' facebook application secret.
    Returns,
        On success: A python dictionary, with unpacked values from 'signed_request'.
        On failure: None
    """
    try:
        sig, payload = signed_request.split(u'.', 1)
    except ValueError:
        return None
    sig = base64_url_decode(sig)
    data = json.loads(base64_url_decode(payload))
    expected_sig = hmac.new(
        app_secret, msg=payload, digestmod=hashlib.sha256).digest()
    
    # Check the authenticity of the data.
    if sig == expected_sig:
        return data
    else:
        return None
    