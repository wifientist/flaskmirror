from app import app

app.config['DEBUG'] = True

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=7777, ssl_context=('server.crt', 'server.key'))
