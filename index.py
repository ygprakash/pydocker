__author__ = "Gowtham"
__date__ = "25 July 2019"

from bottle import get, route, request, static_file, abort, post, default_app, response  # RESTAPI framework
from gevent.pywsgi import WSGIServer  # Server
from geventwebsocket.handler import WebSocketHandler
import os
from dbCon import User,KalonjiDB,Session  # Database connections class import
import datetime
import simplejson as json
from webdav import WebDavApp  # Works as a mount to view content of a file either  through mount or webpage

root = os.path.dirname(os.path.realpath(__file__))  # Global Root path definition to find the file locations/directories

@get('/') # base dir
@get('/index.html')
@get('/index')
@get('/index/index.html')
@get('/index/')
def home():
    return static_file('index.html',root=os.path.join(root, 'templates'))

@get('/<path:path>') # Other routes to handle dependant front end libraries
@get('/index.html/<path:path>')
@get('/login.html/<path:path>')
@get('/index/<path:path>')
@get('/login')
@get('/login/<path:path>')
@get('/redirect.html/<path:path>')
def get_js(path):
    return static_file(path,root=os.path.join(root, 'templates'))

@get("/userlogin")
def login():
    """
    It takes 2 parameters:-
    Username, Password to verify the credentials and update the last_login record in the user database table.
     Return the information either in json / handle authorization replies
     Auto assigns the folder access based on the Team name selection.
     Files comes under that team will be read accessible to user
    :return: json structure with following data
    Name, directory, list of code snippets user has access
     or if the user is admin returns a table with all records information fetched from database.
    """
    if request.method == 'GET':
        uname = request.params.dict['user'][0]
        passwd = request.params.dict['pwd'][0]
        login = session.get_all(uname,passwd,datetime.datetime.utcnow())
        if login and uname=='admin':
            complete_table = session.complete_table()
            return json.dumps(complete_table,indent=2)
        if login:
            folder_list = session.get_folders(login['user_id'])
            res={}
            if folder_list:
                for i in folder_list:
                    directory = os.path.join(os.path.dirname(os.path.realpath('__file__')),'coderepo',i)
                    list_of_files = os.listdir(directory)
                    res={'name':login['name'],'directory':directory,'list_of_files':list_of_files}
                return res
            else:
                return 'Folders Not Assigned'
        else:
             return 'Unauthorized'

@get('/del')
def del_user():
    """
    Requires user id to delete the records from Database . Only accessible to admin
    :return:
    Message for visualization
    """
    dict_struct = request.params.dict
    user_id = dict_struct['id'][0]
    delete_user = session.del_rec(user_id)
    if delete_user:
        # complete_table = session.complete_table()
        # return json.dumps(complete_table, indent=2)
        return 'Record Updated'
    else:
        return 'Unable to delete the record or no record found with current selection, Please logout and and login'

@post("/register")
def register():
    """
    Handles new registrations
    Input : username,userpassword,useremail,isadmin - auto assigned / modified by admin ,issuper - auto assigned / modified by admin
    ,isactive- auto assigned ,lastlog - auto assigned ,datejoined - auto assigned,team
    :return:
    Message for visualization
    """
    if request.method == 'POST':
        dict_struct = request.params.dict
        username = dict_struct['uname'][0]
        userpassword = dict_struct['passw'][0]
        useremail = dict_struct['mail'][0]
        isadmin = False
        issuper = False
        isactive = True
        lastlog = datetime.datetime.utcnow()
        datejoined = datetime.datetime.utcnow()
        team = dict_struct['team'][0]
        q = session.add_details(username,userpassword,useremail,isadmin,issuper,isactive,lastlog,datejoined,team)
        if q:
            return 'Registered'
        else:
            return 'Failed'

@get('/webdav')
def call_wsgi(subpath=''):
    """
    Creates a webav mount to view the file content either through webpage or through normal mount
    input : File name, directory to find the file
    :param subpath: path to look for files
    :return: File content the user has access
    """
    user = request.get_header('X-WEBAUTH-USER', 'admin')  # 'admin'
    if user not in ['admin']:
        abort(403, 'Unauthorised')
    file = request.params.dict['file'][0]
    subpath = request.params.dict['path'][0]
    new_environ = request.environ.copy()
    new_environ['SCRIPT_NAME'] = new_environ.get('SCRIPT_NAME', '') + '/index/webdav'
    new_environ['PATH_INFO'] = '/'+ os.path.join(str(subpath),str(file))

    def start_response(status, headerlist, other):
        response.status = int(status.split()[0])
        for key, value in headerlist:
            response.add_header(key, value)
    app = WebDavApp()
    app.__init__(rootpath=subpath)
    return app(new_environ, start_response)

@get('/update')
def update():
    """
    Only for admin, to grant access with admin or super user
    :return: Complete records after update in json
    """
    id = request.params.dict['id'][0]
    name = request.params.dict['name'][0]
    isadmin = bool(request.params.dict['isadmin'][0])
    issuper = False
    update_field = session.update(id, name, issuper, isadmin)
    if update_field:
        # complete_table = session.complete_table()
        # return json.dumps(complete_table, indent=2)
        return 'Record updated'
    else:
        return 'Failed to update'


if __name__ == '__main__':  # Set up when running stand alone
    try:
        user_name = request.get_header('X-WEBAUTH-USER', 'admin')
        session = KalonjiDB()
        check = session.get_all(user_name,'',datetime.datetime.utcnow())
        if check or user_name=='admin':
            pass
            raise Exception
        else:
            abort(401,'Un-authorized to view this webpage')
    except Exception as e:
        db = KalonjiDB()
        db.setup_kalonji_db()
        print('DB set')

    print('Starting localhost webserver at port 3030')
    server = WSGIServer(('localhost', 3030), default_app(), handler_class=WebSocketHandler)
    server.serve_forever()
