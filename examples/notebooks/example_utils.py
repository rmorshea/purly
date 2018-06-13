import os


def localhost(protocol, port=8000):
    """Returns the host URL.

    When examples are running on mybinder.org this is not simply "localhost" or
    "127.0.0.1". Instead we use ``nbserverproxy`` whose proxy is used instead.
    """
    if 'JUPYTERHUB_OAUTH_CALLBACK_URL' in os.environ:
        if not protocol.endswith('s'):
            protocol += 's'
        form = protocol + '://hub.mybinder.org%s/proxy/%s'
        auth = os.environ['JUPYTERHUB_OAUTH_CALLBACK_URL'].rsplit('/', 1)[0]
        return form % (auth, port)
    else:
        form = protocol + '://127.0.0.1:%s'
        return form % port
