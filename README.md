# Optimized Subscription Management API


## Application Features

RESTful API using Python (Flask) backed by SQL (SQLite) for managing user subscriptions

### Features
- A User can register ```domain/user/register```
- A User can login ```domain/user/login```
- A User can create subscription plan ```domain/plan/create```
- A User can list subscription plans ```domain/plan/```
- A User can subscribe to a plan ```domain/subscription/subscribe```
- A User can upgade/downgrade to another subscription plan ```domain/subscription/upgrade```
- A User can cancel an active plan ```domain/subscription/cancel```
- A User can see all  his/her subscriptions(NB: can be filtered by status) ```domain/subscription/?status```
- A User can see retrieve a subscriptions ```domain/subscription/?status=active```

**NB:** You have to add the authorization token to the header of your request in order to access all subscription endpoints below e.g `Authorization: Bearer 94e052d826593f57118aa5c49b4d7b1786c37b6d`

## Technologies

### Backend

- [Python](https://www.python.org/) is a programming language that lets you work more quickly and integrate your systems more effectively.
- [Flask](https://flask.palletsprojects.com/en/stable/) is a lightweight WSGI web application framework.
- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
- [Docker](https://www.docker.com/) is a platform designed to help developers build, share, and run container applications.


## Installation
===== Set up for Docker ====
- Install [Python](https://www.python.org/) and [Docker](https://www.docker.com/) on your computer
- Clone this repository ```git clone https://github.com/nouwatinjacob/Optimized-Subscription-Management-API.git```
- Navigate to the directoty ```cd Optimized-Subscription-Management-API```
- add a ```.env``` file to the root of the project with neccessary environment added by following the example in .env.sample file
- Initialize migrations by running each command seperately ```flask db init``` , ```flask db migrate -m "Initial migration"```, and ```flask db upgrade```
- To start the app by running ```docker-compose up -d --build```

===== Set up for Virtual Environment ===== 
- Install [Python](https://www.python.org/) and [Docker](https://www.docker.com/) on your computer
- Clone this repository ```git clone https://github.com/nouwatinjacob/Optimized-Subscription-Management-API.git```
- Navigate to the directoty ```cd Optimized-Subscription-Management-API```
- add a ```.env``` file to the root of the project with neccessary environment added by following the example in .env.sample file
- Run : ```python -m venv venv``` (this creates the virtual env)
- Run : ```source venv/bin/activate``` (to activate your environment)
- Run : ```pip install -r requirements.txt``` (To install the dependencies)
- Initialize migrations by running each command seperately ```flask db init``` , ```flask db migrate -m "Initial migration"```, and ```flask db upgrade```
- Run : ```export FLASK_APP=run.py```
- Run : ```export FLASK_ENV=development```
- Run : ```flask run``` (To start the application)

## API Documentation is available on
After starting the application you will see the [documentation on swagger doc](http://127.0.0.1:5000/docs)

## Testing

- Create a test database of your choice by following the example in .env.sample file
- Run test with `pytest`


## Optimization Steps for Listing Subscriptions

- I implemented pagination which instead fetching all subscriptions at once, I added pagination using paginate(). This reduces memory usage and improves response time, especially for users with large numbers of subscriptions. The page and per_page query parameters allow flexible client-side navigation.
- I defined a composite database index on user_id and status (ix_user_status). This significantly improves the speed of filtered queries that include both fields — such as when fetching subscriptions for a specific user with a particular status
- I utilized eager loading (joinedload()) to preload the plan related to each subscription in the same query. This avoids the N+1 query problem where each subscription would otherwise trigger a separate query to fetch its associated plan. By eagerly loading the plan, I reduce the number of queries and enhance performance, especially when the subscription list is large.