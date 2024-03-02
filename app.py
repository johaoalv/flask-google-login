# app.py
from flask import Flask, render_template, redirect, request, url_for, session
import requests

app = Flask(__name__)
# Clave secreta para cifrar las sesiones de usuario
app.secret_key = 'tu_clave_secreta'

# Reemplaza con tu ID de cliente de Google
CLIENT_ID = '748742245469-pepitcpcecgtpt802q5n3uq40773b1bg.apps.googleusercontent.com'
# Reemplaza con tu secreto de cliente de Google
CLIENT_SECRET = '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'
# Reemplaza con tu URI de redireccionamiento
REDIRECT_URI = 'http://localhost:5000/oauth2callback'
# Correos electrónicos permitidos para iniciar sesión
ALLOWED_EMAILS = ['johao.alvarado@pedidosya.com', 'johaoalvarado24@gmail.com', 'jalvarado@pedidosya.com']


@app.route('/login')
def login():
    google_login_url = f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=email&access_type=offline'
    return render_template('login.html', google_login_url=google_login_url)


@app.route('/oauth2callback')
def oauth2callback():
    auth_code = request.args.get('code')
    token_endpoint = 'https://oauth2.googleapis.com/token'
    data = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_endpoint, data=data)
    if response.ok:
        tokens = response.json()
        access_token = tokens['access_token']
        # Puedes usar el access_token para obtener información del usuario desde Google
        user_info_endpoint = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_endpoint, headers=headers)
        if user_info_response.ok:
            user_info = user_info_response.json()
            user_email = user_info.get('email')
            # Verificar si el correo electrónico está en la lista de permitidos
            if user_email in ALLOWED_EMAILS:
                session['user_email'] = user_email
                session['user_picture'] = user_info.get('picture')
                return redirect(url_for('index'))
            else:
                return redirect(url_for('forbidden'))
    return 'Error al obtener tokens de acceso'

@app.route('/')
def index():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))

    user_picture = session.get('user_picture')
    return render_template('index.html', user_email=user_email, user_picture=user_picture)


@app.route('/logout', methods=['GET'])
def logout():
    # Limpiar la sesión del usuario
    session.clear()
    # Redirigir a la página de inicio de sesión
    return redirect(url_for('login'))

@app.route('/forbidden')
def forbidden():
    return render_template('forbidden.html')


if __name__ == '__main__':
    app.run(debug=True)
