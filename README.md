`$ carto_cli`
=========================

**WORK IN PROGRESS**

A simple set of command line applications to interact with your own CARTO account.


* [`carto_env`](#carto_env): load your credentials to interact with your account
* [`carto_sql`](#carto_sql): perform queries against the [SQL API](https://carto.com/docs/carto-engine/sql-api/)
* [`carto_batch`](#carto_batch): perform queries using the [Batch SQL API](https://carto.com/docs/carto-engine/sql-api/batch-queries)
* [`carto_dataset`](#carto_dataset): manage your CARTO datasets
* [`carto_map`](#carto_map): TO DO

## How-to's

### How to install

As for now you need to clone or download the repo and run `pip install .` or `python setup.py install`.

### How to contribute

You can fork the repo and set up your environment for development running `pip install --editable .`

From there you can make Pull Requests with any fix or improvement. When this is more mature I'll document how to contribute a new subcommand but you can actually take a look to the `setup.py` file and then any of the scripts of the different folders.

### A note about environment variables

All the tools here use by default some environment variables. If you only manage one single CARTO account then you can set them in any initialization script that your environment uses like `~/.bashrc` or `/etc/environment` with these variables:

 - `CARTO_USER`: you user name
 - `CARTO_ORG`: the name of your CARTO organization if you use the Open Source or an Enterprise account
 - `CARTO_API_KEY`: your API key to interact with CARTO Engine
 - `CARTO_API_URL`: if you don't use a `carto.com` account you need to put here the equivalent to the API end point. For a `carto.com` account it would be `http://user.carto.com/`
 - `CARTO_CHECK_SSL`: if you are using your own server and don't have a proper certificate installed set this variable to `false`

Setting up those variables will save you having to put them on any call to the command line applications, saving you a lot of Copy&Paste work.

## `carto_env`

If you happen to work with a different set of CARTO accounts this tool is for you. This relies in a yaml file that with a very simple structure. This command wil load information into your terminal so you can copy & paste once and export your environment variables for your session or if you have the `$CARTO_ENV` environment or use the `-o` parameter it will save it in a file so you can source it.

```
$ carto_env -h
Usage: carto_env [OPTIONS] COMMAND [ARGS]...

  Allows you to get the account details

Options:
  -c, --config-file FILENAME  Configuration file to read, defaults to
                              ~/.cartorc.yaml or the environment variable
                              $CARTO_DB
  -h, --help                  Show this message and exit.

Commands:
  list     List your stored users
  load     The user wou want to retrieve
  search   Returns the user names that match the given...
  version  Prints the version of this application
```

So if you have the `$CARTO_ENV` environment pointing for example to `/tmp/cartoenv` and then you define `alias c="source $CARTO_ENV"` then you can load any user of your database with:

```bash
$ carto_env load jsanz; c
```

### Configuration file

Store a `yaml` file named (by default) `~/.cartorc.yaml` with this structure

```yaml
---
jsanz:
  api_key: your_api_key
  organization: team

another_user:
  api_key: another_api_key
  organization: team

another_user:
  api_key: your_api_key
  organization: myorg
  url: http://myserver.mydomain.com
```

## `carto_sql`

```
$ carto_sql -h
Usage: carto_sql [OPTIONS] COMMAND [ARGS]...

  Performs different actions against the SQL API

Options:
  -u, --user-name TEXT     Your CARTO.com user. It can be omitted if
                           $CARTO_USER is available
  -o, --org-name TEXT      Your organization name. It can be ommitted if
                           $CARTO_ORG is available
  -a, --api-url TEXT       If you are not using carto.com you need to specify
                           your API endpoint. It can be omitted if
                           $CARTO_API_URL is available
  -k, --api-key TEXT       It can be omitted if $CARTO_API_KEY is available
  -c, --check-ssl BOOLEAN  Check server SSL Certificate (default = True or
                           CARTO_CHECK_SSL envvar)
  -h, --help               Show this message and exit.

Commands:
  functions  Functions on your account
  kill       Kills a query based on its pid
  queries    Shows the current running queries
  run        Execute a SQL passed as a string
  schemas    List your organization schemas
  version    Prints the version of this application
```

Check for details on each command as they have especific options.

## `carto_batch`

```
$ carto_batch -h
Usage: carto_batch [OPTIONS] COMMAND [ARGS]...

  Performs different actions against the Batch SQL API

Options:
  -u, --user-name TEXT     Your CARTO.com user. It can be omitted if
                           $CARTO_USER is available
  -o, --org-name TEXT      Your organization name. It can be ommitted if
                           $CARTO_ORG is available
  -a, --api-url TEXT       If you are not using carto.com you need to specify
                           your API endpoint. It can be omitted if
                           $CARTO_API_URL is available
  -k, --api-key TEXT       It can be omitted if $CARTO_API_KEY is available
  -c, --check-ssl BOOLEAN  Check server SSL Certificate (default = True or
                           CARTO_CHECK_SSL envvar)
  -h, --help               Show this message and exit.

Commands:
  cancel   Cancels a job
  create   Creates a new job and returns its ID
  list     Display the ids of all your running jobs
  read     Returns details about a job id (JSON)
  version  Prints the version of this application
```

## `carto_dataset`

Command to work with your account datasets, get information from them, upload and
download data, etc.


```
$ carto_dataset -h
Usage: carto_dataset [OPTIONS] COMMAND [ARGS]...

  Performs different actions against the SQL API

Options:
  -u, --user-name TEXT     Your CARTO.com user. It can be omitted if
                           $CARTO_USER is available
  -o, --org-name TEXT      Your organization name. It can be ommitted if
                           $CARTO_ORG is available
  -a, --api-url TEXT       If you are not using carto.com you need to specify
                           your API endpoint. It can be omitted if
                           $CARTO_API_URL is available
  -k, --api-key TEXT       It can be omitted if $CARTO_API_KEY is available
  -c, --check-ssl BOOLEAN  Check server SSL Certificate (default = True or
                           CARTO_CHECK_SSL envvar)
  -h, --help               Show this message and exit.

Commands:
  cartodbfy       Runs the cartodbfication of a table to...
  delete          Deletes a dataset from your account
  describe        Report of all your table details
  edit            Edit dataset properties
  export          Export your dataset
  import_dataset  Import a new dataset from a file on your...
  indexes         List your table associated indexes
  list            Display all your CARTO datasets
  list_tables     List tables and their main Postgres...
  merge           Merges a number of datasets
  rename          Renames a dataset from your account
  schema          Shows your dataset attributes and types
  triggers        List your table associated triggers
  version         Prints the version of this application

```


## `carto_map`

Manage your maps