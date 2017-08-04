import click
import json
import re

from carto_cli.carto import queries


@click.command(help="Display the ids of all your running jobs")
@click.help_option('-h', '--help')
@click.pass_context
def list(ctx):
    '''
    Reads using SQL API the list of batch API jobs
    leveraging that the JOB_ID is inside a comment
    '''
    carto_obj = ctx.obj['carto']
    sql = queries.CURRENT_RUNNING
    try:
        query = carto_obj.execute_sql(sql,format='json')
        regex = "\/\*\ ([0-9a-z]*-[0-9a-z]*-[0-9a-z]*-[0-9a-z]*-[0-9a-z]*)\ \*\/"
        for row in query['rows']:
            for result in re.findall(regex,row['query']):
                click.echo(result)

    except Exception as e:
        ctx.fail("Error executing your SQL: {}".format(e))



@click.command(help="Returns details about a job id (JSON)")
@click.argument('job_id')
@click.help_option('-h', '--help')
@click.pass_context
def read(ctx,job_id):
    '''
    Just returns the details of a job using as a JSON
    '''
    carto_obj = ctx.obj['carto']
    try:
        job_details = carto_obj.batch_check(job_id)
        click.echo(json.dumps(job_details))
    except Exception as e:
        ctx.fail(e)



@click.command(help="Creates a new job and returns its ID")
@click.argument('sql', nargs=-1)
@click.help_option('-h', '--help')
@click.pass_context
def create(ctx,sql):
    '''
    Creates a new job and returns it's ID
    '''
    carto_obj = ctx.obj['carto']
    if type(sql) == tuple:
        sql = ' '.join(sql)

    job_details = carto_obj.batch_create(sql)

    click.echo(job_details['job_id'])



@click.command(help="Cancels a job")
@click.argument('job_id')
@click.help_option('-h', '--help')
@click.pass_context
def cancel(ctx,job_id):
    '''
    Just returns the details of a job using as a JSON
    '''
    carto_obj = ctx.obj['carto']

    job_details = carto_obj.batch_cancel(job_id)

    click.echo(json.dumps(job_details))