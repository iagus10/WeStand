# Generated by Django 5.1.7 on 2025-05-02 12:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voluntariados', '0007_valoracionvoluntariado_autor_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='valoracionvoluntariado',
            name='autor',
            field=models.ForeignKey(default=16, on_delete=django.db.models.deletion.CASCADE, related_name='valoraciones_realizadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
