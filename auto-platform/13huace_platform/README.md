平台设计核心思路1： 更友好的UI界面
> 配置文件的方法，依然有一定的使用门槛，以及不便性

1. pycharm创建项目 04-huace_platform
2. 添加依赖 django 
```pip install django```
3. 创建django项目
```django-admin startproject auto_test_platform```
4. 配置数据库
```
# 数据库操作 - python依赖
pymysql==1.0.2
sqlalchemy==1.4.18
# auto_test_platform/__init__.py 文件
import pymysql
pymysql.install_as_MySQLdb()

# settings.py文件内添加数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'auto_test_platform',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
```
5. 添加页面UI模板依赖
```
# 所需要的依赖
django-simpleui==2021.6.2
django-nested_admin==3.3.3
# setting.py 文件内修改
INSTALLED_APPS = [
    'simpleui',
    'nested_admin',
    ...
```
6. 配置中文/时区/LOGO展示
```
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/static/'
HERE = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.join(HERE, '../')
STATICFILES_DIRS = (
    os.path.join(HERE, 'static/'),
)
SIMPLEUI_LOGO='/static/img/logo.png'
SIMPLEUI_HOME_INFO=False

```
7. 第一次启动，检查登录逻辑
```
# 创建数据库
python manage.py  makemigrations
# 生成数据库 - 此操作连接数据库创建表及对应的数据
python manage.py  migrate
# 首次启动创建root账户
python manage.py  createsuperuser
# 启动django程序
python manage.py runserver 0.0.0.0:8000
```
8. 添加django模块
```
# 增加一个接口自动化测试模块
django-admin startapp apitest

# 修改模块名称 apps.py
name = 'apitest'
verbose_name="接口自动化测试管理"

# django中加入新增的模块 settings.py
INSTALLED_APPS = [
    'apitest',
    ... 
```
9. 分析数据需要，设计接口自动化测试相关的数据库表
```
# models设计


# 新模块上线
# 创建数据库
python manage.py  makemigrations
# 生成数据库 - 此操作连接数据库创建表及对应的数据
python manage.py  migrate
```
10. 添加执行用例功能
11. 添加测试报告查看功能
```
# 调用 apirun 命令，生成测试报告到指定的文件夹
# 指定模板目录
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["/tmp/auto_test_platform"],
# 查看报告时，返回html内容即可
# 
```


12. 安装pytest-selenium插件
13. 安装webrun命令
14. 安装apprun命令