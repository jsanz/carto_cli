# Migrating data between accounts

This procedure is intended to document how to move all tables from one CARTO account to another.

## Export datasets

Asuming you have `$CARTO_ENV` so `carto_env load` outputs to that location:

```shell
$ # Load environment
$ echo $CARTO_ENV 
/tmp/cartoenv
$ carto_env load account1
$ source $CARTO_ENV

$ # Export all tables as geopackage
$ for i in `carto_dataset list_tables | jq ".[].name" | sed 's/"//g'`; do\
  echo "Exporting $i ..."; \
  carto_dataset export $i; \
  done
```

If any of the datasets is bigger than the `$CARTO_SPLIT_EXPORT` variable or the default value of 500.000 then the exporter will automatically generate split files that you'll have to merge later using `carto_dataset merge`

## Importing datasets

Again load the environment and run the import command moving the datasets to a processed folder

```shell
$ # Load environment
$  echo $CARTO_ENV 
/tmp/cartoenv
$ carto_env load account2
$ source $CARTO_ENV

$ # Import all datasets
$ mkdir -p processed
$ for i in *.gpkg; do \
  echo "Importing $i ..."; \
  carto_dataset import_dataset $i; \
  mv $i uploaded; \
  done
```
