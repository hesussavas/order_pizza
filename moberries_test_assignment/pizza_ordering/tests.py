from functools import partial

from django.test import TestCase, Client

from pizza_ordering.models import Order


class OrdersApiBaseTestCase(TestCase):
    """Base test case for the project"""
    def setUp(self):
        # initialize test client
        self.client = Client()


class GetOrdersBaseTestCase(OrdersApiBaseTestCase):
    """Tests for GET /api/v1/orders/ method """
    def setUp(self):
        super(GetOrdersBaseTestCase, self).setUp()
        self.url = '/api/v1/orders/'
        self.order_items = """[
                                {"flavour": "hawaii",
                                 "quantity": 2,
                                 "size": "small"},                                                
                                {"flavour": "fungi",
                                 "quantity": 9,
                                 "size": "big"}
                               ]"""

    def test_get_zero_orders(self):
        # Issue a GET request.
        response = self.client.get(self.url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that by default we don't have anything in DB
        self.assertEqual(response.json()['count'], 0)

    def test_get_several_orders(self):
        # pre-create orders
        Order.objects.create(customer_email="test1@moberries.com",
                             delivery_status="not_in_delivery",
                             order_items=self.order_items)

        Order.objects.create(customer_email="test2@moberries.com",
                             delivery_status="not_in_delivery",
                             order_items=self.order_items)

        # Issue a GET request.
        response = self.client.get(self.url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that we got exactly 2 orders
        self.assertEqual(response.json()['count'], 2)

    def test_get_several_orders_filter_by_customer(self):
        # pre-create orders
        Order.objects.create(customer_email="test1@moberries.com",
                             delivery_status="not_in_delivery",
                             order_items=self.order_items)

        customer_to_filter = "test2@moberries.com"
        Order.objects.create(customer_email=customer_to_filter,
                             delivery_status="not_in_delivery",
                             order_items=self.order_items)

        # Issue a GET request with query param to filter by customer_email
        response = self.client.get(f'{self.url}?customer_email={customer_to_filter}')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that we got exactly 1 order (second order was filtered out)
        self.assertEqual(response.json()['count'], 1)

    def test_get_several_orders_filter_by_delivery_status(self):
        # pre-create orders
        Order.objects.create(customer_email="test1@moberries.com",
                             delivery_status="not_in_delivery",
                             order_items=self.order_items)

        delivery_status_to_filter = "delivered"
        Order.objects.create(customer_email="test1@moberries.com",
                             delivery_status=delivery_status_to_filter,
                             order_items=self.order_items)

        # Issue a GET request with query param to filter by delivery_status
        response = self.client.get(f'{self.url}?delivery_status={delivery_status_to_filter}')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that we got exactly 1 order (second order was filtered out)
        self.assertEqual(response.json()['count'], 1)

    def test_get_several_orders_paginate_with_limit(self):
        # pre-create 3 orders
        for _ in range(3):
            Order.objects.create(customer_email="test1@moberries.com",
                                 delivery_status="not_in_delivery",
                                 order_items=self.order_items)

        # Issue a GET request with query param to limit
        response = self.client.get(f'{self.url}?limit=2')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that we got exactly 2 orders
        self.assertEqual(len(response.json()['results']), 2)

    def test_get_several_orders_filter_by_offset(self):
        # pre-create 3 orders
        for i in range(3):
            Order.objects.create(customer_email=f"test{i}@moberries.com",
                                 delivery_status="not_in_delivery",
                                 order_items=self.order_items)

        # Issue a GET request with query param to offset orders by 1
        response = self.client.get(f'{self.url}?offset=1')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that we got exactly 2 orders
        self.assertEqual(len(response.json()['results']), 2)

        # chech that we filtered last created order
        results = response.json()['results']
        response_emails = [res['customer_email'] for res in results]
        # order should be "descending", cause we are intentionally sorting orders by creation date
        email_to_check = [f"test{i}@moberries.com" for i in reversed(range(2))]
        self.assertListEqual(response_emails, email_to_check)


class PostOrdersBaseTestCase(OrdersApiBaseTestCase):
    """Tests for POST /api/v1/orders/ method """
    def setUp(self):
        super(PostOrdersBaseTestCase, self).setUp()
        self.valid_post_data = {"customer_email": "test@moberries.com",
                                "order_items": [
                                    {"flavour": "hawaii",
                                     "quantity": 2,
                                     "size": "small"},
                                    {"flavour": "fungi",
                                     "quantity": 9,
                                     "size": "big"}
                                ]}
        self.post = partial(self.client.post, path='/api/v1/orders/', content_type='application/json')

    def test_post_orders_positive(self):
        response = self.post(data=self.valid_post_data)

        # Check that the response is 201 Created.
        self.assertEqual(response.status_code, 201)

        # Check customer_email in response
        self.assertEqual(response.json()["customer_email"], self.valid_post_data["customer_email"])

        # validate creation defaults
        self.assertIsNotNone(response.json()["created_at"])
        self.assertIsNotNone(response.json()["updated_at"])
        self.assertEqual(response.json()["delivery_status"], Order.DELIVERY_STATUSES[0][0])

    def test_post_orders_negative_empty_body(self):
        response = self.post(data=None)

        # check that both customer_email and order_items are required
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'This field is required', response.content)
        self.assertIn(b'customer_email', response.content)
        self.assertIn(b'order_items', response.content)

    def test_post_orders_negative_wrong_email(self):
        response = self.post(data={"customer_email": "test",
                                   "order_items": self.valid_post_data['order_items']})

        # check invalid email is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Enter a valid email address', response.content)

    def test_post_orders_negative_empty_order_items(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": []})

        # check empty order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'You have to specify at least 1 position in order items', response.content)

    def test_post_orders_negative_wrong_order_items_type(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": "test"})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Order items should be array', response.content)

    def test_post_orders_negative_wrong_number_of_params(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": [{"size": "big"}]})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'You have to specify exactly 3 attributes', response.content)

    def test_post_orders_negative_wrong_attr_name(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": [{"size": Order.ITEM_SIZES[0],
                                                    "flavour": Order.ITEM_FLAVOURS[0],
                                                    "test": "test"}]})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'You have to specify those attributes', response.content)

    def test_post_orders_negative_wrong_flavour_value(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": [{"flavour": "test",
                                                    "size": Order.ITEM_SIZES[0],
                                                    "quantity": 3}]})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Flavour must be one of', response.content)

    def test_post_orders_negative_wrong_size_value(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": [{"flavour": Order.ITEM_FLAVOURS[0],
                                                    "size": "test",
                                                    "quantity": 3}]})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Size must be one of', response.content)

    def test_post_orders_negative_wrong_quantity_type(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": [{"flavour": Order.ITEM_FLAVOURS[0],
                                                    "size": Order.ITEM_SIZES[0],
                                                    "quantity": "3"}]})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Quantity must be an integer', response.content)

    def test_post_orders_negative_quantity_zero(self):
        response = self.post(data={"customer_email": "test@moberries.com",
                                   "order_items": [{"flavour": Order.ITEM_FLAVOURS[0],
                                                    "size": Order.ITEM_SIZES[0],
                                                    "quantity": 0}]})

        # check invalid order_items is prohibited
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Quantity must be > 0"', response.content)

    def test_post_orders_order_items_deduplication(self):
        response = self.post(data={
            "customer_email": "test@moberries.com",
            "order_items": [
                {"flavour": Order.ITEM_FLAVOURS[0],
                 "size": Order.ITEM_SIZES[0],
                 "quantity": 2
                 },
                # duplicate for the first item. This item will remain in response.
                {"flavour": Order.ITEM_FLAVOURS[0],
                 "size": Order.ITEM_SIZES[0],
                 "quantity": 4
                 },

                # unique item
                {"flavour": Order.ITEM_FLAVOURS[1],
                 "size": Order.ITEM_SIZES[1],
                 "quantity": 2
                 },
            ]
        })

        self.assertEqual(response.status_code, 201)
        # check we have 2 order_items rather than 3 (was in initial request)
        self.assertEqual(len(response.json()['order_items']), 2)


