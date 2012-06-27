#!/bin/bash

python manage.py test --settings=settings.test
return $?
