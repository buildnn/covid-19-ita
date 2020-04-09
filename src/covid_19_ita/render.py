from os.path import join, dirname, abspath
import json
import yaml
from markdown import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape, meta
import click

default_template_dir = join(dirname(abspath(__file__)), "templates")


def list_template_variables(template_name, env):
    template_source = env.loader.get_source(env, template_name)[0]
    parsed_content = env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)


def render_from_configfile(configfile, output, template_dir):

    print("{} -> {}".format(configfile, output))

    if not template_dir:
        template_dir = default_template_dir

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

    with open(output, "w",) as outfile:
        rendered = env.get_template(template).render(**variables)
        outfile.write(rendered)


# --- CLI ---


@click.command()
@click.argument("configfile", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--template-dir", type=click.Path(exists=True), default=None)
def from_config(configfile, output, template_dir):
    render_from_configfile(
        configfile=configfile,
        output=output,
        template_dir=template_dir,
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
