import subprocess, sys
from zenith.scanner.secrets import scan_text
from rich.console import Console
from rich.table import Table

console = Console()

def get_staged_diff() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=0"],
        capture_output=True, text=True
    )
    return result.stdout

def run():
    diff = get_staged_diff()
    if not diff:
        sys.exit(0)

    findings = scan_text(diff)

    if not findings:
        console.print("[green]✔ Zenith: No secrets detected. Safe to commit.[/green]")
        sys.exit(0)

    console.print("\n[bold red]🚨 Zenith Security Alert — Commit Blocked[/bold red]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Type", style="red")
    table.add_column("Line", style="cyan")
    table.add_column("Severity", style="yellow")
    for f in findings:
        table.add_row(f["type"], str(f["line"]), f["severity"])
    console.print(table)
    console.print("\n[yellow]💡 Fix: Move secrets to .env and use os.getenv()[/yellow]\n")
    sys.exit(1)

if __name__ == "__main__":
    run()
