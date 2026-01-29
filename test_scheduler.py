from scheduler import Task, EDFScheduler, RMSScheduler
from main import print_timeline

def test_edf_preemption():
    print("Testing EDF Preemption...")
    t1 = Task("T1", 0, 3, 10) # Abs DL 10
    t2 = Task("T2", 1, 2, 4)  # Abs DL 5
    
    scheduler = EDFScheduler()
    tasks = [t1, t2]
    
    history = scheduler.run(tasks, max_time=10)
    
    assert history[0] == (0, 1, "T1")
    assert history[1] == (1, 2, "T2")
    assert history[2] == (2, 3, "T2")
    assert history[3] == (3, 4, "T1")
    assert history[4] == (4, 5, "T1")
    
    print("EDF Preemption Test PASSED")

def test_rms_preemption():
    print("Testing RMS Preemption...")
    # T1: Period 10 (Lower Priority)
    # T2: Period 5 (Higher Priority)
    t1 = Task("T1", 0, 3, 10, period=10) 
    t2 = Task("T2", 1, 2, 5, period=5)
    
    scheduler = RMSScheduler()
    tasks = [t1, t2]
    
    history = scheduler.run(tasks, max_time=10)
    print_timeline(history)
    
    # Expected: T2 preempts T1 at time 1
    assert history[0] == (0, 1, "T1")
    assert history[1] == (1, 2, "T2")
    assert history[2] == (2, 3, "T2")
    assert history[3] == (3, 4, "T1")
    assert history[4] == (4, 5, "T1")
    
    print("RMS Preemption Test PASSED")

if __name__ == "__main__":
    test_edf_preemption()
    test_rms_preemption()
