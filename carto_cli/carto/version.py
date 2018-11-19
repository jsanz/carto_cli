import click

CARTO_CLI_VERSION='0.0.3'

@click.command(help='Prints the version of this application')
@click.help_option('-h', '--help')
@click.pass_context
def version(ctx):
    click.echo(CARTO_CLI_VERSION)
