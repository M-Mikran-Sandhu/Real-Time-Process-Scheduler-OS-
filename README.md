# Real-Time Process Scheduler

This project simulates real-time operating system scheduling with deadlines using two different algorithms: Earliest Deadline First (EDF) and Rate Monotonic Scheduling (RMS).

## Project Overview

The Real-Time Process Scheduler project consists of two interfaces:

- **CLI Application** (`main.py`): A command-line interface with rich, colorful output
- **GUI Application** (`GUI.py`): A desktop graphical interface with visual representations

Both applications implement real-time scheduling algorithms to demonstrate how processes are managed with deadlines in a real-time operating system.

## Scheduling Algorithms

### Earliest Deadline First (EDF)

- **Dynamic Priority Algorithm**: Priority is assigned based on the proximity of the deadline
- Tasks with earlier deadlines receive higher priority
- Preemptive scheduling: A newly arrived task with an earlier deadline can preempt the currently running task
- Optimal for meeting deadlines when the system is not overloaded
- Runtime complexity: O(n log n) due to maintaining a priority queue

### Rate Monotonic Scheduling (RMS)

- **Static Priority Algorithm**: Priority is assigned based on the period of the task
- Tasks with shorter periods (higher frequency) receive higher priority
- Non-preemptive in traditional form, but our implementation is preemptive
- Suitable for periodic tasks with fixed periods
- More predictable than EDF but potentially less efficient in utilization

### Period in GUI

In the GUI application, the **Period** field represents the interval at which a periodic task repeats:

- For RMS scheduling, the period determines the task's priority (shorter period = higher priority)
- For EDF scheduling, the period is used as part of the deadline calculation
- If left blank, the deadline value is used as the period
- The period is particularly important for periodic tasks in real-time systems

## How the Scheduling Process Works

### 1. Task Creation

- Each task has the following properties:
  - **Task ID/Name**: Unique identifier for the task
  - **Arrival Time**: When the task becomes available for execution
  - **Burst Time**: Amount of CPU time required to complete the task
  - **Deadline**: Time by which the task must complete
  - **Period**: For periodic tasks (used primarily in RMS)

### 2. Scheduling Algorithm Execution

- The scheduler maintains a ready queue of tasks
- At each time unit, the scheduler:
  1. Checks for newly arrived tasks and adds them to the ready queue
  2. Selects the highest priority task based on the chosen algorithm
  3. Executes the selected task for one time unit
  4. Updates the task's remaining execution time
  5. Checks if the task has completed or if deadlines have been missed

### 3. Deadline Monitoring

- The system continuously monitors if tasks are completing before their deadlines
- A deadline is considered missed if the task completes after its deadline time
- The system counts and displays missed deadlines
- Visual indicators (colors in GUI, text in CLI) highlight missed deadlines

### 4. Visualization

- **Gantt Chart**: Visual timeline showing which task executes at each time unit
- **Timeline Display**: Detailed breakdown of execution order
- **Statistics**: Summary of scheduling results including missed deadlines

## Features

### CLI Application (`main.py`)

- Professional command-line interface with colored output using Rich library
- Menu-driven interface with options:
  - Add Task
  - View All Tasks
  - Run Scheduler
  - Show Gantt Chart
  - Show Missed Deadline Count
  - Display Full Execution Timeline
  - Exit
- Horizontal bar Gantt chart with color-coded status (green for on-time, red for missed)
- Real-time progress indicators during scheduling

### GUI Application (`gui.py`)

- Graphical desktop interface built with Tkinter
- Interactive task management with tree view
- Visual Gantt chart with timeline visualization
- Support for both EDF and RMS algorithms
- Detailed results window with statistics and timeline
- Color-coded visualization for missed deadlines

## Running the Applications

### Prerequisites

- Python 3.6 or higher
- For CLI: `pip install rich`

### Execution Commands

```bash
# Run CLI application
python main.py

# Run GUI application
python GUI.py

# Run existing tests
python test_scheduler.py
```

## Project Structure

```
OS Project/
├── README.md           # This file
├── main.py    # Command-line interface application
├── gui.py             # Graphical user interface application
├── scheduler.py       # Core scheduling algorithms implementation
├── test_scheduler.py  # Unit tests
```

## Key Components

### Core Classes

- **Task**: Represents a schedulable entity with properties like arrival time, burst time, deadline, and period
- **Scheduler**: Abstract base class for scheduling algorithms
- **EDFScheduler**: Implements Earliest Deadline First algorithm
- **RMSScheduler**: Implements Rate Monotonic Scheduling algorithm
- **CLIScheduler**: Manages the command-line interface
- **SchedulerApp**: Manages the graphical user interface

### Algorithm Implementation Details

- Both algorithms use a priority queue (min-heap) for efficient task selection
- Tasks are dynamically prioritized based on either deadline (EDF) or period (RMS)
- The simulation runs in discrete time units, advancing the clock after each unit of execution
- Deadline miss detection occurs both during execution and upon task completion

## Educational Objectives

This project demonstrates:

- Real-time scheduling concepts and algorithms
- Priority-based task scheduling
- Deadline management and monitoring
- Comparison between dynamic (EDF) and static (RMS) priority scheduling
- Practical implementation of scheduling theory
- Visualization of scheduling behavior

## University Submission Requirements

This project is designed for university submission and includes:

- Clean, well-commented code with proper documentation
- Professional user interfaces (CLI and GUI)
- Comprehensive functionality demonstrating real-time scheduling concepts
- Visual representations for easy analysis
- Support for both major real-time scheduling algorithms
