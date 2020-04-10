from os.path import join, dirname, abspath
import json
from pprint import pformat
from datetime import datetime
import logging

import click
import yaml
from markdown import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape, meta
import click

from . import TEMPLATES_DIR, CONFIG_DIR

logger = logging.getLogger("covid_19_ita")


def list_template_variables(template_name, env):
    template_source = env.loader.get_source(env, template_name)[0]
    parsed_content = env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)


def render_from_configfile(configfile, template_dir=None, desc_dir=None):

    if not template_dir:
        template_dir = TEMPLATES_DIR

    if not desc_dir:
        desc_dir = CONFIG_DIR

    print(f"loading templates from: {template_dir}")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(
            set(["html", "xml", "md", "js", "css", "json", "csv"])
        ),
    )

    with open(configfile, "r") as config_file_in:
        config_ext = configfile.rsplit(".")[-1]
        if config_ext == "json":
            config_vars = json.load(config_file_in)
        elif config_ext in ["yml", "yaml"]:
            config_vars = yaml.load(
                config_file_in, Loader=yaml.loader.BaseLoader
            )
        else:
            raise NotImplementedError(
                "configfile must be yaml or json. You provided "
                "'{}' extension.".format(config_vars)
            )

    if "desc_file" in config_vars.keys():
        desc_file = config_vars.pop("desc_file")
        desc_file = join(desc_dir, desc_file)

        with open(desc_file, "r") as desc_file_in:
            desc_ext = desc_file.rsplit(".")[-1]
            if desc_ext == "md":
                desc = markdown(desc_file_in.read())
            else:
                raise NotImplementedError("desc file can only be `.md`.")
        print("description:", desc[:500])
    else:
        desc = ""

    template = config_vars.pop("template")
    template_variables = list_template_variables(template, env)

    print(template_variables)

    variables = config_vars["variables"]
    variables["mark_text"] = desc

    rendered = env.get_template(template).render(**variables)

    return rendered


def save_render(rendered, output):
    with open(output, "w",) as outfile:
        outfile.write(rendered)


# --- CLI ---


@click.command()
@click.argument("configfile", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--template-dir", type=click.Path(exists=True), default=None)
@click.option("--desc-dir", type=click.Path(exists=True), default=None)
@click.option(
    "--log",
    type=click.STRING,
    default="INFO",
    help="one of DEBUG, INFO, WARNING, ERROR, FATAL",
)
def from_config(configfile, output, template_dir, desc_dir, log):
    logging.basicConfig(level=getattr(logging, log, "INFO"))

    start = datetime.now()
    logger.info(">>> {} -> {}".format(configfile, output))

    rendered = render_from_configfile(
        configfile=configfile, template_dir=template_dir, desc_dir=desc_dir,
    )

    save_render(rendered, output)

    logger.info(
        ">>> output {} created in {}.".format(output, datetime.now() - start)
    )


@click.group()
def cli():
    """ Runs report processing script to turn raw template from (./reports/templates) into
        cleaned report ready to be analyzed (saved in ./reports).
    """
    pass


def main():
    cli.add_command(from_config)
    cli()


if __name__ == "__main__":
    main()
