# Generated by Django 5.2.1 on 2025-06-09 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0088_alter_articlepage_body_alter_contactopage_body_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticiapage',
            name='categoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='noticias', to='home.categorianoticia'),
        ),
    ]
