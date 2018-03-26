import click
import json
from prettytable import PrettyTable


from carto_cli.carto import queries as carto_queries

QUERY_FIELDS = [
    ('pid','pid'),
    ('state','State'),
    ('query_start','Query start'),
    ('application_name','Application'),
    ('query','Query')
]

@click.command(help="Shows the current running queries")
@click.option('-o','--output',type=click.File('w'),
              help="Output file to generate instead of printing directly")
@click.option('-p','--pretty',default=False,is_flag=True, help="Formats only some relevant fields for easy reading")
@click.help_option('-h', '--help')
@click.pass_context
def queries(ctx,output,pretty):
    carto_obj = ctx.obj['carto']
    sql = carto_queries.CURRENT_RUNNING
    try:
        query = carto_obj.execute_sql(sql,format='json')

        if pretty:
            fields = [item[0] for item in QUERY_FIELDS]
            titles = [item[1] for item in QUERY_FIELDS]
            table_general = PrettyTable(titles)

            for row in query['rows']:
                table_general.add_row([row[field] for field in fields])
            result = str(table_general)
        else:
            result = json.dumps(query['rows'])

        if output:
            output.write(result)
        else:
            click.echo(result)
    except Exception as e:
        ctx.fail("Error executing your SQL: {}".format(e))
