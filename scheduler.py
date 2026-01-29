import heapq


class Task:
    def __init__(self, task_id, arrival_time, burst_time, deadline, period=0):
        self.task_id = task_id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.deadline = deadline
        self.period = period  # For RMS, period is usually equal to deadline
        self.absolute_deadline = arrival_time + deadline
        self.start_time = -1
        self.completion_time = -1
        self.missed_deadline = False
        # Add a unique counter to break ties in priority queue
        self._counter = 0  # Will be set when added to scheduler

    def __repr__(self):
        return f"Task(id={self.task_id}, arrival={self.arrival_time}, burst={self.burst_time}, deadline={self.deadline})"


class Scheduler:
    def __init__(self):
        self.time = 0
        self.ready_queue = []
        self.history = []  # List of (start_time, end_time, task_id)
        self.completed_tasks = []
        self.missed_deadlines = 0
        self._task_counter = 0  # To assign unique IDs to tasks

    def add_task(self, task):
        # Assign a unique counter to break ties in heap
        task._counter = self._task_counter
        self._task_counter += 1
        raise NotImplementedError

    def get_next_task(self):
        raise NotImplementedError

    def run(self, tasks, max_time=20):
        # Sort tasks by arrival time initially
        tasks.sort(key=lambda x: x.arrival_time)
        task_idx = 0
        current_task = None

        while self.time < max_time:
            # Check for new task arrivals
            while task_idx < len(tasks) and tasks[task_idx].arrival_time <= self.time:
                self.add_task(tasks[task_idx])
                task_idx += 1

            # Select next task
            current_task = self.get_next_task()

            # Execute the current task
            if current_task:
                # If task hasn't started yet
                if current_task.start_time == -1:
                    current_task.start_time = self.time

                # Execute for 1 unit
                self.history.append(
                    (self.time, self.time + 1, current_task.task_id))
                current_task.remaining_time -= 1

                # Check completion
                if current_task.remaining_time == 0:
                    current_task.completion_time = self.time + 1
                    if current_task.completion_time > current_task.absolute_deadline:
                        current_task.missed_deadline = True
                        self.missed_deadlines += 1
                    self.completed_tasks.append(current_task)
                else:
                    # Task not finished, push it back
                    self.push_back(current_task)
            else:
                # Idle
                self.history.append((self.time, self.time + 1, "IDLE"))

            self.time += 1

        return self.history


class EDFScheduler(Scheduler):
    def add_task(self, task):
        # Assign a unique counter to break ties in heap
        task._counter = self._task_counter
        self._task_counter += 1
        # EDF: Priority is based on absolute deadline (earlier is higher priority)
        # heapq is a min-heap, so we store (absolute_deadline, arrival_time, counter, task)
        # We include arrival_time as tie-breaker (FIFO), and counter to break final ties
        heapq.heappush(self.ready_queue, (task.absolute_deadline,
                       task.arrival_time, task._counter, task))

    def get_next_task(self):
        if not self.ready_queue:
            return None

        deadline, arrival, counter, task = heapq.heappop(self.ready_queue)
        return task

    def push_back(self, task):
        self.add_task(task)


class RMSScheduler(Scheduler):
    def add_task(self, task):
        # Assign a unique counter to break ties in heap
        task._counter = self._task_counter
        self._task_counter += 1
        # RMS: Priority is based on Period (shorter period = higher priority)
        # Static priority.
        # We assume period is provided. If not, maybe use deadline? RMS is strictly for periodic.
        # If input doesn't have period, RMS might not apply well, but we can use deadline as proxy if implicit deadline.
        priority = task.period if task.period > 0 else task.deadline
        heapq.heappush(self.ready_queue, (priority,
                       task.arrival_time, task._counter, task))

    def get_next_task(self):
        if not self.ready_queue:
            return None
        priority, arrival, counter, task = heapq.heappop(self.ready_queue)
        return task

    def push_back(self, task):
        self.add_task(task)
