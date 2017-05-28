# webscraping app in python with Django

Install instructions:

```
$ git clone https://github.com/rishikant42/webscraping
$ cd webscraping
```

Install required dependencies:

```
$ pip install -r requirements.txt
```

Database configurations:

```
$ python manage.py makemigrations webscrapingapp
$ python manage.py sqlmigrate webscrapingapp 0001
$ python manage.py migrate
```

Run server on locathost:

```
$ python manage.py runserver
```
