# Generated by Django 3.2.4 on 2021-11-05 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024, verbose_name='报告标题')),
                ('report_type', models.CharField(max_length=200, null=True, verbose_name='报告类型')),
                ('desc', models.CharField(max_length=1024, verbose_name='报告简述')),
                ('report_detail', models.CharField(max_length=1024, verbose_name='报告详情')),
                ('created_time', models.DateTimeField(auto_now=True, verbose_name='报告生成时间')),
            ],
            options={
                'verbose_name': '测试报告',
                'verbose_name_plural': '测试报告',
            },
        ),
    ]
