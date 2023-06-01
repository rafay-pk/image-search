import shutil, os

pwd = os.getcwd().replace("\\", '/')
print(f'Starting Execution with Working Dir: {pwd}')
path_app = pwd + '/lib/app.py'
path_data = pwd + '/data'
path_folder = path_data + '/folders/'
path_db = path_data + '/database.sqlite'

if os.path.exists(path_folder):
    shutil.rmtree(path_folder)

if os.path.exists(path_db):
    os.remove(path_db)

exec(open(path_app).read())