# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration:

    Project setup
    
            Custom installation:
            Django:
                -> go into django dir
                -> virtualenv -p python3 uber_env
                -> source uber_env/bin/activate
                -> pip install -r requirements.txt
                -> configure database name, user, password in redington_uber/settings.py
                    DATABASES = {
                        'default': {
                            'NAME': 'your database name',
                            'USER': 'your database username',
                            'PASSWORD': 'your database password',
                        }
                    }
                -> python manage.py migrate
                -> python manage.py runserver 8000
            Angular4:  
                -> go into angular4 dir
                -> npm install
                -> ng serve

    Before starting setup make sure that following packages are installed in local machine
    
	    For django:
	        -> apt-get install python-pip
	        -> apt-get install mysql-server
	        -> apt-get install mysql-client
	        -> apt-get install python3-dev
	        -> pip install virtualenv
	        -> Also check elasticsearch installation section
	    
	    For Angular4:
	        -> sudo apt-get install build-essential checkinstall
	        -> sudo apt-get install libssl-dev
            -> curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.0/install.sh | bash
            -> nvm install 7.3.0 (version may change)
            -> nvm use 7.3.0
            -> nvm alias default node
            -> npm install -g angular-cli
            
* Database configuration

        Data loading:
	        -> Load common_aipdirectory table data from file `django/data/common_aipdirectory.sql`
        
        Creating predefined roles:
            -> Predefined roles will be created automatically during migration
            -> For dev mode run this command `django/migrate.py updateroles` within the virtualenv to update predefined roles and their permissions
            -> Don't update predefined roles in production mode
           
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact


#For Background process rabbitmq
  rabbitmq install:
    https://www.rabbitmq.com/install-debian.html
