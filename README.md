# ECFR API 

## This API provides the following capabilities:

1. Actionable insights to be made on potential deregulation efforts across the government by providing KPIs such as word count growth is CFR, growth is restrictive terms ("shall", "must", "may not", "prohibited"), growth in the number of sections, addition of subparts over time
2. API to extract KPIs


## Instructions
1. Download and install Community Edition of MySQL from [here](https://www.mysql.com/products/community/)
2. create user 'ecfr_user'@'localhost' IDENTIFIED BY 'secret';
3. create database ecfr;
4. create database test_ecfr;
5. grant all on `ecfr`.* to 'ecfr_user'@'localhost';
6. grant all on `test_ecfr`.* to 'ecfr_user'@'localhost';
