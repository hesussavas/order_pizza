import itertools
from typing import List, Dict

from rest_framework import serializers

from pizza_ordering.models import Order


class OrderPatchSerializer(serializers.ModelSerializer):
    """
    Serializer class for PATCH method. With PATCH method user must be allowed to patch only delivery_status field.
    That's why the rest of the fields are marked as read-only
    """

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'customer_email', 'order_items', 'created_at', 'updated_at', ]


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer class for GET, POST, PUT and DELETE methods.
    The only writable fields are: customer_email and order_items
    """

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'delivery_status', 'created_at', 'updated_at', ]
        extra_kwargs = {'customer_email': {'required': True},
                        'order_items': {'required': True}}

    def validate_order_items(self, order_items: List[Dict]) -> List[Dict]:
        """
        Validates order_items input parameter. Raises serializers.ValidationError if validation failed.
        """
        # don't accept empty order_items.
        if not order_items:
            raise serializers.ValidationError("Empty orders are not allowed. "
                                              "You have to specify at least 1 position in order items.")

        # don't accept order_items of other types
        if not isinstance(order_items, list):
            raise serializers.ValidationError("Empty orders are not allowed. "
                                              "Order items should be array.")

        # check the content of each item and deduplicate items of the same flavour and size if any
        for item in order_items:
            self.validate_order_item_element(item)

        # return deduplicated version of order_items
        return list(self.deduplicate(order_items))

    @staticmethod
    def deduplicate(order_items: List[Dict]):
        """
        Generator, which removes duplicates for order items with the same 'flavour' and 'size'.
        """
        soi = sorted(order_items, key=keyfunc)
        for key, group in itertools.groupby(soi, key=keyfunc):
            yield list(group)[0]

    @staticmethod
    def validate_order_item_element(order_item: dict) -> None:
        """
        Checks that order_item's element is valid (contains needed amount of parameters and their
        values are also valid).
        """

        # check the amount of parameters
        if len(order_item) != len(Order.ORDER_ITEM_ATTRIBUTES):
            raise serializers.ValidationError("Wrong order item format. "
                                              "You have to specify exactly 3 attributes")

        # check the names of parameters
        if sorted(order_item.keys()) != sorted(Order.ORDER_ITEM_ATTRIBUTES):
            raise serializers.ValidationError("Wrong order item format. "
                                              f"You have to specify those attributes: {Order.ORDER_ITEM_ATTRIBUTES}")

        # check 'flavour' value
        if not order_item['flavour'] in Order.ITEM_FLAVOURS:
            raise serializers.ValidationError("Wrong order item format. "
                                              f"Flavour must be one of: {Order.ITEM_FLAVOURS}")
        # check 'quantity' value
        if not isinstance(order_item['quantity'], int):
            raise serializers.ValidationError("Wrong order item format. "
                                              "Quantity must be an integer")
        # check 'quantity' > 0
        if not order_item['quantity'] > 0:
            raise serializers.ValidationError("Wrong order item format. Quantity must be > 0")

        # check 'size' value
        if not order_item['size'] in Order.ITEM_SIZES:
            raise serializers.ValidationError("Wrong order item format. "
                                              f"Size must be one of: {Order.ITEM_SIZES}")


def keyfunc(x):
    """ Simple function for sorting order_items"""
    return x['flavour'], x['size']
