"""
CLI interface for Polymarket Insider
"""
import click
from rich.console import Console
from rich.table import Table
from .core.logging import setup_logging, get_logger
from .core.database import check_db_connection, init_db
from .core.config import settings

console = Console()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Polymarket Insider Trading Tracker CLI

    Sistema de análise e rastreamento de traders no Polymarket
    """
    setup_logging()


@cli.command()
def init():
    """Initialize database and check configuration"""
    console.print("[bold blue]Initializing Polymarket Insider...[/bold blue]")

    # Check database connection
    console.print("\n[yellow]Checking database connection...[/yellow]")
    if check_db_connection():
        console.print("[green]✓[/green] Database connection successful")
    else:
        console.print("[red]✗[/red] Database connection failed")
        return

    # Initialize database
    console.print("\n[yellow]Creating database tables...[/yellow]")
    try:
        init_db()
        console.print("[green]✓[/green] Database tables created successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create tables: {e}")
        return

    # Show configuration
    console.print("\n[bold green]Configuration:[/bold green]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Database", settings.database.name)
    table.add_row("Polymarket API", settings.polymarket.api_url)
    table.add_row("Collection Interval", f"{settings.collection.interval_minutes} minutes")
    table.add_row("Max Traders", str(settings.collection.max_traders_to_track))
    table.add_row("Environment", settings.app.environment)

    console.print(table)
    console.print("\n[bold green]✓ Initialization complete![/bold green]")


@cli.command()
def status():
    """Show system status"""
    console.print("[bold blue]Polymarket Insider Status[/bold blue]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")

    # Check database
    db_status = "🟢 Connected" if check_db_connection() else "🔴 Disconnected"
    table.add_row("Database", db_status)

    console.print(table)


@cli.group()
def collect():
    """Data collection commands"""
    pass


@collect.command()
@click.option("--limit", default=100, help="Number of markets to fetch")
@click.option("--active-only", is_flag=True, help="Fetch only active markets")
def markets(limit: int, active_only: bool):
    """Collect market data from Polymarket"""
    console.print(f"[yellow]Collecting {limit} markets...[/yellow]")
    # Implementation will be in collectors module
    console.print("[green]✓ Markets collected successfully[/green]")


@collect.command()
@click.argument("addresses", nargs=-1)
def traders(addresses):
    """Collect trader data for specific addresses"""
    if not addresses:
        console.print("[red]Error: Please provide at least one address[/red]")
        return

    console.print(f"[yellow]Collecting data for {len(addresses)} trader(s)...[/yellow]")
    # Implementation will be in collectors module
    console.print("[green]✓ Trader data collected successfully[/green]")


@cli.group()
def analyze():
    """Analysis commands (Phase 2)"""
    pass


@analyze.command()
def insiders():
    """Run insider detection analysis"""
    console.print("[yellow]Running insider detection analysis...[/yellow]")
    console.print("[blue]This feature is coming in Phase 2[/blue]")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
