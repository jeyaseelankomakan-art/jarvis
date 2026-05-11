"""Command-line interface for OpenJarvis (Click-based)."""

from __future__ import annotations

import importlib

import click

import openjarvis

_COMMAND_SPECS: dict[str, tuple[str, str]] = {
    "add": ("openjarvis.cli.add_cmd", "add"),
    "agents": ("openjarvis.cli.agent_cmd", "agent"),
    "ask": ("openjarvis.cli.ask", "ask"),
    "bench": ("openjarvis.cli.bench_cmd", "bench"),
    "channel": ("openjarvis.cli.channel_cmd", "channel"),
    "channels": ("openjarvis.cli.channels_cmd", "channels"),
    "chat": ("openjarvis.cli.chat_cmd", "chat"),
    "compose": ("openjarvis.cli.compose_cmd", "compose"),
    "config": ("openjarvis.cli.config_cmd", "config"),
    "connect": ("openjarvis.cli.connect_cmd", "connect"),
    "deep-research-setup": ("openjarvis.cli.deep_research_setup_cmd", "deep_research_setup"),
    "digest": ("openjarvis.cli.digest_cmd", "digest"),
    "doctor": ("openjarvis.cli.doctor_cmd", "doctor"),
    "eval": ("openjarvis.cli.eval_cmd", "eval_group"),
    "feedback": ("openjarvis.cli.feedback_cmd", "feedback_group"),
    "gateway": ("openjarvis.cli.gateway_cmd", "gateway"),
    "host": ("openjarvis.cli.host_cmd", "host"),
    "init": ("openjarvis.cli.init_cmd", "init"),
    "learning": ("openjarvis.learning.distillation.cli", "learning_group"),
    "memory": ("openjarvis.cli.memory_cmd", "memory"),
    "model": ("openjarvis.cli.model", "model"),
    "operators": ("openjarvis.cli.operators_cmd", "operators"),
    "optimize": ("openjarvis.cli.optimize_cmd", "optimize_group"),
    "quickstart": ("openjarvis.cli.quickstart_cmd", "quickstart"),
    "registry": ("openjarvis.cli.registry_cmd", "registry"),
    "research": ("openjarvis.cli.deep_research_setup_cmd", "deep_research_setup"),
    "scan": ("openjarvis.cli.scan_cmd", "scan"),
    "scheduler": ("openjarvis.cli.scheduler_cmd", "scheduler"),
    "serve": ("openjarvis.cli.serve", "serve"),
    "skill": ("openjarvis.cli.skill_cmd", "skill"),
    "telemetry": ("openjarvis.cli.telemetry_cmd", "telemetry"),
    "tool": ("openjarvis.cli.tool_cmd", "tool"),
    "vault": ("openjarvis.cli.vault_cmd", "vault"),
    "workflow": ("openjarvis.cli.workflow_cmd", "workflow"),
    "start": ("openjarvis.cli.daemon_cmd", "start"),
    "stop": ("openjarvis.cli.daemon_cmd", "stop"),
    "restart": ("openjarvis.cli.daemon_cmd", "restart"),
    "status": ("openjarvis.cli.daemon_cmd", "status"),
}


class LazyGroup(click.Group):
    def list_commands(self, ctx: click.Context):
        return sorted(_COMMAND_SPECS)

    def get_command(self, ctx: click.Context, cmd_name: str):
        spec = _COMMAND_SPECS.get(cmd_name)
        if spec is None:
            return None
        module_name, attr_name = spec
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            return None
        return getattr(module, attr_name)


@click.group(cls=LazyGroup, help="OpenJarvis — modular AI assistant backend")
@click.version_option(version=openjarvis.__version__, prog_name="jarvis")
@click.option("--verbose", is_flag=True, default=False, help="Enable debug logging")
@click.option("--quiet", is_flag=True, default=False, help="Suppress non-error output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """Top-level CLI group."""
    from openjarvis.cli.log_config import setup_logging

    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    setup_logging(verbose=verbose, quiet=quiet)

    # Check for updates on interactive commands
    if not quiet and ctx.invoked_subcommand:
        from openjarvis.cli._version_check import check_for_updates

        check_for_updates(ctx.invoked_subcommand)


def main() -> None:
    """Entry point registered as ``jarvis`` console script."""
    cli()


__all__ = ["cli", "main"]
