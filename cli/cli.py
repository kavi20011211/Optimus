import click
import subprocess
import sys
import os

BANNER = r"""
     ______   ______   _________  ________  ___ __ __   __  __   ______
    /_____/\ /_____/\ /________/\/_______/\/__//_//_/\ /_/\/_/\ /_____/\
    \:::_ \ \\:::_ \ \\__.::.__\/\__.::._\/\::\| \| \ \\:\ \:\ \\::::_\/_
     \:\ \ \ \\:(_) \ \  \::\ \     \::\ \  \:.      \ \\:\ \:\ \\:\/___/\
      \:\ \ \ \\: ___\/   \::\ \    _\::\ \__\:.\-/\  \ \\:\ \:\ \\_::._\:\
       \:\_\ \ \\ \ \      \::\ \  /__\::\__/\\. \  \  \ \\:\_\:\ \ /____\:\
        \_____\/ \_\/       \__\/  \________\/ \__\/ \__\/ \_____\/ \_____\/
"""


def print_banner():
    click.echo(click.style(BANNER, fg="cyan", bold=True))
    click.echo(click.style("  Optimus MCP Server", fg="bright_white", bold=True) +
               click.style(" | ", fg="bright_black") +
               click.style("@brightseid", fg="magenta", bold=True) +
               click.style(" | ", fg="bright_black") +
               click.style("v0.0.1\n", fg="yellow"))


def print_commands():
    click.echo(click.style("  Available Commands:", fg="bright_white", bold=True))
    commands = [
        ("start", "Start the Optimus MCP server"),
        ("read ",  "Read a file from the workspace"),
        ("write", "Write content to a file in the workspace"),
        ("run  ", "Run a shell command inside the workspace"),
    ]
    for cmd, desc in commands:
        click.echo(
            click.style(f"    optimus {cmd}", fg="green") +
            click.style(f"  {desc}", fg="bright_black")
        )
    click.echo()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print_banner()
        print_commands()


@cli.command()
@click.option("--workdir", "-w", default=".", show_default=True, help="Working directory for the agent")
@click.option("--safe", "-s", is_flag=True, default=False, help="Run in safe mode (disables shell=True)")
def start(workdir, safe):
    """Start the Optimus MCP server"""
    print_banner()
    click.echo(click.style("  Starting server...\n", fg="bright_white", bold=True))
    click.echo(click.style("  Workdir   : ", fg="bright_black") + click.style(os.path.abspath(workdir), fg="cyan"))
    click.echo(click.style("  Safe mode : ", fg="bright_black") + click.style(str(safe), fg="green" if safe else "yellow"))
    click.echo()

    env = os.environ.copy()
    env["OPTIMUS_WORKDIR"] = os.path.abspath(workdir)
    env["OPTIMUS_SAFE"] = "true" if safe else "false"

    subprocess.run([sys.executable, "server.py"], env=env)


@cli.command()
@click.argument("path")
@click.option("--workdir", "-w", default=".", help="Working directory")
def read(path, workdir):
    """Read a file from the workspace"""
    full_path = os.path.join(os.path.abspath(workdir), path)
    click.echo(click.style(f"\n  Reading: {full_path}\n", fg="cyan"))
    try:
        with open(full_path, "r") as f:
            click.echo(f.read())
    except FileNotFoundError:
        click.echo(click.style(f"\n  Error: File not found: {full_path}", fg="red", bold=True))
        sys.exit(1)


@cli.command()
@click.argument("path")
@click.argument("content")
@click.option("--workdir", "-w", default=".", help="Working directory")
def write(path, content, workdir):
    """Write content to a file in the workspace"""
    full_path = os.path.join(os.path.abspath(workdir), path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    click.echo(click.style(f"\n  ✔ Written to {full_path}\n", fg="green", bold=True))


@cli.command()
@click.argument("command")
@click.option("--workdir", "-w", default=".", help="Working directory")
def run(command, workdir):
    """Run a shell command inside the workspace"""
    cwd = os.path.abspath(workdir)
    click.echo(click.style(f"\n  Running: ", fg="bright_black") + click.style(command, fg="cyan") +
               click.style(f" in {cwd}\n", fg="bright_black"))

    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        click.echo(click.style(result.stdout, fg="bright_white"))
    if result.stderr:
        click.echo(click.style(result.stderr, fg="yellow"))


if __name__ == "__main__":
    cli()