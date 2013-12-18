#!env/bin/python
from flask.ext.script import Manager, Server, Command
from flask.ext.migrate import MigrateCommand
from app import app, db, assets
import logging
from webassets.script import CommandLineEnvironment

# Setup a logger
log = logging.getLogger('webassets')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
cmdenv = CommandLineEnvironment(assets, log)

manager = Manager(app)
manager.add_command("runserver", Server(debug=True))
manager.add_command('db', MigrateCommand)


@manager.command
def initdb():
    "Put tables into the database"
    db.create_all()

@manager.command
def rmdb():
    "Drop all tables from database"
    db.drop_all()

@manager.command
def updb():
    "Combined initdb and rmdb"
    rmdb()
    initdb()

@manager.command
def asset(command):
    "Assets"
    if command == "build":
        cmdenv.build()
    elif command == "watch":
        cmdenv.watch()
    elif command == "clean":
        cmdenv.clean()
    else:
        print "Incorrect command"

if __name__ == "__main__":
    manager.run()