class GetOrderByIdBaseTestCase(OrdersApiBaseTestCase):
    """Tests for GET /api/v1/orders/{order_id}/ method """
    def setUp(self):
        super(GetOrderByIdBaseTestCase, self).setUp()
        self.url = '/api/v1/orders/'
        self.order_items = """[{"flavour": "hawaii",
                                "quantity": 2,
                                "size": "small"}
                               ]"""

    def test_get_order_by_id_positive(self):
        order = Order.objects.create(
            customer_email="test1@moberries.com",
            delivery_status="not_in_delivery",
            order_items=self.order_items
        )

        # Issue a GET request.
        response = self.client.get(f"{self.url}{order.id}/")

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check email is the same
        self.assertEqual(response.json()['customer_email'], order.customer_email)

    def test_get_order_by_id_negative(self):
        order = Order.objects.create(
            customer_email="test1@moberries.com",
            delivery_status="not_in_delivery",
            order_items=self.order_items
        )

        # Issue a GET request with inexistent order_id in url
        response = self.client.get(f"{self.url}{order.id+1}/")

        # Check that the response is 404
        self.assertEqual(response.status_code, 404)


class PutOrderByIdBaseTestCase(OrdersApiBaseTestCase):
    """Tests for PUT /api/v1/orders/{order_id}/ method """
    def setUp(self):
        super(PutOrderByIdBaseTestCase, self).setUp()
        self.put = partial(self.client.put, content_type='application/json')
        self.url = '/api/v1/orders/'
        self.order_items = """
                [
                   {
                      "flavour":"hawaii",
                      "quantity":2,
                      "size":"small"
                   },
                   {
                      "flavour":"fungi",
                      "quantity":9,
                      "size":"big"
                   }
                ]"""

        self.order_items_updated = [
            {
                "flavour": "hawaii",
                "quantity": 2,
                "size": "small"
            }
        ]

    def test_put_order_by_id_positive(self):
        order = Order.objects.create(
            customer_email="test1@moberries.com",
            delivery_status="not_in_delivery",
            order_items=self.order_items
        )

        # Issue a PUT request.
        response = self.put(path=f"{self.url}{order.id}/",
                            data={"customer_email": "test1@moberries.com",
                                  "order_items": self.order_items_updated})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that order_items updated successfully
        self.assertEqual(response.json()['order_items'], self.order_items_updated)

    def test_put_order_by_id_wrong_delivery_status(self):
        order = Order.objects.create(
            customer_email="test1@moberries.com",
            delivery_status=Order.DELIVERY_STATUSES_NO_UPDATE[0],
            order_items=self.order_items
        )

        # Issue a PUT request.
        response = self.put(path=f"{self.url}{order.id}/",
                            data={"customer_email": "test1@moberries.com",
                                  "order_items": self.order_items_updated})

        # Check that the response is 400
        self.assertEqual(response.status_code, 400)

        # Check that we can't update order in specific delivery_status
        self.assertIn(b"Order couldn't be updated once it's in one of delivery statuses", response.content)


