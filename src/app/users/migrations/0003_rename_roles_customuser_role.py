# Generated by Django 4.1.3 on 2022-11-11 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_customuser_roles_delete_role_customuser_roles'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='roles',
            new_name='role',
        ),
    ]
