import os
import tempfile
import sys
import click

from werkzeug.serving import run_simple

def make_app():
    from shorty.application import Shorty

    # return Shorty("mysql+mysqlconnector://root@localhost:3306/bluebiz")
    return Shorty("mysql+mysqlconnector://dbmasteruser:EDl=uo(*k^(0wzc+>aor[J*R`&yS_smS@ls-ecdee0357dd59b21c7ea5b0c99864d4255ce680b.co3jgj7mhva9.eu-west-3.rds.amazonaws.com:3306/bluebiz")

def make_shell():
    from shorty import models, utils

    application = make_app()
    return {"application": application, "models": models, "utils": utils}


@click.group()
def cli():
    pass

@cli.command()
@click.option("-e", "--email", type=str, default="bluebiz.admin@gmail.com", help="bluebize.admin@gmail.com")
@click.option("-p", "--password", type=str, default="Mrpi3yo! BIlivvm.", help="Mrpi3yo! BIlivvm.")
def createsuper(email, password):
    make_app().create_superuser(email, password)

@cli.command()
def initdb():
    make_app().init_database()


@cli.command()
@click.option("-h", "--hostname", type=str, default="localhost", help="localhost")
@click.option("-p", "--port", type=int, default=5000, help="5000")
@click.option("--no-reloader", is_flag=True, default=False)
@click.option("--debugger", is_flag=True)
@click.option("--no-evalex", is_flag=True, default=False)
@click.option("--threaded", is_flag=True)
@click.option("--processes", type=int, default=1, help="1")
def runserver(hostname, port, no_reloader, debugger, no_evalex, threaded, processes):
    """Start a new development server."""
    app = make_app()
    reloader = not no_reloader
    evalex = not no_evalex
    run_simple(
        hostname,
        port,
        app,
        use_reloader=reloader,
        use_debugger=debugger,
        use_evalex=evalex,
        threaded=threaded,
        processes=processes,
    )


@cli.command()
@click.option("--no-ipython", is_flag=True, default=False)
def shell(no_ipython):
    """Start a new interactive python session."""
    banner = "Interactive Werkzeug Shell"
    namespace = make_shell()
    if not no_ipython:
        try:
            try:
                from IPython.frontend.terminal.embed import InteractiveShellEmbed

                sh = InteractiveShellEmbed.instance(banner1=banner)
            except ImportError:
                from IPython.Shell import IPShellEmbed

                sh = IPShellEmbed(banner=banner)
        except ImportError:
            pass
        else:
            sh(local_ns=namespace)
            return
    from code import interact

    interact(banner, local=namespace)


if __name__ == "__main__":
    cli()
