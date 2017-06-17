import click
import os.path
import yaml


default_config_file = os.path.join(os.path.expanduser("~"), '.cartorc.yaml')


@click.group(help='Allows you to get the account details')
@click.option('-c', '--config-file', type=click.File('r'),
              default=default_config_file,
              help="Configuration file to read, defaults to ~/.cartorc.yaml")
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
@click.pass_context
def list(ctx):
    '''
    List the users in the configuration file
    '''
    for user in ctx.obj['config']:
        click.echo(user)


@cli.command(help='Returns the user names that match the given string')
@click.argument('search')
@click.pass_context
def search(ctx, search):
    '''
    Search for a string in the configuration file
    '''
    for user in ctx.obj['config']:
        if user.find(search) > -1:
            click.echo(user)


@cli.command(help='The user wou want to retrieve')
@click.argument('user')
@click.pass_context
def load(ctx, user):
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

        click.echo('''
 export CARTO_USER={user}
 export CARTO_API_KEY={api_key}
 export CARTO_API_URL={url}'''.format(user=user, org=org, api_key=api_key, url=url))

        if org != None:
            click.echo(' export CARTO_ORG={org}'.format(org=org))


if __name__ == '__main__':
    cli(obj={})
