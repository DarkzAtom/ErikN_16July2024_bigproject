from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

SQUID_CONFIG_TEMPLATE = """
http_port 3128
cache_peer {host} parent {port} 0 no-query login={username}:{password}
never_direct allow all
"""

@app.route('/set_proxy', methods=['POST'])
def set_proxy():
    data = request.json
    host = data['host']
    port = data['port']
    username = 'your_static_username'
    password = 'your_static_password'

    config = SQUID_CONFIG_TEMPLATE.format(
        host=host, port=port, username=username, password=password
    )

    with open('/etc/squid/squid.conf', 'w') as f:
        f.write(config)

    subprocess.run(['service', 'squid', 'reload'])

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)