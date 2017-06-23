import click
import json
from prettytable import PrettyTable

@click.command(help="Display all your dataset names")
@click.option('-o','--output',type=click.File('w'),
              help="Output file to generate instead of printing directly")
@click.option('-p','--pretty',default=False,is_flag=True, help="Formats only some relevant fields for easy reading")
@click.help_option('-h', '--help')
@click.pass_context
def list(ctx,output,pretty):
    carto_obj = ctx.obj['carto']

    sql = "select pg_class.relname from pg_class, pg_roles, pg_namespace where pg_roles.oid = pg_class.relowner and pg_roles.rolname = current_user and pg_namespace.oid = pg_class.relnamespace and pg_class.relkind = 'r'  order by relname"

    try:
        if pretty:
            query = carto_obj.execute_sql(sql,format='json')
            table_general = PrettyTable(['Table Name'])
            table_general.align = "l"
            for row in query['rows']:
                table_general.add_row([row['relname']])
            result = table_general.get_string()

        else:
            result = carto_obj.execute_sql(sql,format='csv')
        if output:
            output.write(result)
        else:
            click.echo(result,nl=pretty)
    except Exception as e:
        ctx.fail("Error executing your SQL: {}".format(e))
