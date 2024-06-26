# Generated by Django 3.2.4 on 2021-11-05 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apitest', '0002_auto_20211105_1512'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='apicasestep',
            options={'ordering': ('sort',), 'verbose_name': '接口测试步骤', 'verbose_name_plural': '接口测试步骤'},
        ),
        migrations.AddField(
            model_name='ddtdata',
            name='desc',
            field=models.CharField(default=None, max_length=255, verbose_name='说明'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='httprequest',
            name='bodyType',
            field=models.CharField(blank=True, choices=[('json', 'json格式数据'), ('data', '普通键值对')], max_length=128, null=True, verbose_name='Post参数类型(可选)'),
        ),
    ]
