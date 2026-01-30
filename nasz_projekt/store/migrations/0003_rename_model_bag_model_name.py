
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_bag_cart_cartitem_order_ordersummary_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bag',
            old_name='model',
            new_name='model_name',
        ),
    ]
