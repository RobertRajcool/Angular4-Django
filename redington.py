import os
from sys import exit
import sys
import subprocess
import getpass

print ('This will installs all your requirements for REDINGTON project')

# declaring project directory path details
user = ''
project_name = ''
project_path = ''
project_directory_path = ''
current_working_path = ''
current_working_directory = ''
db_name = ''
db_username = ''
db_password = ''
host_name = 'api.redington'


def install_linux_package(pkg_name):
    print ('\033[0;36;1m Installing {pkg}\033[0m'.format(pkg=pkg_name))
    status = os.system('dpkg -s {pkg}| grep Status'.format(pkg=pkg_name))
    if not status:
        print ('\033[0;37;42m {pkg} already installed \033[0m'.format(pkg=pkg_name))
        return True

    elif status:
        print ('\033[0;30;1m{pkg} not installed yet\033[0m'.format(pkg=pkg_name))
        confirm = os.system('sudo apt-get install {pkg}'.format(pkg=pkg_name))
        if confirm == 0:
            print ('\033[0;37;42m{pkg} Successful\033[0m'.format(pkg=pkg_name))
            return True
        else:
            print ('\033[0;37;41m {pkg} Failed\033[0m'.format(pkg=pkg_name))
            exit(0)


def install_pip_package(pkg_name):
    print ('\033[0;36;1m Installing {pkg}\033[0m'.format(pkg=pkg_name))
    status = os.system('pip show {pkg} | grep Version'.format(pkg=pkg_name))
    if not status:
        print ('\033[0;37;42m {pkg} already installed \033[0m'.format(pkg=pkg_name))
        return True
    elif status:
        print ('\033[0;30;1m{pkg} not installed yet\033[0m'.format(pkg=pkg_name))
        confirm = os.system('pip install {pkg}'.format(pkg=pkg_name))
        if confirm == 0:
            print ('\033[0;37;42m{pkg} Successful\033[0m'.format(pkg=pkg_name))
            return True
        else:
            print ('\033[0;37;41m {pkg} Failed\033[0m'.format(pkg=pkg_name))
            exit(0)


def install_npm_package(pkg_name):
    print ('\033[0;36;1m Installing {pkg}\033[0m'.format(pkg=pkg_name))
    status = os.system('npm list -g {pkg}'.format(pkg=pkg_name))
    if not status:
        print ('\033[0;37;42m {pkg} already installed \033[0m'.format(pkg=pkg_name))
        return True
    elif status:
        print ('\033[0;30;1m{pkg} not installed yet\033[0m'.format(pkg=pkg_name))
        confirm = os.system('npm install -g {pkg}'.format(pkg=pkg_name))
        if confirm == 0:
            print ('\033[0;37;42m{pkg} Successful\033[0m'.format(pkg=pkg_name))
            return True
        else:
            print ('\033[0;37;41m {pkg} Failed\033[0m'.format(pkg=pkg_name))
            exit(0)

def change_settings_py(dbname, user, pwd):
    host = '127.0.0.1'
    port = '3306'
    search_text = 'DATABASES'
    f = project_directory_path + '/' + project_name + '/django/redington/settings.py'
    settings_file = open(f, 'r')
    settings_content = settings_file.read()
    point1 = settings_content.index(search_text)
    settings_file.seek(0, 0)
    content_before = settings_file.read(point1)

    point2 = settings_content.index('# Password validation')
    settings_file.seek(point2, 0)
    content_after = settings_file.read()

    settings_file.close()

    content = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '""" + dbname + """',
        'HOST': '""" + host + """',
        'PORT': '""" + port + """',
        'USER': '""" + user + """',
        'PASSWORD': '""" + pwd + """',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


