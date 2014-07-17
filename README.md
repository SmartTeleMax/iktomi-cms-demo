
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

