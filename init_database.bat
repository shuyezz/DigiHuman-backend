:: 请修改下面的password为mysql数据库密码
:: 请修改下面的user为mysql用户名

@echo off
chcp 65001

set user=root
set password=123456

mysql -u %user% -p%password% --default-character-set=utf8 < reset.sql
mysql -u %user% -p%password% --default-character-set=utf8 < server_init.sql
mysql -u %user% -p%password% --default-character-set=utf8 < preset_data_init.sql

echo 数据库初始化完毕, 现在可以退出了

pause;