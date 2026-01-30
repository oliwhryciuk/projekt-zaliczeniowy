
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_model_bag_model_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='bag',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='bag_photos/'),
        ),
    ]
