import sys

import click

from hotdag import HotDAG
from hotdag.manifest import manifest_loaders
from hotdag.renderer import renderers


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--input", type=click.Choice(list(manifest_loaders.keys())), required=True
)
@click.option("--output", type=click.Choice(list(renderers.keys())), default="text")
@click.option("--file", type=click.Path())
@click.option("--url", type=str)
@click.option("--account-id", type=int)
@click.option("--job-id", type=int)
@click.option("--select")
@click.option("--exclude")
def select(input, output, file, url, account_id, job_id, select, exclude):
    """Evaluate a dbt selector against a manifest."""

    manifest_loader = manifest_loaders[input]()

    if input == "file":
        if file is None:
            raise Exception("The --file option is required when --input is file.")

        manifest_args = {"file": open(file)}

    elif input == "stdin":
        manifest_args = {"file": sys.stdin}

    elif input == "url":
        if url is None:
            raise Exception("The --url option is required when --input is url.")

        manifest_args = {"url": url}

    elif input == "dbt_cloud":
        if account_id is None or job_id is None:
            raise Exception(
                "Both the --account-id and --job-id options are required when --input is dbt_cloud."
            )

        manifest_args = {"account_id": account_id, "job_id": job_id}

    else:
        manifest_args = {}

    renderer = renderers[output]()

    hotdag = HotDAG(manifest_loader=manifest_loader, renderer=renderer)

    hotdag.load_manifest(**manifest_args)
    selection = hotdag.get_selection(select, exclude)
    output: str = hotdag.render(selection)
    print(output)


@cli.command()
@click.option("--port", type=int, default=8000)
def serve(port: int):
    """Run a server interactive selector processing via APi."""
    import uvicorn

    uvicorn.run("hotdag.server.server:get_application", port=port, log_level="info")


if __name__ == "__main__":
    cli()
