
Setup
-----

* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* You can set your database connection options in `front/cfg_local.py` and `admin/cfg_local.py`.
  By default, do:
        * mysql: `CREATE DATABASE demo_front CHAR SET utf8;`.
        * `CREATE DATABASE demo_admin CHAR SET utf8;`.
        * Grant all (for dev server) permissions on both databases to demo_admin
          db user; password is "demo_admin".
        * Grant SELECT permission on front database to demo_front
          user; password is "demo_front".
* `python manage.py db:create_tables`
* `python manage.py db:init`
* `python manage.py db:gen photos:30 photosets:10 docs:5`
* for development server, set `SERVE_STATIC = True` in `./cfg_local.py`.
* `python manage.py admin:serve`
* Open http://localhost:8000/ in a browser. Default login/password are wheel/wheel.

