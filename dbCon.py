import sqlite3
import os, socket
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import sqlalchemy.dialects.mysql as my
import simplejson as json

project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'db')
Base = declarative_base()
Session = sessionmaker()

class User(Base):
    """
    User table to hold user information
    """
    __tablename__ = 'user'

    user_id =  Column(my.INTEGER(unsigned=True), primary_key=True, autoincrement=True,nullable=False)
    user_name = Column(my.VARCHAR(64),nullable=False)
    user_email = Column(my.VARCHAR(64),nullable=False)
    user_password = Column(my.VARCHAR(64),nullable=False)
    is_admin = Column(my.BOOLEAN,nullable=False)
    is_super_user = Column(my.BOOLEAN,nullable=False)
    is_active = Column(my.BOOLEAN)
    last_login = Column(my.DATETIME)
    date_joined = Column(my.DATETIME)
    user_belongs_to = Column(my.VARCHAR(64))

class Folder(Base):
    """
    Folder table to hold developer information
    """
    __tablename__ = 'folder'

    folder_id = Column(my.INTEGER(unsigned=True), primary_key=True)
    folder_name = Column(my.VARCHAR(64))
    user_ids = Column(my.VARCHAR(64))

class KalonjiDB:
    """
    Contains interfaces to the Kalonji db.
    """
    def __init__(self, mode=None):
        """
        :param mode: Override mode, for testing only.
        """
        self.engine = create_engine(get_sql_client(mode=mode))
        self._id = None

        # Create missing tables
        table_checklist = [
            'user','folder'
        ]

        available_tables =  self.engine.table_names()
        for t in table_checklist:
            if t not in available_tables:
                self.setup_kalonji_db()  # Creates any missing tables
                break

        # Session for upcoming checks
        session = Session(bind=self.engine)
    def complete_table(self):
        """
        :return: Complete records from the table User
        """
        session = Session(bind=self.engine)
        q = session.query(User)
        res = {}
        for r in q:
            # res.append([str(r.user_id),str(r.user_name),str(r.user_email),str(r.is_admin),str(r.is_active),str(r.last_login),str(r.date_joined),str(r.user_belongs_to)])
            # res.append({'User Id': r.user_id, 'User Name': r.user_name, 'User Email': r.user_email,
            #                   'Is Admin': r.is_admin, 'Is Active': r.is_active, 'Last Login': r.last_login,
            #                   'Joining Date': r.date_joined, 'Team': r.user_belongs_to})
            res[r.user_id] = {'User Id': r.user_id, 'User Name': r.user_name, 'User Email': r.user_email,
                               'Is Admin': r.is_admin, 'Is Active': r.is_active, 'Last Login': str(r.last_login),
                               'Joining Date': str(r.date_joined), 'Team': r.user_belongs_to}
        return res
    def get_all(self,uname,passwd,date):
        """
        Get all information from User table as per below parameters
        :param uname:
        :param passwd:
        :param date:
        :return: json structure with user_id and name
        """
        session = Session(bind=self.engine)
        q = session.query(User).filter_by(user_name=uname)
        res = {}
        for r in q:
            if r.last_login:
                r.last_login = date
                session.commit()
            if r.user_password == str(passwd):
                res={'user_id': r.user_id, 'name': r.user_name}
        return res
    def get_folders(self,id):
        """
        Returns directories user id has access to
        :param id:
        :return: list with directory names
        """
        session =Session(bind=self.engine)
        q = session.query(Folder)
        res=[]
        for r in q:
            json_struct = json.loads(r.user_ids)
            if id in json_struct:
                res.append(r.folder_name)
        return res
    def del_rec(self,id):
        """
        Only for admin to delete record as per user id
        :param id:
        :return: True of False on the success of query commit
        """
        session = Session(bind=self.engine)

        try:
            q = session.query(User).filter(User.user_id==int(id)).delete()
            session.commit()
            return True
        except Exception as e:
            return False
    def update(self,id,name,issuper,isadmin):
        """
        Updates the records per below parameters
        :param id:
        :param name:
        :param issuper:
        :param isadmin:
        :return: True of False on the success of query commit
        """
        session = Session(bind=self.engine)
        q = session.query(User).filter_by(user_id=id)
        for r in q:
            if issuper!=None:
                r.is_super_user = issuper
            if isadmin!=None:
                r.is_admin = isadmin
        try:
            session.commit()
            session.close()
            return True
        except:
            return False
    def add_details(self,username,userpassword,useremail,isadmin,issuper,isactive,lastlog,datejoined,team):
        """
        Adds all records per below parameters to database
        :param username:
        :param userpassword:
        :param useremail:
        :param isadmin:
        :param issuper:
        :param isactive:
        :param lastlog:
        :param datejoined:
        :param team:
        :return: True of False on the success of query commit
        """
        session = Session(bind=self.engine)
        entry = User(user_name=username,user_password=userpassword,user_email=useremail,is_admin=isadmin,is_super_user=issuper,
                     is_active=isactive,last_login=lastlog,date_joined=datejoined,user_belongs_to=team)
        try:
            session.add(entry)
            session.commit()
            res = True
        except:
            res=False
        return res
    def update_details(self):
        session = Session(bind=self.engine)

    def setup_kalonji_db(self):
        """
        Create database scheme.
        """
        print('Creating database schema')
        Base.metadata.create_all(self.engine)



    # is_admin = Column(my.BOOLEAN, ForeignKey('developer.dev_id'))
    # is_super_user = Column(my.BOOLEAN, ForeignKey('super.super_id'))

    # user_permissions = Column(my.VARCHAR(64), ForeignKey('folder.folder_id'))

    # developer = relationship('Developer', back_populates='user')
    # manager = relationship('Manager', back_populates='user')
    # super = relationship('Super')

# class Developer(Base):
#     """
#     Developer table to hold developer information
#     """
#     __tablename__ = 'developer'
#
#     dev_id = Column(my.INTEGER(unsigned=True), primary_key=True)
#     dev_first_name = Column(my.VARCHAR(64))
#     dev_last_name = Column(my.VARCHAR(64))
#     dev_is_admin = Column(my.BOOLEAN)
#
# class Manager(Base):
#     """
#     Manager table to hold manager information
#     """
#     __tablename__ = 'manager'
#
#     man_id = Column(my.INTEGER(unsigned=True), primary_key=True)
#     man_first_name = Column(my.VARCHAR(64))
#     man_last_name = Column(my.VARCHAR(64))
#
# class Super(Base):
#     """
#     Super user table
#     """
#     __tablename__ = 'super'
#
#     super_id = Column(my.INTEGER(unsigned=True), primary_key=True)
#     super_user = Column(my.VARCHAR(64))

def get_sql_client(mode=None):
    """
    Returns SQL alchemy connection string
    :param mode: To define the environment where the script is running
    :return:
    """
    if mode is None:
        mode = 'local'

    if mode == 'local':
        mysql_con_str = 'sqlite:///{}'.format(os.path.join(project_dir, 'db.sqlite3'))
        return mysql_con_str
    else:
        hostname = socket.gethostname().lower()
        raise KeyError("sql connections is not allowed on host {0}".format(
            hostname))

if __name__ == '__main__':
    db = KalonjiDB()
    db.setup_kalonji_db()