"""

    settings_file = open(f, 'w')
    settings_file.write(content_before)
    settings_file.write(content)
    settings_file.write(content_after)
    settings_file.close()

    # os.system('python manage.py migrate')
    # os.system('python manage.py runserver 127.0.0.1:8000')

def enable_site():
    print ('Finalizing', '.' * 100)

    # enabling site
    os.system('sudo a2ensite ' + host_name)
    os.system('sudo service apache2 restart')

    # return to directory
    os.chdir(current_working_path)

    print ('That\'s it..now setup is ready..\ngood luck...!')
    print ('Project url : http://' + host_name)
    print ('Enter this url in browser...Bye..!')


def add_host():
    if os.geteuid() == 0:
        host_file = open('/etc/hosts', 'r+')
        content = host_file.read()
        host_file.seek(0)
        # host_file = open('/etc/hosts', 'w')
        content = '127.0.0.1       ' + host_name + '\n' + content
        host_file.write(content)
        host_file.close()

        print ('host added\n')
        print (open('/etc/hosts', 'r').read())
        print ('.' * 100)
    else:
        print("You are not root.")
       # subprocess.call(['sudo', 'python3 add_host', *sys.argv])



def create_virtualhost():
    print ('Creating virtual host', '.' * 100)

    content = """
# Python path
WSGIPythonPath """ + project_path + """/django:""" + project_path + """/django/redingtonenv/lib/python3.5/site-packages
<VirtualHost *:80>
    ServerName """ + host_name + """
    WSGIDaemonProcess """ + project_name +""" python-home=""" + project_path + """/django/redingtonenv python-path=""" + project_path + """
    WSGIProcessGroup """ + project_name +"""
    WSGIScriptAlias / """ + project_path + """/django/redington/wsgi.py
    WSGIPassAuthorization on

#   Error logs
    ErrorLog /var/log/apache2/""" + host_name + """-error.log
    CustomLog /var/log/apache2/""" + host_name + """-access.log combined

    Alias /static/ """ + project_path + """/django/static/

#   Supply Project files
    <Directory """ + project_path + """/django/redington>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

#   Supply Static files
    <Directory """ + project_path + """/django/static>
        Require all granted
    </Directory>

#   Supply Media files
    <Directory """ + project_path + """/django/uploads>
        Require all granted
    </Directory>
