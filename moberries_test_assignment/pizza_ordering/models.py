from django.db import models
from django.contrib.postgres.fields import JSONField


class Order(models.Model):
    """
    Main model, representing the whole order.
    """
    DELIVERY_STATUSES = (
        ('not_in_delivery', 'Not ready yet for delivery. Still preparing'),
        ('ready_for_delivery', 'All preparations finished. Ready for delivery'),
        ('dispatched', 'Order has been dispatched to delivery service'),
        ('on_its_way', 'Delivery service is currently delivering the order'),
        ('delivered', 'Delivered to customer'),
    )
    DELIVERY_STATUSES_NO_UPDATE = ['dispatched', 'on_its_way', 'delivered']
    ORDER_ITEM_ATTRIBUTES = ['flavour', 'quantity', 'size']
    ITEM_FLAVOURS = ["margherita", "hawaii", "fungi", "pepperoni", "capricciosa"]
    ITEM_SIZES = ["big", "small"]

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_email = models.EmailField(db_index=True)
    delivery_status = models.CharField(choices=DELIVERY_STATUSES,
                                       default=DELIVERY_STATUSES[0][0],
                                       max_length=20,
                                       db_index=True)
    order_items = JSONField(verbose_name="The content of the order")

    def __str__(self):
        """
        String representation of the order - id of the order
        """
        return f"{self.id}"
