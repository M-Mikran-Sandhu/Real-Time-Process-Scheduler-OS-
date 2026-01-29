import tkinter as tk
from tkinter import ttk, messagebox
from scheduler import Task, EDFScheduler, RMSScheduler
import time


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Process Scheduler Simulator")
        self.root.geometry("800x600")

        self.tasks = []
        self.last_scheduler = None
        self.last_history = None

        # --- Top Frame: Input ---
        input_frame = ttk.LabelFrame(root, text="Add Task")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Name:").grid(
            row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.name_var,
                  width=10).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Arrival:").grid(
            row=0, column=2, padx=5, pady=5)
        self.arrival_var = tk.IntVar(value=0)
        ttk.Entry(input_frame, textvariable=self.arrival_var,
                  width=5).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Burst:").grid(
            row=0, column=4, padx=5, pady=5)
        self.burst_var = tk.IntVar(value=1)
        ttk.Entry(input_frame, textvariable=self.burst_var,
                  width=5).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(input_frame, text="Deadline:").grid(
            row=0, column=6, padx=5, pady=5)
        self.deadline_var = tk.IntVar(value=10)
        ttk.Entry(input_frame, textvariable=self.deadline_var,
                  width=5).grid(row=0, column=7, padx=5, pady=5)

        ttk.Label(input_frame, text="Period:").grid(
            row=0, column=8, padx=5, pady=5)
        self.period_var = tk.StringVar()  # Optional
        ttk.Entry(input_frame, textvariable=self.period_var,
                  width=5).grid(row=0, column=9, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(
            row=0, column=10, padx=10, pady=5)

        # --- Middle Frame: Task List ---
        list_frame = ttk.LabelFrame(root, text="Task List")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Arrival", "Burst", "Deadline", "Period")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=5)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Bottom Frame: Controls & Visualization ---
        control_frame = ttk.Frame(root)
        control_frame.pack(fill="x", padx=10, pady=5)

        self.algo_var = tk.StringVar(value="EDF")
        ttk.Radiobutton(control_frame, text="EDF", variable=self.algo_var,
                        value="EDF").pack(side="left", padx=10)
        ttk.Radiobutton(control_frame, text="RMS", variable=self.algo_var,
                        value="RMS").pack(side="left", padx=10)

        ttk.Button(control_frame, text="Run Simulation",
                   command=self.run_simulation).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Clear Tasks",
                   command=self.clear_tasks).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Show Results",
                   command=self.show_results).pack(side="left", padx=10)

        # Canvas for Gantt Chart
        self.canvas_frame = ttk.LabelFrame(root, text="Gantt Chart")
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", height=150)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollbar for canvas
        self.scrollbar = ttk.Scrollbar(
            self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar.pack(fill="x")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

    def add_task(self):
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Task name is required.")
                return

            arrival = self.arrival_var.get()
            burst = self.burst_var.get()
            deadline = self.deadline_var.get()

            period_str = self.period_var.get().strip()
            period = int(period_str) if period_str else deadline

            task = Task(name, arrival, burst, deadline, period)
            self.tasks.append(task)

            self.tree.insert("", "end", values=(
                name, arrival, burst, deadline, period))

            # Reset fields
            self.name_var.set("")
            self.arrival_var.set(0)
            self.burst_var.set(1)
            self.deadline_var.set(10)
            self.period_var.set("")

        except ValueError:
            messagebox.showerror(
                "Error", "Invalid input. Please check numeric fields.")

    def clear_tasks(self):
        self.tasks = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.canvas.delete("all")

    def run_simulation(self):
        if not self.tasks:
            messagebox.showwarning("Warning", "No tasks to schedule.")
            return

        # Re-create task objects because previous run might have modified them (remaining_time etc.)
        # Since our Task class is simple, let's just rebuild them from the Treeview data to be safe and stateless.

        simulation_tasks = []
        for item in self.tree.get_children():
            vals = self.tree.item(item)["values"]
            # vals are strings from treeview
            name = vals[0]
            arrival = int(vals[1])
            burst = int(vals[2])
            deadline = int(vals[3])
            period = int(vals[4])
            simulation_tasks.append(
                Task(name, arrival, burst, deadline, period))

        algo = self.algo_var.get()
        if algo == "EDF":
            scheduler = EDFScheduler()
        else:
            scheduler = RMSScheduler()

        # Heuristic for max time
        max_time = max(t.absolute_deadline for t in simulation_tasks) + 20
        history = scheduler.run(simulation_tasks, max_time=max_time)

        self.draw_gantt(history, max_time)

        # Store scheduler for later results
        self.last_scheduler = scheduler
        self.last_history = history

        # Show basic stats
        missed = scheduler.missed_deadlines
        msg = f"Simulation Complete.\nTotal Tasks: {len(simulation_tasks)}\nMissed Deadlines: {missed}"
        messagebox.showinfo("Simulation Status", msg)

    def draw_gantt(self, history, max_time):
        self.canvas.delete("all")

        if not history:
            return

        # Merge contiguous
        merged = []
        if history:
            curr_start, curr_end, curr_task = history[0]
            for start, end, task in history[1:]:
                if task == curr_task and start == curr_end:
                    curr_end = end
                else:
                    merged.append((curr_start, curr_end, curr_task))
                    curr_start, curr_end, curr_task = start, end, task
            merged.append((curr_start, curr_end, curr_task))

        # Drawing config
        unit_width = 30
        height = 50
        y_offset = 50

        total_width = max_time * unit_width + 50
        self.canvas.configure(scrollregion=(0, 0, total_width, 200))

        # Draw Time Axis
        self.canvas.create_line(
            10, y_offset + height + 10, total_width, y_offset + height + 10, arrow=tk.LAST)
        for t in range(max_time + 1):
            x = 10 + t * unit_width
            self.canvas.create_line(
                x, y_offset + height + 10, x, y_offset + height + 15)
            self.canvas.create_text(
                x, y_offset + height + 25, text=str(t), font=("Arial", 8))

        # Draw Bars
        colors = ["#FFCCCC", "#CCFFCC", "#CCCCFF",
                  "#FFFFCC", "#FFCCFF", "#CCFFFF"]
        task_colors = {}

        for start, end, task_id in merged:
            if task_id == "IDLE":
                continue

            if str(task_id) not in task_colors:
                task_colors[str(task_id)] = colors[len(
                    task_colors) % len(colors)]

            # Check if this task missed its deadline
            task_obj = next(
                (t for t in self.tasks if t.task_id == task_id), None)
            if task_obj and task_obj.missed_deadline:
                # Use a red-like color for missed deadline tasks
                color = "#FF9999"
            else:
                color = task_colors[str(task_id)]

            x1 = 10 + start * unit_width
            x2 = 10 + end * unit_width
            y1 = y_offset
            y2 = y_offset + height

            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, outline="black")

            # Label
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            label = str(task_id)
            # Truncate if too small
            if (x2 - x1) < 20:
                label = ""
            self.canvas.create_text(
                mid_x, mid_y, text=label, font=("Arial", 10, "bold"))

        # Draw IDLE time if any
        idle_segments = [(start, end)
                         for start, end, task_id in merged if task_id == "IDLE"]
        for start, end in idle_segments:
            x1 = 10 + start * unit_width
            x2 = 10 + end * unit_width
            y1 = y_offset
            y2 = y_offset + height
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill="#DDDDDD", outline="black")
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_text(mid_x, mid_y, text="IDLE", font=(
                "Arial", 10, "bold"), fill="gray")

    def show_results(self):
        if not self.last_scheduler:
            messagebox.showwarning("Warning", "Please run simulation first.")
            return

        # Create a new window for detailed results
        result_window = tk.Toplevel(self.root)
        result_window.title("Simulation Results")
        result_window.geometry("600x400")

        # Create a frame for the results
        result_frame = ttk.Frame(result_window)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Stats frame
        stats_frame = ttk.LabelFrame(result_frame, text="Statistics")
        stats_frame.pack(fill="x", padx=5, pady=5)

        total_tasks = len([item for item in self.tree.get_children()])
        ttk.Label(stats_frame, text=f"Total Tasks: {total_tasks}").pack(
            anchor="w", padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Completed Tasks: {len(self.last_scheduler.completed_tasks)}").pack(
            anchor="w", padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Missed Deadlines: {self.last_scheduler.missed_deadlines}").pack(
            anchor="w", padx=10, pady=2)
        ttk.Label(stats_frame, text=f"Algorithm Used: {self.algo_var.get()}").pack(
            anchor="w", padx=10, pady=2)

        # Timeline frame
        timeline_frame = ttk.LabelFrame(
            result_frame, text="Execution Timeline")
        timeline_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create a text widget with scrollbar for timeline
        timeline_text = tk.Text(timeline_frame, wrap=tk.NONE)
        timeline_scroll = ttk.Scrollbar(
            timeline_frame, orient="vertical", command=timeline_text.yview)
        timeline_text.configure(yscrollcommand=timeline_scroll.set)

        timeline_text.pack(side="left", fill="both", expand=True, padx=(5, 0))
        timeline_scroll.pack(side="right", fill="y")

        # Insert timeline data
        timeline_text.insert(tk.END, "Timeline:\n")
        for start, end, task_id in self.last_history:
            # Check if this task missed deadline
            # Look up the original task info from the treeview
            task_missed = False
            for item in self.tree.get_children():
                vals = self.tree.item(item)["values"]
                if str(vals[0]) == str(task_id):  # Compare with task name
                    # Extract deadline from the original task data
                    deadline = int(vals[3])
                    arrival = int(vals[1])
                    # If the execution time exceeds the absolute deadline, it's missed
                    if start >= (arrival + deadline):
                        task_missed = True
                        break

            if task_missed:
                timeline_text.insert(
                    tk.END, f"Time {start}-{end}: Task {task_id} [MISSED]\n")
            else:
                timeline_text.insert(
                    tk.END, f"Time {start}-{end}: Task {task_id}\n")

        timeline_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
