# TODO: dump session data, havent found a good way to merge the output yet.
# ================================== # ==================================# 


# Dump superuser data 
./manage.py dumpdata --indent=2 auth > initial_data.json;

# Remove database since there can be dependencies (foreign keys)
rm database/test.db;

# By default syncdb with --noinput will use "initial_data.json".
./manage.py syncdb --noinput;

