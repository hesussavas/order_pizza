from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers

from pizza_ordering.models import Order
from pizza_ordering.serializers import OrderSerializer, OrderPatchSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be viewed or edited.
    """
    queryset = Order.objects.order_by('-created_at')  # sort orders by creation time in desc order.
    serializer_class = OrderSerializer  # default serializer
    filter_backends = [DjangoFilterBackend]  # backend for filtering
    filterset_fields = ['customer_email', 'delivery_status']  # fields to filter by

    def update(self, request, *args, **kwargs):
        """
        Handler for HTTP PUT method.
        Will refuse to do the actual update for order with several delivery statuses values.

        Under the hood, partial_update() eventually will also call this method. For those calls we don't want to
        check delivery status because it doesn't make sense (partial_update() can only update delivery_method).

        """
        obj = self.get_object()

        # don't allow updates for orders with several delivery statuses. But partial update should be allowed.
        if obj.delivery_status in Order.DELIVERY_STATUSES_NO_UPDATE and not kwargs.get('partial'):
            raise serializers.ValidationError(
                f"Order couldn't be updated once it's in one of delivery statuses {Order.DELIVERY_STATUSES_NO_UPDATE}")

        return super(OrderViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Handler for HTTP PATCH method. Used for delivery_status updates. This is the only way to update delivery_status.
        It has to have it's own serializer (OrderPatchSerializer) where delivery_status is not read-only.
        """
        self.serializer_class = OrderPatchSerializer
        return super(OrderViewSet, self).partial_update(request, *args, **kwargs)
