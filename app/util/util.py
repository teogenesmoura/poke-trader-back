from email.utils import parseaddr

def is_email_valid(address):
    return '@' in parseaddr(address)[1]

def build_response_object(status, message, auth_token):
    response = {}
    if status:
        response['status'] = status
    if message:
        response['message'] = message
    if auth_token:
        response['auth_token'] = auth_token
    return response
