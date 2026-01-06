
import os
import asyncio
import logging
import re
import sys
from pathlib import Path

import typer
from graphrag.api import build_index
from graphrag.callbacks.console_workflow_callbacks import ConsoleWorkflowCallbacks
from graphrag.config.enums import CacheType, IndexingMethod
from graphrag.config.load_config import load_config
from graphrag.logger.standard_logging import init_loggers

app = typer.Typer(help="Custom GraphRAG CLI with single file support.")
logger = logging.getLogger(__name__)

@app.callback()
def main():
    """Custom CLI for GraphRAG."""
    pass

@app.command("index")
def index_cli(
    root: Path = typer.Option(
        Path(),
        "--root",
        "-r",
        help="The project root directory.",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="The configuration to use.",
        exists=True,
        file_okay=True,
        readable=True,
    ),
    file: Path | None = typer.Option(
        None,
        "--file",
        "-f",
        help="Specific file to index. Overrides input configuration.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    method: IndexingMethod = typer.Option(
        IndexingMethod.Standard.value,
        "--method",
        "-m",
        help="The indexing method to use.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Run the indexing pipeline with verbose logging",
    ),
    memprofile: bool = typer.Option(
        False,
        "--memprofile",
        help="Run the indexing pipeline with memory profiling",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help=(
            "Run the indexing pipeline without executing any steps "
            "to inspect and validate the configuration."
        ),
    ),
    cache: bool = typer.Option(
        True,
        "--cache/--no-cache",
        help="Use LLM cache.",
    ),
    skip_validation: bool = typer.Option(
        False,
        "--skip-validation",
        help="Skip any preflight validation. Useful when running no LLM steps.",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help=(
            "Indexing pipeline output directory. "
            "Overrides output.base_dir in the configuration file."
        ),
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
) -> None:
    """Build a knowledge graph index."""
    
    # 1. Prepare Overrides
    cli_overrides = {}
    if output:
        # User requested specific output destination.
        # Structure: <provided_path>/graphrag-index/{output, logs, cache}
        
        # Ensure we are working with an absolute path
        dest_root = output.resolve() / "graphrag-index"
        
        output_dir = dest_root / "output"
        logs_dir = dest_root / "logs"
        cache_dir = dest_root / "cache"
        
        # Create these directories to ensure they exist (though GraphRAG might create them)
        # It's safer to let GraphRAG create them, but we define the paths here.

        cli_overrides["output.base_dir"] = str(output_dir)
        cli_overrides["reporting.base_dir"] = str(logs_dir)
        cli_overrides["update_index_output.base_dir"] = str(output_dir)
        cli_overrides["cache.base_dir"] = str(cache_dir)
        
        if verbose:
            print(f"Configuring dedicated output structure at: {dest_root}")
            print(f"  output.base_dir = {output_dir}")
            print(f"  reporting.base_dir = {logs_dir}")
            print(f"  cache.base_dir = {cache_dir}")
    
    if file:
        # Override input configuration to point to this specific file
        # We assume the file exists because of typer validation
        # input.base_dir = parent directory of the file
        # input.file_pattern = exact match regex for the filename
        
        file_dir = file.parent
        # FilePipelineStorage matches against the full absolute path of the file found.
        # So we must match the exact absolute path of our target file.
        file_pattern = f"^{re.escape(str(file.resolve()))}$"
        
        cli_overrides["input.storage.base_dir"] = str(file_dir)
        cli_overrides["input.file_pattern"] = file_pattern
        
        if verbose:
            print(f"Overriding input config for specific file:")
            print(f"  input.storage.base_dir = {file_dir}")
            print(f"  input.file_pattern = {file_pattern}")

    # 2. Load Config
    try:
        config = load_config(root, config, cli_overrides)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    # 3. Setup Logging
    init_loggers(
        config=config,
        verbose=verbose,
    )

    if not cache:
        config.cache.type = CacheType.none

    # 4. Run Pipeline (via API)
    logger.info("Starting pipeline run. Dry run: %s", dry_run)
    
    if dry_run:
        logger.info("Dry run complete, exiting...")
        sys.exit(0)

    # Using console callbacks for standard output
    callbacks = [ConsoleWorkflowCallbacks(verbose=verbose)]

    try:
        outputs = asyncio.run(
            build_index(
                config=config,
                method=method,
                is_update_run=False, # We are mirroring the 'index' command, not 'update'
                memory_profile=memprofile,
                callbacks=callbacks,
                verbose=verbose,
            )
        )
        
        encountered_errors = any(
            output.errors and len(output.errors) > 0 for output in outputs
        )

        if encountered_errors:
            logger.error(
                "Errors occurred during the pipeline run, see logs for more details."
            )
            sys.exit(1)
        else:
            logger.info("All workflows completed successfully.")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    os.environ['LITELLM_LOG'] = 'DEBUG' 
    app()
