import click
import json
import warnings
import csv

from prettytable import PrettyTable
from carto_cli.carto import queries

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

warnings.filterwarnings('ignore')

def get_dataset(name, datasets):
    for dataset in datasets:
        if dataset.name == name:
            return dataset


@click.command(help="Display all your CARTO datasets")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.pass_context
def list(ctx, format):
    carto_obj = ctx.obj['carto']
    manager = carto_obj.get_dataset_manager()
    try:
        datasets = manager.all()
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
        else:
            table_general = PrettyTable(
                ['Table Name', 'Privacy', 'Locked', 'Likes', 'Size',
                 'Rows', 'Tags'])
            table_general.align = "r"
            table_general.align['Table Name'] = "l"
            table_general.align['Privacy'] = "c"
            table_general.align['Tags'] = "l"

            for row in results:
                if row['size']:
                    row_size_val = int(row['size']) / (1024.0*1024)
                    row_size = "{:.2f} MB".format(row_size_val)
                else:
                    row_size = row['size']

                table_general.add_row([
                    row['name'],
                    row['privacy'],
                    row['locked'],
                    row['likes'],
                    row_size_val,
                    row['row_count'],
                    ", ".join(row['tags'])
                ])

            raw_result = table_general.get_string()

        click.echo(raw_result, nl=format in ['json', 'pretty'])
    except Exception as e:
        ctx.fail("Error retrieving the list of datasets: {}".format(e))


@click.command(help="List tables and their main Postgres statistics")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.pass_context
def list_tables(ctx, format):
    carto_obj = ctx.obj['carto']
    sql = queries.LIST_TABLES.format(schema_name=carto_obj.user_name,table_name='%')
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
            table_general.add_row(['row_count', dataset.table.row_count])
            table_general.add_row(['size', dataset.table.size])
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

