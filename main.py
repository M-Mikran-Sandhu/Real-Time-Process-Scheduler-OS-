import os
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, BarColumn, TextColumn
from rich.style import Style
import time


class Task:
    """Represents a task in the real-time scheduler"""

    def __init__(self, task_id: int, execution_time: int, deadline: int, arrival_time: int = 0):
        """
        Initialize a task

        Args:
            task_id: Unique identifier for the task
            execution_time: Time units required to complete the task
            deadline: Deadline time for the task
            arrival_time: Arrival time of the task (default 0 for static tasks)
        """
        self.task_id = task_id
        self.execution_time = execution_time
        self.deadline = deadline
        self.arrival_time = arrival_time
        self.remaining_time = execution_time
        self.start_time = None
        self.completion_time = None
        self.is_completed = False
        self.missed_deadline = False

    def __str__(self):
        return f"Task {self.task_id}: ET={self.execution_time}, DL={self.deadline}, AT={self.arrival_time}"


class EDFTaskScheduler:
    """Implements Earliest Deadline First (EDF) scheduling algorithm"""

    def __init__(self):
        """Initialize the scheduler with an empty task list"""
        self.tasks: List[Task] = []
        self.current_time = 0
        self.completed_tasks: List[Task] = []
        self.missed_deadlines_count = 0
        self.timeline: List[Dict] = []  # For gantt chart

    def add_task(self, task: Task):
        """Add a task to the scheduler"""
        self.tasks.append(task)

    def sort_tasks_by_deadline(self):
        """Sort tasks by their deadline (Earliest Deadline First)"""
        self.tasks.sort(key=lambda x: x.deadline)

    def get_next_ready_task(self) -> Optional[Task]:
        """Get the next ready task with earliest deadline"""
        ready_tasks = [task for task in self.tasks if
                       task.arrival_time <= self.current_time and
                       not task.is_completed and
                       task.remaining_time > 0]

        if not ready_tasks:
            return None

        # Sort by deadline (EDF)
        ready_tasks.sort(key=lambda x: x.deadline)
        return ready_tasks[0]

    def run_scheduler(self):
        """Run the EDF scheduler and return execution timeline"""
        # Reset scheduler state
        self.current_time = 0
        self.completed_tasks = []
        self.missed_deadlines_count = 0
        self.timeline = []

        # Make sure all tasks are sorted by deadline initially
        self.sort_tasks_by_deadline()

        # Calculate max time (largest deadline)
        max_time = max([task.deadline for task in self.tasks]
                       ) if self.tasks else 0

        # Run simulation until all tasks are completed or max time reached
        while self.current_time <= max_time and not self.all_tasks_completed():
            # Check for missed deadlines
            for task in self.tasks:
                if not task.is_completed and task.remaining_time > 0 and self.current_time > task.deadline:
                    if not task.missed_deadline:
                        task.missed_deadline = True
                        self.missed_deadlines_count += 1

            # Get next task to execute
            current_task = self.get_next_ready_task()

            if current_task:
                # Record execution in timeline
                self.timeline.append({
                    'time': self.current_time,
                    'task_id': current_task.task_id,
                    'executing': True
                })

                # Execute one time unit of the task
                current_task.remaining_time -= 1

                # Mark start time if not already set
                if current_task.start_time is None:
                    current_task.start_time = self.current_time

                # Check if task is completed
                if current_task.remaining_time == 0:
                    current_task.completion_time = self.current_time
                    current_task.is_completed = True
                    self.completed_tasks.append(current_task)

                    # Check if deadline was missed
                    if current_task.completion_time > current_task.deadline:
                        current_task.missed_deadline = True
                        self.missed_deadlines_count += 1
            else:
                # No task ready to execute, record idle time
                self.timeline.append({
                    'time': self.current_time,
                    'task_id': 'IDLE',
                    'executing': False
                })

            self.current_time += 1

        return self.timeline

    def all_tasks_completed(self) -> bool:
        """Check if all tasks are completed"""
        return all(task.is_completed for task in self.tasks)

    def get_missed_deadlines_count(self) -> int:
        """Return the number of missed deadlines"""
        return self.missed_deadlines_count

    def get_gantt_chart_data(self) -> List[Dict]:
        """Return gantt chart data"""
        return self.timeline


