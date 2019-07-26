# Generated by Django 2.1.1 on 2019-07-25 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(verbose_name='收货地址')),
                ('reciver', models.CharField(max_length=30, verbose_name='收货人')),
                ('rece_phone', models.CharField(max_length=30, verbose_name='收货电话')),
                ('post_num', models.CharField(max_length=30, verbose_name='邮编')),
            ],
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30, verbose_name='用户名')),
                ('password', models.CharField(max_length=30, verbose_name='密码')),
                ('email', models.EmailField(max_length=254, verbose_name='用户邮箱')),
                ('phone', models.CharField(max_length=30, verbose_name='用户电话')),
                ('connect_address', models.TextField(verbose_name='联系地址')),
            ],
        ),
        migrations.AddField(
            model_name='address',
            name='buyer_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Buyer.Buyer', verbose_name='用户id'),
        ),
    ]