</VirtualHost>
"""
    if os.geteuid() == 0:
        vh_file = open('/etc/apache2/sites-available/' + host_name + '.conf', 'w')
        vh_file.write(content)
        vh_file.close()

        print ('Virtual host created..\n')
        print (open('/etc/apache2/sites-available/' + host_name + '.conf', 'r').read())
        print ('.' * 100)
    else:
        print("You are not root.")
       # subprocess.call(['sudo', 'python3 create_virtual_host', *sys.argv])


def configure_database():
    import MySQLdb

    reference = os.path.split(os.getcwd())

    project_directory_path = project_name = project_path = ''
    project_directory_path = os.getcwd()

    project_name = reference[1]
    project_path = reference[0]

    print ('\033[0;36;1m Database creation \033[0m')
    dbname = ''
    user = input('Enter MySQL user name :\033[0;34;1m')
    print ('\033[0m')
    pwd = input('Enter MySQL password :\033[0;34;1m')
    print ('\033[0m')

    database_exists = input('Do you already have database (\033[0;35;1m y or n \033[0m)? :\033[0;34;1m ')
    print ('\033[0m')

    if database_exists == 'y':
        dbname = input('Enter database name : \033[0;34;1m')
        print ('\033[0m')
    elif database_exists == 'n':
        option = 'n'
        # input('Do you want to change database name(' + project_name + ')  (\033[0;35;1m y or n \033[0m)? :')
        if option == 'n':
            dbname = input('Enter database name : \033[0;34;1m')
            print ('\033[0m')
            con = MySQLdb.connect(host='localhost', user=user, passwd=pwd)
            cur = con.cursor()
            query = 'CREATE DATABASE ' + dbname + ';'
            if cur.execute(query):
                print ('\033[0;37;42m Database created \033[0m')

            else:
                print ('\033[0;37;41m Database not created..!!..error..!! \033[0m')

    change_settings_py(dbname, user, pwd)


def create_virtualenv():
    print ('\033[0;36;1m Creating virtualenv \033[0m')
    env = 'django/' + project_name + 'env'

    if not os.path.exists('./' + env):
        status = os.system('virtualenv -p python3 ' + env)
        if not status:
            print ('\033[0;37;42m virtualenv created \033[0m')
        elif status:
            print ('\033[0;37;41m virtualenv not created ...error \033[0m')
            exit(0)
    else:
        print ('\033[0;37;42m virtualenv already created \033[0m')

    print ('Kindly run this command to continue the setup : \033[2;34;1m python3 {path}/redington.py install_requirements \033[0m'.format(path=project_path))
    # os.system('source ' + env + '/bin/activate')
    os.system('/bin/bash  --rcfile ' + env + '/bin/activate')
    # sys.exit(0)
    # subprocess.call(['/bin/bash  --rcfile ' + env + '/bin/activate', *sys.argv])
    # subprocess.call(['python3 ~/Rajez/Scripts/Django\ setup/Redington\ setup/redington.py install_requirements'])


def dir_permission():
    # check directory access
    if os.access(project_path, os.R_OK and os.W_OK):
        return True
    else:
        os.system('sudo chmod -R 777 ../' + current_working_directory)


def beginning():
    # input('Installation method : \'virtualenv\' (ctrl+c to cancel or press any key to continue) >')
    global project_path, current_working_path, project_directory_path, project_name, db_name, db_username, db_password, user

    project_path = current_working_path = os.getcwd()
    project_directory_path = os.path.abspath(os.path.join(project_path, os.pardir))
    array = current_working_path.split('/')
    project_name = array[len(array) - 1]
    user = getpass.getuser()


def main(argv):
    if argv == 'dependencies' or argv == 'null':
        beginning()
        dir_permission()
        install_linux_package('apache2')
        install_linux_package('mysql-server')
        install_linux_package('mysql-client')
        install_linux_package('libmysqlclient-dev')
        install_linux_package('python-pip')
        install_linux_package('python3-dev')
        # install_linux_package('python-mysqldb')
        install_pip_package('virtualenv')
        create_virtualenv()
        main('install_requirements')

    elif argv == 'install_requirements':
        beginning()
        file = open(project_path + '/django/requirements')
        requirements = file.read().splitlines()
        for package in requirements:
            install_pip_package(package)
        main('integer_mysql')

    elif argv == 'integer_mysql':
        beginning()
        configure_database()
        os.system('python3 ' + project_path + '/django/manage.py migrate')
        os.system('deactivate')
        main('configure_angular2')
        # create_virtualhost()
        # add_host()
        # enable_site()
        # os.system('python manage.py runserver 127.0.0.1:8000')
        # sys.exit(0)

    elif argv == 'configure_angular2':
        beginning()
        install_linux_package('build-essential')
        install_linux_package('checkinstall')
        install_linux_package('libssl-dev')
        install_linux_package('curl')
        os.system('curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.0/install.sh | bash')
        os.system('nvm install 7.3.0')
        os.system('nvm use 7.3.0')
        os.system('nvm alias default node')
        install_npm_package('angular-cli')
        os.chdir(project_path + '/angular2')
        os.system('npm install')
        os.system('ng serve')
        sys.exit(0)

    elif argv == 'add_host':
        add_host()

    elif argv == 'create_virtual_host':
        create_virtualhost()

    elif argv == 'create_database':
        configure_database()


if __name__ == "__main__":
    if sys.argv.__len__() == 1:
        print ('\033[0;31;1mArgument missing...Setup will starts from beginning. Do you want to continue?\033[0m')
        input('cancel :\033[0;35;1m ctrl+c\033[0m continue:\033[0;35;1m press any key\033[0m')
        main('null')

    else:
        main(sys.argv[1])