class CLIScheduler:
    """Command Line Interface for the Real-Time Scheduler"""

    def __init__(self):
        """Initialize the CLI with console and scheduler"""
        self.console = Console()
        self.scheduler = EDFTaskScheduler()
        self.running = True

    def clear_screen(self):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Print a styled header"""
        self.console.print(f"\n[bold blue]{'='*60}[/bold blue]")
        self.console.print(f"[bold yellow]{title:^60}[/bold yellow]")
        self.console.print(f"[bold blue]{'='*60}[/bold blue]\n")

    def print_menu(self):
        """Display the main menu"""
        table = Table(title="Main Menu", show_header=True,
                      header_style="bold magenta")
        table.add_column("Option", style="cyan", justify="center")
        table.add_column("Description", style="green")

        table.add_row("1", "Add Task")
        table.add_row("2", "View All Tasks")
        table.add_row("3", "Run Scheduler")
        table.add_row("4", "Show Gantt Chart")
        table.add_row("5", "Show Missed Deadline Count")
        table.add_row("6", "Display Full Execution Timeline")
        table.add_row("7", "Exit")

        self.console.print(table)

    def add_task(self):
        """Add a new task to the scheduler"""
        self.print_header("Add New Task")

        try:
            task_id = IntPrompt.ask("[bold green]Enter Task ID")

            # Check if task ID already exists
            if any(task.task_id == task_id for task in self.scheduler.tasks):
                self.console.print("[red]Error: Task ID already exists![/red]")
                return

            execution_time = IntPrompt.ask("[bold green]Enter Execution Time")
            deadline = IntPrompt.ask("[bold green]Enter Deadline")
            arrival_time = IntPrompt.ask(
                "[bold green]Enter Arrival Time (default 0)", default=0)

            task = Task(task_id, execution_time, deadline, arrival_time)
            self.scheduler.add_task(task)

            self.console.print(
                f"[green]Task {task_id} added successfully![/green]")
        except ValueError:
            self.console.print(
                "[red]Invalid input! Please enter valid numbers.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error adding task: {e}[/red]")

    def view_tasks(self):
        """Display all tasks in a table"""
        self.print_header("All Tasks")

        if not self.scheduler.tasks:
            self.console.print("[yellow]No tasks available.[/yellow]")
            return

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Task ID", style="dim", width=10)
        table.add_column("Exec Time", justify="center", width=12)
        table.add_column("Deadline", justify="center", width=12)
        table.add_column("Arrival Time", justify="center", width=12)
        table.add_column("Status", justify="center", width=15)

        for task in self.scheduler.tasks:
            status = "[green]COMPLETED[/green]" if task.is_completed else \
                     "[red]PENDING[/red]"
            table.add_row(
                str(task.task_id),
                str(task.execution_time),
                str(task.deadline),
                str(task.arrival_time),
                status
            )

        self.console.print(table)

    def run_scheduler(self):
        """Run the scheduler and show results"""
        self.print_header("Running EDF Scheduler")

        if not self.scheduler.tasks:
            self.console.print("[yellow]No tasks to schedule![/yellow]")
            return

        # Show progress bar while running
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("[cyan]Scheduling tasks...", total=100)

            # Simulate processing
            for i in range(100):
                time.sleep(0.02)  # Simulate processing time
                progress.update(task, advance=1)

        # Run the actual scheduler
        timeline = self.scheduler.run_scheduler()

        self.console.print("\n[bold green]Scheduler completed![/bold green]")
        self.console.print(
            f"[bold cyan]Total Missed Deadlines: {self.scheduler.get_missed_deadlines_count()}[/bold cyan]")

    def show_gantt_chart(self):
        """Display a text-based Gantt chart"""
        self.print_header("Gantt Chart")

        if not self.scheduler.timeline:
            self.console.print(
                "[yellow]Run scheduler first to generate timeline![/yellow]")
            return

        # Create a timeline visualization
        self.console.print("\n[bold white]Execution Timeline:[/bold white]")

        # Group timeline by time units
        timeline_dict = {}
        for entry in self.scheduler.timeline:
            time_unit = entry['time']
            task_id = entry['task_id']
            if time_unit not in timeline_dict:
                timeline_dict[time_unit] = []
            timeline_dict[time_unit].append(task_id)

        # Determine the time range
        if not timeline_dict:
            self.console.print("[yellow]No timeline data available![/yellow]")
            return

        min_time = min(timeline_dict.keys())
        max_time = max(timeline_dict.keys())

        # Create a horizontal bar chart representation
        task_executions = {}
        for time_unit in range(min_time, max_time + 1):
            if time_unit in timeline_dict:
                for task_id in timeline_dict[time_unit]:
                    if task_id != 'IDLE':
                        if task_id not in task_executions:
                            task_executions[task_id] = []
                        task_executions[task_id].append(time_unit)

        # Print the Gantt chart as horizontal bars
        for task_id in sorted(task_executions.keys()):
            if task_id != 'IDLE':
                time_slots = task_executions[task_id]
                bar_length = len(time_slots)
                bar = "█" * bar_length

                # Check if this task missed its deadline
                task = next(
                    (t for t in self.scheduler.tasks if t.task_id == task_id), None)
                status_color = "red" if task and task.missed_deadline else "green"

                self.console.print(
                    f"Task {task_id:2d}: [{status_color}]{bar}[/{status_color}] ({' , '.join(map(str, time_slots))})")

        # Print IDLE time if any
        idle_times = []
        for time_unit in range(min_time, max_time + 1):
            if time_unit in timeline_dict:
                for task_id in timeline_dict[time_unit]:
                    if task_id == 'IDLE':
                        idle_times.append(time_unit)

        if idle_times:
            idle_bar = "░" * len(idle_times)
            self.console.print(
                f"IDLE    : [yellow]{idle_bar}[/yellow] ({' , '.join(map(str, idle_times))})")

    def show_missed_deadlines(self):
        """Display the count of missed deadlines"""
        self.print_header("Missed Deadlines Count")

        if not self.scheduler.tasks:
            self.console.print("[yellow]No tasks scheduled![/yellow]")
            return

        missed_count = self.scheduler.get_missed_deadlines_count()
        self.console.print(
            f"[bold cyan]Total Missed Deadlines: {missed_count}[/bold cyan]")

        if missed_count > 0:
            self.console.print(
                "[red]Warning: Some deadlines were missed![/red]")
        else:
            self.console.print("[green]All deadlines met![/green]")

    def display_full_timeline(self):
        """Display the complete execution timeline"""
        self.print_header("Full Execution Timeline")

        if not self.scheduler.timeline:
            self.console.print(
                "[yellow]Run scheduler first to generate timeline![/yellow]")
            return

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Time", justify="center", width=8)
        table.add_column("Executing Task", justify="center", width=20)

        for entry in self.scheduler.timeline:
            task_id = entry['task_id']
            time_str = str(entry['time'])

            # Color code based on task status
            if task_id == 'IDLE':
                table.add_row(time_str, "[yellow]IDLE[/yellow]")
            else:
                # Check if this task missed its deadline at this time
                task = next(
                    (t for t in self.scheduler.tasks if t.task_id == task_id), None)
                if task and entry['time'] > task.deadline:
                    table.add_row(time_str, f"[red]Task {task_id}[/red]")
                else:
                    table.add_row(time_str, f"[green]Task {task_id}[/green]")

        self.console.print(table)

    def run(self):
        """Main loop for the CLI"""
        while self.running:
            self.clear_screen()
            self.print_header("Real-Time Process Scheduler (EDF Algorithm)")
            self.print_menu()

            try:
                choice = Prompt.ask("\n[bold cyan]Select an option", choices=[
                                    "1", "2", "3", "4", "5", "6", "7"])

                if choice == "1":
                    self.add_task()
                elif choice == "2":
                    self.view_tasks()
                elif choice == "3":
                    self.run_scheduler()
                elif choice == "4":
                    self.show_gantt_chart()
                elif choice == "5":
                    self.show_missed_deadlines()
                elif choice == "6":
                    self.display_full_timeline()
                elif choice == "7":
                    self.console.print(
                        "[bold green]Thank you for using the Real-Time Scheduler![/bold green]")
                    self.running = False

                if self.running:
                    input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Exiting...[/bold red]")
                self.running = False
            except Exception as e:
                self.console.print(f"[red]An error occurred: {e}[/red]")
                input("Press Enter to continue...")


if __name__ == "__main__":
    # Check if rich is installed
    try:
        cli = CLIScheduler()
        cli.run()
    except ImportError:
        print("Rich library is required. Install it using: pip install rich")
