import click
import os.path
import yaml

from .carto.version import version

default_config_file = os.environ.get(
    'CARTO_DB', os.path.join(os.path.expanduser("~"), '.cartorc.yaml'))


@click.group(help='Allows you to get the account details')
@click.option('-c', '--config-file', type=click.File('r'),
              default=default_config_file,
              help="Configuration file to read, defaults to ~/.cartorc.yaml " +
                   "or the environment variable $CARTO_DB")
@click.help_option('-h', '--help')
@click.pass_context
def cli(ctx, config_file):
    '''
    Main function to handle the command, it just parses the configuration file
    '''
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj['config'] = yaml.load(config_file.read())


@cli.command(help='List your stored users')
@click.help_option('-h', '--help')
@click.pass_context
def list(ctx):
    '''
    List the users in the configuration file
    '''
    for user in ctx.obj['config']:
        click.echo(user)


@cli.command(help='Returns the user names that match the given string')
@click.argument('search')
@click.help_option('-h', '--help')
@click.pass_context
def search(ctx, search):
    '''
    Search for a string in the configuration file
    '''
    for user in ctx.obj['config']:
        if user.find(search) > -1:
            click.echo(user)


@cli.command(help='The user wou want to retrieve')
@click.option('-o', '--output-file', type=click.File('w'), envvar='CARTO_ENV',
              help="Output file to store the export commands, it can use the" +
                   " $CARTO_ENV environment variable")
@click.argument('user')
@click.help_option('-h', '--help')
@click.pass_context
def load(ctx, output_file, user):
    '''
    Tries to load the information as a easy copy&paste set of env vars
    '''
    config = ctx.obj['config']
    if not user in config:
        ctx.fail('User not found on config')
    else:
        user_config = config[user]
        api_key = user_config['api_key']
        if 'organization' in user_config:
            org = user_config['organization']
        else:
            org = None

        if 'url' in user_config:
            url = user_config['url']
        else:
            url = 'https://{}.carto.com/'.format(user)

        result = '''
export CARTO_USER="{user}"
export CARTO_API_KEY="{api_key}"
export CARTO_API_URL="{url}"'''.format(user=user, org=org, api_key=api_key, url=url)

        if org != None:
            result = result + '\nexport CARTO_ORG="{org}"'.format(org=org)

        if 'check_ssl' in user_config:
            result = result + '\nexport CARTO_CHECK_SSL="{}"'.format(user_config['check_ssl'])

        result = result + '\n'

        if output_file:
            output_file.write(result)
        else:
            click.echo(result)

cli.add_command(version)

if __name__ == '__main__':
    cli(obj={})
