Simple Authentication user using JWT 

## Installation steps

1. Ensure you have python3 installed

2. Clone the repository
3. create a virtual environment using `virtualenv .venv`
4. Activate the virtual environment by running `source .venv/bin/activate`

- On Windows use `venv\Scripts\activate`

5. Install the dependencies using `pip install -r requirements.txt`

### Run steps
create your environment by create .env file

copy from: `cp .env-sample .env`

edit it: `vim .env`

#### Then run with
- With `manage.py`
  1. Migrate existing db tables by running `python manage.py migrate`

  2. Run the django development server using `python manage.py runserver`


- With `docker`
    1. create a env file from postgresql/.env-sample
    2. Run docker compose using `docker-compose up`

### Documentation
Swagger url : `{server}/api/schema/swagger-ui/`
Swagger doc : `{server}/api/schema/redoc/`