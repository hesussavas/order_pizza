#Solution for test assignment from Moberries

## Assignment
Implement the following logic using the Django REST framework:
    
    Imagine a pizza ordering services with the following functionality:

	• Order pizzas:
		• It should be possible to specify the desired flavors of pizza, the number of pizzas and their size.
		• An order should contain information regarding the customer.
		• It should be possible to track the status of delivery.
		• It should be possible to order the same flavor of pizza but with different sizes multiple times
	• Update an order:
		• It should be possible to update the details — flavours, count, sizes — of an order
		• It should not be possible to update an order for some statutes of delivery (e.g. delivered).
		• It should be possible to change the status of delivery.
	• Remove an order.
	• Retrieve an order:
		• It should be possible to retrieve the order by its identifier.
	• List orders:
		• It should be possible to retrieve all the orders at once.
		• Allow filtering by status / customer.

    Tasks
	    1. Design the model / database structure, use PostgreSQL for a backend with Django.
	    2. Design and implement an API with the Django REST framework for the web service described above.
	    3. Write test(s) for at least one of the API endpoints that you implemented.
	    4. Write a brief README with instructions on how to get your code from Git clone to up and  running on macOS and/or Linux hosts

    Please note!
	    • Use Python 3.6+ and the latest releases of Django, Django REST framework etc.
	    • You don't have to take care of authentication etc, we are just interested in structure and data modeling.
	    • You don't have to implement any frontend UI, just the API endpoints.
	    • Use viewsets where possible.
	    • Keep your endpoints as RESTful as possible.

## Solution
This solution is a simple RESTful-API implemented with `Python 3.7`, `Dajngo 2.2.6` and `djangorestframework 3.10.3`. 
When application is running, there is an endpoint at `/api/v1/orders/` which handles all the requests 
mentioned in assignment.

## At a glance

- There is a swagger-schema for the API. Please, check `openapi.yaml` file.
- Only 1 Django-model implemented. This model represents all order information.
- For brewity customer information is represented only with customer_email. That's probably ok for the start.
    Later it could be possible to create another model for representing customers and gather more information about
    customer during order creation (first name, address, e.t.c.). This will be useful for sending emails and helpful
    when it will be time to implement authentication or other customer service.
- Details of the order (number of pizzas and their types and sizes) are stored as a json in Postgres. According
    to the assignment there is no need to store them in a separate table, since that information is never used (it only 
    could be updated).
- It's impossible to update orders *(send PUT /orders/{orderID}/ requests)* in the following 
statuses `['dispatched', 'on_its_way', 'delivered']`
- It's only possible to update order's delivery status via PATCH requests.
- There is a `Dockerfile` and `docker-compose.yml` files in the repo. 

## How to run?
**Make sure you have Docker engine set up and docker-compose installed.**

Please, do the following steps:
- Clone the repository using `git clone` command
- Change directory to `/path/to/cloned/repo/`
- Use this command to start the application: `docker-compose up --build web`
This command will run the application at `http://0.0.0.0:8000/`.
Now you could try to reach the app with requests like this (example for [httpie](https://httpie.org/)):
`http GET localhost:8000/api/v1/orders/`.
More details on endpoints specifics in `openapi.yaml` file.

## Unittests
There are also unittests. 24 unittests for all API methods. They could be run inside a Docker container with a 
following command:

`docker-compose up --build unittest`

##Tested with
Tested under Docker Desktop for Mac v2.1.0.0, Docker engine: 19.03.1
