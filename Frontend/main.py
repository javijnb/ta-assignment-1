from flask import Flask, request
from flask import render_template
import requests
import json

backend_url = "http://localhost:8000/authenticate"
TOKEN = ""

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        payload = {'email': email, 'password': password}
        response = requests.post(backend_url, json=payload)
        
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if response_json["success"] == True:
                TOKEN = response_json["token"]
                return "Página de compra"
            
        return 'Error en el inicio de sesión'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)