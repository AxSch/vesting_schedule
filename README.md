# Vesting Schedule

## Requirements
* python 3.13
* pipenv
* A strong will :)


## Setup

1. Setup & activate the project's virtual env
```shell
pipenv install
```

```shell
pipenv shell
```

2. Run the program
```shell
pipenv run vesting_schedule [csv_file] [target_date] [precision]
```

3. Run the tests
```shell
pytest . 
```

3. Enjoy the sunrise :')


Here's some test data:
```
VEST,E001,Alice Smith,ISO-001,2020-01-01,1000
VEST,E001,Alice Smith,ISO-001,2021-01-01,1000
VEST,E001,Alice Smith,ISO-002,2020-03-01,300
VEST,E001,Alice Smith,ISO-002,2020-04-01,500
VEST,E002,Bobby Jones,NSO-001,2020-01-02,100
VEST,E002,Bobby Jones,NSO-001,2020-02-02,200
VEST,E002,Bobby Jones,NSO-001,2020-03-02,300
VEST,E003,Cat Helms,NSO-002,2024-01-01,100
```

```
VEST,E001,Alice Smith,ISO-001,2020-01-01,1000
VEST,E001,Alice Smith,ISO-001,2021-01-01,1000
VEST,E001,Alice Smith,ISO-002,2020-03-01,500
CANCEL,E001,Alice Smith,ISO-002,2020-04-01,200
VEST,E002,Bobby Jones,NSO-001,2020-01-02,400
CANCEL,E002,Bobby Jones,NSO-001,2020-02-02,200
VEST,E002,Bobby Jones,NSO-001,2020-03-02,300
VEST,E003,Cat Helms,NSO-002,2023-01-01,500
VEST,E003,Cat Helms,NSO-002,2024-01-01,500
CANCEL,E003,Cat Helms,NSO-002,2024-02-01,300
```

```
VEST,E001,Alice Smith,ISO-001,2020-01-01,1000
PERFORMANCE,E001,Alice Smith,ISO-001,2020-12-31,2
```
