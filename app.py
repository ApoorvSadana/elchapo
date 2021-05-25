import logging

import requests
from flask import Flask, redirect, jsonify
from flask import request

from constants import WEBHOOK, NOT_FOUND_URL, MAX_RETRY, MAX_URL_LENGTH
from models import ShortURL
from zappa.asynchronous import task
import shortuuid
from urllib.parse import unquote

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

MAIN = False

app = Flask(__name__, static_url_path='/no_static')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/c', methods=['POST'])
def create_url():
    # path = request.json['path']
    length = 4
    attempt = 0
    path = None
    while length<=MAX_URL_LENGTH:
        path = shortuuid.ShortUUID().random(length=length)
        if ShortURL.count(path):
            attempt = attempt + 1
            if attempt >= MAX_RETRY:
                length = length + 1
                attempt = 0
        else:
            break
    if length > MAX_URL_LENGTH:
        return jsonify(success=False), 500
    redirect_url = request.json['redirect_url']
    webhook = request.json.get('webhook', None)
    ShortURL(url=path, redirection_url=redirect_url, webhook=webhook).save()
    return jsonify(success=True,path=path), 200

@app.route('/c2', methods=['GET'])
def create_url2():
    # path = request.json['path']
    length = 4
    attempt = 0
    path = None
    while length<=MAX_URL_LENGTH:
        path = shortuuid.ShortUUID().random(length=length)
        if ShortURL.count(path):
            attempt = attempt + 1
            if attempt >= MAX_RETRY:
                length = length + 1
                attempt = 0
        else:
            break
    if length > MAX_URL_LENGTH:
        return jsonify(success=False), 500
    redirect_url = unquote(request.args.get('redirect_url'))
    # webhook = request.json.get('webhook', None)
    ShortURL(url=path, redirection_url=redirect_url, webhook=None).save()
    return jsonify(success=True,path=path), 200


@task
def call_url(url):
    if url:
        retry = 3
        while retry > 0:
            x = requests.get(url)
            if x.status_code >= 400:
                retry = retry - 1
            else:
                return x.text


def get_hook(webhook, path):
    if webhook:
        if webhook.__contains__('?'):
            webhook + '&path=%s' % path
        else:
            webhook + '?path=%s' % path
    return webhook


@app.route('/<path:path>', methods=['GET'])
def redirect_url(path):
    try:
        short_url = ShortURL.get(path)
        webhook = WEBHOOK
        if short_url.webhook:
            webhook = short_url.webhook
        webhook = get_hook(webhook, path)
        if webhook:
            call_url(webhook)
        return redirect(short_url.redirection_url, code=302)
    except ShortURL.DoesNotExist:
        # return render_template('./404/index.html'), 404
        return jsonify(error="URL Not Found. Make sure you entered the URL correctly."), 404

# We only need this for local development.
if __name__ == '__main__':
    MAIN = True
    app.run(host='0.0.0.0', port=5601)
