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
    import os
    from pathlib import Path

    console.print("[bold blue]Initializing Polymarket Insider...[/bold blue]")

    # Check if .env file exists
    env_path = Path(".env")
    if not env_path.exists():
        console.print("\n[red]✗ .env file not found![/red]")
        console.print("\n[yellow]Please create a .env file with your database credentials:[/yellow]")
        console.print("\n1. Copy the example file:")
        console.print("   [cyan]cp .env.example .env[/cyan]")
        console.print("\n2. Edit .env and set your MySQL password:")
        console.print("   [cyan]DB_PASSWORD=your_mysql_password[/cyan]")
        console.print("\n3. Run this command again:")
        console.print("   [cyan]python3 -m polymarket_insider init[/cyan]")
        return

    # Try to create database if it doesn't exist
    console.print("\n[yellow]Checking/creating database...[/yellow]")
    try:
        from sqlalchemy import create_engine, text
        # Connect to MySQL without specifying database
        root_connection_string = f"mysql+pymysql://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/"
        temp_engine = create_engine(root_connection_string)

        with temp_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SHOW DATABASES LIKE '{settings.database.name}'"))
            if result.fetchone() is None:
                # Create database
                conn.execute(text(f"CREATE DATABASE {settings.database.name}"))
                conn.commit()
                console.print(f"[green]✓[/green] Database '{settings.database.name}' created")
            else:
                console.print(f"[green]✓[/green] Database '{settings.database.name}' already exists")
        temp_engine.dispose()
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create database: {e}")
        console.print("\n[yellow]Common solutions:[/yellow]")
        console.print("1. Check if MySQL is running: [cyan]sudo systemctl status mysql[/cyan]")
        console.print("2. Verify your DB_PASSWORD in .env matches your MySQL root password")
        console.print("3. Or set a password for MySQL root user:")
        console.print("   [cyan]sudo mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_password';\"[/cyan]")
        return

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
    from ..collectors.market_collector import collect_markets_task

    console.print(f"[yellow]Collecting up to {limit} markets...[/yellow]")

    try:
        count = collect_markets_task(limit=limit, active_only=active_only)
        console.print(f"[green]✓ Successfully collected {count} markets[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to collect markets: {e}[/red]")
        logger.error("Market collection failed", error=str(e))


@collect.command()
@click.argument("addresses", nargs=-1)
def traders(addresses):
    """Collect trader data for specific addresses"""
    from ..collectors.trader_collector import collect_traders_task

    if not addresses:
        console.print("[red]Error: Please provide at least one address[/red]")
        return

    console.print(f"[yellow]Collecting data for {len(addresses)} trader(s)...[/yellow]")

    try:
        count = collect_traders_task(list(addresses))
        console.print(f"[green]✓ Successfully collected {count} trader(s)[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to collect traders: {e}[/red]")
        logger.error("Trader collection failed", error=str(e))


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
