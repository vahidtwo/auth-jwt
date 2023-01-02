Simple Authentication user

## Installation steps

1. Ensure you have python3 installed

2. Clone the repository
3. create a virtual environment using `virtualenv .venv`
4. Activate the virtual environment by running `source .venv/bin/activate`

- On Windows use `venv\Scripts\activate`

5. Install the dependencies using `pip install -r requirements.txt`

#### Run steps
- With `manage.py`
  1. Migrate existing db tables by running `python manage.py migrate`

  2. Run the django development server using `python manage.py runserver`


- With `docker`
    Run docker compose using `docker-compose up`