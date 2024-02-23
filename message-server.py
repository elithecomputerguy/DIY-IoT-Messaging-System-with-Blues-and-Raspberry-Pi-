from bottle import route, run, request, post, redirect
import json 
import os

def modem(message):
    id_device = 'DEVICEID'
    id_project = 'PROJECTID'
    id_client = 'CLIENTID'
    secret = 'SECRET'
    #Get OAuth Token
    query = f'''
            curl -X POST -L 'https://notehub.io/oauth2/token' \
            -H 'content-type: application/x-www-form-urlencoded' \
            -d grant_type=client_credentials -d client_id={id_client} \
            -d client_secret={secret}
            '''
    response = os.popen(query).read()
    response = json.loads(response)
    token = response['access_token']
    print(f'Token: {token}')

    print(message)
    #Send Message with OAuth Token to Notehub
    message = message.replace("'", "")
    message = message.replace('"', '')
    query = f"""
            curl -X POST -L 'https://api.notefile.net/v1/projects/{id_project}/devices/{id_device}/notes/data.qi' \
            -H 'Authorization: Bearer {token}' \
            -d '{{\"body\":{{\"message\":\"{message}\"}}}}' 
            """
    
    os.system(query)

    print(f'Message was Sent: {message}')

@route('/')
def message_form():
    page = '''
            <h1>Message App</h1>
                <form action="./message_send" method="post">
                    Message:
                    <br>
                    <textarea name="message" rows="4" cols="40"></textarea>
                    <br>
                    <input type="submit">
                </form>
            <br>
            '''

    return page

@post('/message_send')
def send():
    message = request.forms.get('message')

    print(f'Message from Form: {message}')
    if message != None:
        modem(message)

    return redirect('/')

run(host='0.0.0.0', port=80, debug=True)