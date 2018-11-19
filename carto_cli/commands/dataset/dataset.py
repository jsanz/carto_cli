import click
import json
import warnings
import csv
import os
import time

from prettytable import PrettyTable
from carto_cli.carto import queries
from carto_cli.commands.sql.execute_sql import run as run_sql

from carto.permissions import PRIVATE, PUBLIC, LINK

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

warnings.filterwarnings('ignore')

SPLIT_EXPORT = int(os.environ.get("CARTO_SPLIT_EXPORT", 500000))

def prettyMBprint(value):
    try:
        size = int(value) / (1024.0*1024)
        return "{:.2f} MB".format(size)
    except Exception as e:
        return value

def prettyIntPrint(value):
    return "{:,}".format(value)

def get_dataset(name, datasets):
    for dataset in datasets:
        if dataset.name == name:
            return dataset

def get_cartodbfy_query(user,org,table_name):
    if org:
        return 'SELECT CDB_CartoDBfyTable(\'{}\',\'{}\')'.format(user,table_name)
    else:
        return 'SELECT CDB_CartoDBfyTable(\'{}\')'.format(table_name)

def get_vrt_type(postgis_type):
    return postgis_type.replace('ST_','wkb')

@click.command(help="Display all your CARTO datasets")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty','vrt']))
@click.option('-t', '--filter', help="Filter the datasets")
@click.help_option('-h', '--help')
@click.pass_context
def list(ctx, format, filter):
    carto_obj = ctx.obj['carto']
    manager = carto_obj.get_dataset_manager()
    try:
        all_datasets =  manager.all()
        datasets = [d for d in all_datasets if not filter or d.name.find(filter) > -1]

        dataset_names = [dataset.name for dataset in datasets]

        results = [
            {
                'name': dataset.name,
                'likes': dataset.likes,
                'locked': dataset.locked,
                'privacy': dataset.privacy,
                'description': dataset.description,
                'license': dataset.license,
                'attributions': dataset.attributions,
                'tags': dataset.tags,
                'size': dataset.table.size,
                'row_count': dataset.table.row_count
            } for dataset in datasets
        ]

        if format == 'json':
            raw_result = json.dumps(results)
        elif format == 'csv':
            with StringIO() as csvfile:
                fieldnames = ['name', 'likes', 'locked', 'privacy',
                              'description', 'license', 'attributions',
                              'tags', 'size', 'row_count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in results:
                    row['tags'] = ", ".join(row['tags'])
                    writer.writerow(row)

                raw_result = csvfile.getvalue()
        elif format == 'vrt':
            with StringIO() as vrtfile:
                vrtfile.write('<OGRVRTDataSource>')
                for dataset in datasets:
                    types = dataset.table.geometry_types
                    if types and len(types) == 1:
                        geom_type = get_vrt_type(types[0])
                        template = '''
<OGRVRTLayer name="{layer}">
    <LayerSRS>EPSG:4326</LayerSRS>
    <SrcDataSource>Carto:{user}</SrcDataSource>
    <GeometryType>{geomtype}</GeometryType>
    <SrcLayer>{layer}</SrcLayer>
</OGRVRTLayer>'''.format(layer=dataset.name, geomtype=geom_type, user = carto_obj.user_name)

                        vrtfile.write(template)
                vrtfile.write('\r\n</OGRVRTDataSource>\r\n')
                raw_result = vrtfile.getvalue()
        else:
            table_general = PrettyTable(
                ['Table Name', 'Privacy', 'Locked', 'Likes', 'Size',
                 'Rows', 'Tags'])
            table_general.align = "r"
            table_general.align['Table Name'] = "l"
            table_general.align['Privacy'] = "c"
            table_general.align['Tags'] = "l"

            for row in results:
                table_general.add_row([
                    row['name'],
                    row['privacy'],
                    row['locked'],
                    row['likes'],
                    prettyMBprint(row['size']),
                    prettyIntPrint(row['row_count']),
                    ", ".join(row['tags'])
                ])

            raw_result = table_general.get_string()

        click.echo(raw_result, nl=format in ['json', 'pretty'])
    except Exception as e:
        ctx.fail("Error retrieving the list of datasets: {}".format(e))


@click.command(help="List tables and their main Postgres statistics")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty','vrt']))
@click.option('-t', '--filter', help="Filter the tables")
@click.help_option('-h', '--help')
@click.pass_context
def list_tables(ctx, format, filter):
    carto_obj = ctx.obj['carto']

    if carto_obj.org_name:
        schema_name = carto_obj.user_name
    else:
        schema_name = 'public'

    sql = queries.LIST_TABLES.format(schema_name=schema_name,table_name='%{}%'.format(filter if filter else ''))
    result = carto_obj.execute_sql(sql)

    if format == 'json':
        raw_result = json.dumps(result['rows'])
    elif format == 'csv':
        with StringIO() as csvfile:
            fieldnames = queries.LIST_TABLES_HEADER
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in result['rows']:
                writer.writerow(row)

            raw_result = csvfile.getvalue()
    else:
        table_general = PrettyTable(queries.LIST_TABLES_HEADER)
        table_general.align = "r"
        table_general.align['name'] = "l"

        for row in result['rows']:
            pretty_row = []
            for key in queries.LIST_TABLES_HEADER:
                pretty_row.append(row[key])
            table_general.add_row(pretty_row)

        raw_result = table_general.get_string()

    click.echo(raw_result, nl=format in ['json', 'pretty'])

@click.command(help="Shows your dataset attributes and types")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.argument('table_name')
@click.pass_context
def schema(ctx, format, table_name):
    carto_obj = ctx.obj['carto']
    sql = queries.SCHEMA.format(table_name=table_name)
    result = carto_obj.execute_sql(sql)

    if format == 'json':
        raw_result = json.dumps(result['rows'])

    elif format == 'csv':
        with StringIO() as csvfile:
            fieldnames = ['attribute', 'type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in result['rows']:
                writer.writerow(row)

            raw_result = csvfile.getvalue()
    else:
        table_general = PrettyTable(['attribute', 'type'])
        table_general.align = "l"

        for row in result['rows']:
            table_general.add_row(row.values())

        raw_result = table_general.get_string()
    click.echo(raw_result, nl=format in ['json', 'pretty'])


@click.command(help="List your table associated triggers")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.argument('table_name')
@click.pass_context
def triggers(ctx, format, table_name):
    carto_obj = ctx.obj['carto']
    sql = queries.TRIGGERS.format(table_name=table_name)
    result = carto_obj.execute_sql(sql)
    fieldnames = ['tgname']

    if format == 'json':
        raw_result = json.dumps(result['rows'])

    elif format == 'csv':
        with StringIO() as csvfile:
            #import ipdb; ipdb.set_trace()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in result['rows']:
                writer.writerow(row)

            raw_result = csvfile.getvalue()
    else:
        table_general = PrettyTable(fieldnames)
        table_general.align = "l"

        for row in result['rows']:
            table_general.add_row(row.values())

        raw_result = table_general.get_string()
    click.echo(raw_result, nl=format in ['json', 'pretty'])


@click.command(help="List your table associated indexes")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.argument('table_name')
@click.pass_context
def indexes(ctx, format, table_name):
    carto_obj = ctx.obj['carto']
    sql = queries.INDEXES.format(table_name=table_name)
    result = carto_obj.execute_sql(sql)
    fieldnames = ['index_name', 'column_name', 'index_type']

    if format == 'json':
        raw_result = json.dumps(result['rows'])

    elif format == 'csv':
        with StringIO() as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in result['rows']:
                writer.writerow(row)

            raw_result = csvfile.getvalue()
    else:
        table_general = PrettyTable(fieldnames)
        table_general.align = "l"

        for row in result['rows']:
            table_general.add_row(row.values())

        raw_result = table_general.get_string()
    click.echo(raw_result, nl=format in ['json', 'pretty'])



@click.command(help="Report of all your table details")
@click.option('-r','--refresh',is_flag=True,default=False,
    help="Force statistics refresh")
@click.help_option('-h', '--help')
@click.argument('table_name')
@click.pass_context
def describe(ctx, refresh, table_name):
    carto_obj = ctx.obj['carto']
    try:
        if refresh:
            result = carto_obj.execute_sql('vacuum analyze {}'.format(table_name))

        sql = queries.LIST_TABLES.format(schema_name=carto_obj.user_name,
                table_name=table_name)
        result = carto_obj.execute_sql(sql)
        table_general = PrettyTable(['Property','Value'])
        table_general.align = "l"

        for row in result['rows']:
            for key in row.keys():
                table_general.add_row([key,row[key]])

        click.echo('\r\n# Report for table: {}'.format(table_name))
        click.echo('\r\n## Postgres Metadata\r\n')
        click.echo(table_general.get_string())
    except Exception as e:
        click.echo(e)
        ctx.fail('Error retrieving information, is your table name correct?')

    manager = carto_obj.get_dataset_manager()
    click.echo('\r\n## CARTO Metadata\r\n')
    try:
        dataset = manager.get(table_name)

        if dataset:
            table_general = PrettyTable(['Property','Value'])
            table_general.align = "l"

            table_general.add_row(['name', dataset.name])
            table_general.add_row(['row_count', "{:,}".format(dataset.table.row_count)])
            table_general.add_row(['size', prettyMBprint(dataset.table.size)])
            table_general.add_row(['likes', dataset.likes])
            table_general.add_row(['locked', dataset.locked])
            table_general.add_row(['privacy', dataset.privacy])
            table_general.add_row(['description', dataset.description])
            table_general.add_row(['license', dataset.license])
            table_general.add_row(['attributions', dataset.attributions])
            table_general.add_row(['tags', dataset.tags])
            click.echo(table_general.get_string())
    except Exception as e:
        click.echo("Table is not CartoDBfied")

    click.echo('\r\n## Schema\r\n')
    ctx.invoke(schema, format = 'pretty', table_name = table_name)

    click.echo('\r\n## Indexes\r\n')
    ctx.invoke(indexes, format = 'pretty', table_name = table_name)

    click.echo('\r\n## Triggers\r\n')
    ctx.invoke(triggers, format = 'pretty', table_name = table_name)



@click.command(help="Download a dataset")
@click.help_option('-h', '--help')
@click.option('-f','--format',default="gpkg",help="Format of your results",
    type=click.Choice(['gpkg','csv', 'shp','geojson']))
@click.option('-o','--output',type=click.File('wb'),
              help="Output file to generate")
@click.argument('table_name')
@click.pass_context
def download(ctx, format, output, table_name):
    carto_obj = ctx.obj['carto']
    
    # Check table size
    sql = "select count(*) from {}".format(table_name)
    result = carto_obj.execute_sql(sql)
    counts = int(result['rows'][0]['count'])

    if counts > SPLIT_EXPORT:
        click.echo("Table is too big ({}), we need to download it in chunks of {} rows".format(counts, SPLIT_EXPORT))
        ind = 1
        base, ext = os.path.splitext(output.name)
        for i in range(1,counts,SPLIT_EXPORT):
            sql = '''
                    select * 
                      from {table_name}
                     order by cartodb_id
                     limit {limit} 
                    offset {offset}
                  '''.format(
                        table_name = table_name,
                        limit = SPLIT_EXPORT,
                        offset = i)
            output = open('{}_{}{}'.format(base,ind,ext),'wb')
            ctx.invoke(run_sql,
                format = format,
                output = output ,
                explain = False,
                explain_analyze = False,
                sql = sql)

            click.echo("Chunk {} exported to {}".format(ind,output.name))
            ind = ind + 1

    else:
        ctx.invoke(run_sql,
            format = format,
            output = output,
            explain = False,
            explain_analyze = False,
            sql = "select * from {}".format(table_name))
        click.echo("Table {} exported to {}".format(table_name,output.name))



@click.command(help="Upload a new dataset from a file on your computer")
@click.help_option('-h', '--help')
@click.option('-s','--sync',default=None,help="Seconds between sync updates",
    type=int)
@click.argument('path')
@click.pass_context
def upload(ctx, sync, path):
    carto_obj = ctx.obj['carto']

    # Check the resource
    if path[:4] == 'http':
        sync_manager = carto_obj.get_sync_manager()
        if sync:
            task = sync_manager.create(path,sync)
            click.echo("You can safely abort now if you don't want to wait for the import to finish")

            # Check the import
            sync_id = task.get_id()
            while(task.state != 'success'):
                time.sleep(5)
                click.echo("Checking status of the import...")
                task.refresh()
                if (task.state == 'failure'):
                    print('The error code is: ' + str(task.error_code))
                    print('The error message is: ' + str(task.error_message))
                    break
            click.echo("Dataset imported!")
        else:
            task = carto_obj.upload(path)


    elif os.path.exists(path):
        task = carto_obj.upload(path)
        click.echo("Local resource uploaded!")
    else:
        ctx.fail("The resource provided is not a valid URL or an existing file")


@click.command(help="Deletes a dataset from your account")
@click.help_option('-h', '--help')
@click.argument('table_name')
@click.pass_context
def delete(ctx, table_name):
    carto_obj = ctx.obj['carto']
    dataset_manager = carto_obj.get_dataset_manager();
    dataset = dataset_manager.get(table_name)
    if dataset:
        dataset.delete()
        click.echo("Dataset deleted!")
    else:
        ctx.fail('The dataset does not exist!')


@click.command(help="Edit dataset properties")
@click.help_option('-h', '--help')
@click.option('-d', '--description', help="Add a meaninful description to your tables",
    type=str)
@click.option('-p', '--privacy', help="Set the privacy of your dataset",
    type=click.Choice(['PRIVATE','LINK','PUBLIC'])
    )
@click.option('-c', '--locked', help="Lock your dataset",default= None, type=bool)
@click.option('-l', '--license', help="Set your dataset license")
@click.option('-a', '--attributions', help="Set your dataset attributions")
@click.option('-t', '--tags', help="Set your dataset tags, use commas to separate them")
@click.argument('dataset_name')
@click.pass_context
def edit(ctx, description, privacy, locked, license, attributions, tags, dataset_name):
    carto_obj = ctx.obj['carto']
    dataset_manager = carto_obj.get_dataset_manager()
    try:
        dataset = dataset_manager.get(dataset_name)
        if privacy:
            if privacy == 'PRIVATE':
                dataset.privacy = PRIVATE
            elif privacy == 'LINK':
                dataset.privacy = LINK
            elif privacy == 'PUBLIC':
                dataset.privacy = PUBLIC
        if locked is not None:
            dataset.locked = locked
        if description:
            dataset.description = description
        if license:
            dataset.license = license
        if attributions:
            dataset.attributions = attributions
        if tags:
            dataset.tags = tags.split(',')

        dataset.save()
        click.echo("Dataset edited!")
    except:
        ctx.fail('The dataset does not exist!')

@click.command(help="Renames a dataset from your account")
@click.help_option('-h', '--help')
@click.argument('old')
@click.argument('new')
@click.pass_context
def rename(ctx, old, new):
    carto_obj = ctx.obj['carto']
    dataset_manager = carto_obj.get_dataset_manager();
    dataset = dataset_manager.get(old)
    if dataset:
        dataset.name = new
        dataset.save()
        click.echo("Dataset renamed!")
    else:
        ctx.fail('The dataset does not exist!')



@click.command(help="Merges a number of datasets")
@click.help_option('-h', '--help')
@click.argument('table_name_prefix')
@click.argument('new_table_name')
@click.pass_context
def merge(ctx, table_name_prefix,new_table_name):
    carto_obj = ctx.obj['carto']
    # get the list of tables
    sql = queries.LIST_TABLES.format(schema_name=carto_obj.user_name,table_name='{}%'.format(table_name_prefix))
    result = carto_obj.execute_sql(sql)
    tables = [row['name'] for row in result['rows']]

    click.echo("Tables to merge:")
    for table in tables:
        click.echo("\t{}".format(table))


    # get the list of columns from the first table
    sql = queries.SCHEMA.format(table_name=tables[0])
    result = carto_obj.execute_sql(sql)
    columns = ",".join([row['attribute'] for row in result['rows'] if row['attribute'] != 'cartodb_id'])

    # build the list of queries
    query_list = [
        'CREATE TABLE {} AS SELECT {} FROM {}'.format(new_table_name,columns,tables[0]),
    ];
    for table in tables[1:]:
        query_list.append('''INSERT INTO {first_table} SELECT {columns} FROM {table}'''.format(
                first_table = new_table_name,
                columns = columns,
                table = table
            ))

    # add cartodbfication of the new table
    query_list.append(get_cartodbfy_query(org=carto_obj.org_name,
        user=carto_obj.user_name,
        table_name = new_table_name))

    # start a batch sql api job
    job_details = carto_obj.batch_create(query_list)
    click.echo("Batch SQL API job launched to merge all tables")
    click.echo(job_details['job_id'])

@click.command(help="Runs the cartodbfication of a table to convert it into a dataset")
@click.help_option('-h', '--help')
@click.argument('table_name')
@click.pass_context
def cartodbfy(ctx, table_name):
    carto_obj = ctx.obj['carto']
    job_details = carto_obj.batch_create(get_cartodbfy_query(
        org=carto_obj.org_name,
        user=carto_obj.user_name,
        table_name = table_name
        ))
    click.echo("Batch SQL API job launched to cartodbfy the table")
    click.echo(job_details['job_id'])
