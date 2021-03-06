# Generated by Django 2.2.6 on 2019-10-14 11:29

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer_email', models.EmailField(db_index=True, max_length=254)),
                ('delivery_status', models.CharField(choices=[('not_in_delivery', 'Not ready yet for delivery. Still preparing'), ('ready_for_delivery', 'All preparations finished. Ready for delivery'), ('dispatched', 'Order has been dispatched to delivery service'), ('on_its_way', 'Delivery service is currently delivering the order'), ('delivered', 'Delivered to customer')], db_index=True, default='not_in_delivery', max_length=20)),
                ('order_items', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='The content of the order')),
            ],
        ),
    ]
