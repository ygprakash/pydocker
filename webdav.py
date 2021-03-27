from wsgidav.fs_dav_provider import FilesystemProvider
from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp
import socket

################################################################################
# SINGLETON CLASS FOR GLOBAL STATE
#################################################################################

class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

#####################################################################################
# WEB INTERFACE: WEBDAV MOUNT to retrieve codesnippets from the webserver
#####################################################################################

class WebDavApp(WsgiDAVApp):
    __metaclass__ = Singleton

    def __init__(self, rootpath=None):
        host = socket.gethostname()
        # if host.upper().startswith('LT'):
        rootpath = r'.'
        # else:
        #     rootpath = '/home/user/'
        provider = FilesystemProvider(rootpath)

        config = DEFAULT_CONFIG.copy()
        config.update({
            "mount_path": "/webdav",
            "provider_mapping": {"/": provider},
            "user_mapping": {},
            "verbose": 1,
        })
        super(WebDavApp, self).__init__(config)