class PatchOrderByIdBaseTestCase(OrdersApiBaseTestCase):
    """Tests for PATCH /api/v1/orders/{order_id}/ method """
    def setUp(self):
        super(PatchOrderByIdBaseTestCase, self).setUp()
        self.patch = partial(self.client.patch, content_type='application/json')
        self.url = '/api/v1/orders/'
        self.order_items = """
                [
                   {
                      "flavour":"hawaii",
                      "quantity":2,
                      "size":"small"
                   },
                   {
                      "flavour":"fungi",
                      "quantity":9,
                      "size":"big"
                   }
                ]"""

    def test_patch_order_by_id_positive(self):
        order = Order.objects.create(
            customer_email="test1@moberries.com",
            delivery_status="delivered",
            order_items=self.order_items
        )
        delivery_status_updated = "on_its_way"
        # Issue a PATCH request.
        response = self.patch(path=f"{self.url}{order.id}/",
                              data={"delivery_status": delivery_status_updated})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that delivery status actually updated in DB
        order.refresh_from_db()
        self.assertEqual(order.delivery_status, delivery_status_updated)


class DeleteOrderByIdBaseTestCase(OrdersApiBaseTestCase):
    """Tests for DELETE /api/v1/orders/{order_id}/ method """
    def setUp(self):
        super(DeleteOrderByIdBaseTestCase, self).setUp()
        self.url = '/api/v1/orders/'
        self.order_items = """
                [
                   {
                      "flavour":"hawaii",
                      "quantity":2,
                      "size":"small"
                   }
                ]"""

    def test_delete_order_by_id_positive(self):
        order = Order.objects.create(
            customer_email="test1@moberries.com",
            delivery_status="delivered",
            order_items=self.order_items
        )
        # check that order is presented
        response = self.client.get(path=f"{self.url}{order.id}/")
        self.assertEqual(response.status_code, 200)

        # Issue a DELETE request.
        response = self.client.delete(path=f"{self.url}{order.id}/")
        # Check that the response is 204 No content.
        self.assertEqual(response.status_code, 204)

        # check that order vanished from DB
        response = self.client.get(path=f"{self.url}{order.id}/")
        self.assertEqual(response.status_code, 404)
