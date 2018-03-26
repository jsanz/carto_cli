import click
import json
import csv

from prettytable import PrettyTable
from carto_cli.carto import queries

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

@click.command(help="Execute a SQL passed as a string")
@click.option('-f','--format',default="json",help="Format of your results",
    type=click.Choice(['csv', 'shp','json','gpkg','geojson']))
@click.option('-o','--output',type=click.File('wb'),
              help="Output file to generate instead of printing directly")
@click.option('-e','--explain',is_flag=True,default=False,help="Explains the query")
@click.option('-ea','--explain-analyze',is_flag=True,default=False,help="Explains the query executing it")
@click.option('-eaj','--explain-analyze-json',is_flag=True,default=False,help="Explains the query executing it and return as a JSON")
@click.help_option('-h', '--help')
@click.argument('sql', nargs=-1)
@click.pass_context
def run(ctx,format,output,explain,explain_analyze,explain_analyze_json,sql):
    carto_obj = ctx.obj['carto']
    if type(sql) == tuple:
        sql = ' '.join(sql)
    try:
        if explain:
            sql = "EXPLAIN " + sql
            format = 'json'
        elif explain_analyze:
            sql = "EXPLAIN ANALYZE " + sql
            format = 'json'
        elif explain_analyze_json:
            sql = "EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON) " + sql
            format = 'json'

        result = carto_obj.execute_sql(sql,format=format,do_post=True)

        if explain or explain_analyze:
            result = '\r\n'.join([row['QUERY PLAN'] for row in result['rows']])
        elif explain_analyze_json:
            result = json.dumps(result['rows'][0]['QUERY PLAN'])
        elif format in ['json','geojson']:
            result = json.dumps(result)

        if output:
            output.write(result)
        else:
            click.echo(result,nl=format=='json')
    except Exception as e:
        ctx.fail("Error executing your SQL: {}".format(e))


@click.command(help="Kills a query based on its pid")
@click.argument('pid',type=int)
@click.help_option('-h', '--help')
@click.pass_context
def kill(ctx,pid):
    carto_obj = ctx.obj['carto']
    sql = queries.KILL_QUERY.format(pid)

    try:
        result = carto_obj.execute_sql(sql)
        if 'rows' in result and len(result['rows']) > 0:
            cancelling = result['rows'][0]['pg_cancel_backend']

            if cancelling:
                click.echo('Query cancelled')
            else:
                ctx.fail('Invalid PID?')
        else:
            raise
    except Exception as e:
        ctx.fail("Error cancelling the query: {}".format(e))



@click.command(help="Functions on your account")
@click.option('-f', '--format', default="json",
              help="Format of your results (JSON output includes definition)",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.pass_context
def functions(ctx,format):
    carto_obj = ctx.obj['carto']
    sql = queries.FUNCTIONS
    result = carto_obj.execute_sql(sql)

    if format == 'json':
        raw_result = json.dumps(result['rows'])
    elif format == 'csv':
        with StringIO() as csvfile:
            fieldnames = queries.FUNCTIONS_HEADER
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in result['rows']:
                arg_array = row['arguments']
                if arg_array and len(arg_array) > 0:
                    arg_str = ', '.join(arg_array)
                else:
                    arg_str = None

                writer.writerow({
                    'oid' : row['oid'],
                    'name' : row['name'],
                    'arguments': arg_str
                })

            raw_result = csvfile.getvalue()
    else:
        table_general = PrettyTable(queries.FUNCTIONS_HEADER)
        table_general.align = "l"

        #import ipdb; ipdb.set_trace()
        for row in result['rows']:
            pretty_row = []

            arg_array = row['arguments']
            if arg_array and len(arg_array) > 0:
                row['arguments'] = ', '.join(arg_array)
            else:
                row['arguments'] = ''

            for key in queries.FUNCTIONS_HEADER:
                pretty_row.append(row[key])
            table_general.add_row(pretty_row)

        raw_result = table_general.get_string()

    click.echo(raw_result, nl=format in ['json', 'pretty'])


@click.command(help="List your organization schemas")
@click.option('-f', '--format', default="json", help="Format of your results",
              type=click.Choice(['json', 'csv', 'pretty']))
@click.help_option('-h', '--help')
@click.pass_context
def schemas(ctx,format):
    carto_obj = ctx.obj['carto']
    sql = queries.LIST_SCHEMAS
    result = carto_obj.execute_sql(sql)

    if format == 'json':
        raw_result = json.dumps(result['rows'])
    elif format == 'csv':
        with StringIO() as csvfile:
            fieldnames = ['user']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in result['rows']:
                writer.writerow(row)
            raw_result = csvfile.getvalue()
    else:
        table_general = PrettyTable(['user'])
        table_general.align = "l"

        #import ipdb; ipdb.set_trace()
        for row in result['rows']:
            table_general.add_row([row['user']])

        raw_result = table_general.get_string()

    click.echo(raw_result, nl=format in ['json', 'pretty'])
