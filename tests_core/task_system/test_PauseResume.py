"""
Tests for AbstractTask pause/resume mechanism.
"""

import threading
import time

from core.taskSystem.TaskStatus import TaskStatus
from tests_core.task_system.test_AbstractTask import ConcreteTask


class SlowTask(ConcreteTask):
    """Task that loops and calls checkPaused(), allowing pause to take effect."""

    def __init__(self, *args, iterations=10, iterationDelayMs=50, **kwargs):
        super().__init__(*args, **kwargs)
        self.iterations = iterations
        self.iterationDelayMs = iterationDelayMs
        self.completedIterations = 0

    def handle(self):
        for i in range(self.iterations):
            if self.isStopped():
                return
            self.checkPaused()
            time.sleep(self.iterationDelayMs / 1000)
            self.completedIterations += 1
        self.setProgress(100)

    @classmethod
    def deserialize(cls, data):
        return cls(name=data['name'])


def test_pauseSetsStatus(qtbot):
    """pause() sets task status to PAUSED."""
    task = ConcreteTask(name='PauseTest')
    task.setStatus(TaskStatus.RUNNING)
    with qtbot.waitSignal(task.statusChanged, timeout=1000):
        task.pause()
    assert task.status == TaskStatus.PAUSED
    assert task._isPaused is True


def test_resumeSetsStatus(qtbot):
    """resume() after pause() transitions back to RUNNING."""
    task = ConcreteTask(name='ResumeTest')
    task.setStatus(TaskStatus.RUNNING)
    task.pause()
    with qtbot.waitSignal(task.statusChanged, timeout=1000):
        task.resume()
    assert task.status == TaskStatus.RUNNING
    assert task._isPaused is False


def test_checkPausedBlocksThread(qtbot):
    """checkPaused() blocks thread execution while paused."""
    task = SlowTask(name='BlockTest', iterations=20, iterationDelayMs=30)
    task.setStatus(TaskStatus.RUNNING)
    completedWhenPaused = []
    def runTask():
        task.run()
    thread = threading.Thread(target=runTask, daemon=True)
    thread.start()
    # Let it run a few iterations
    time.sleep(0.15)
    task.pause()
    countAtPause = task.completedIterations
    # Wait while paused — completedIterations should not increase
    time.sleep(0.3)
    completedWhenPaused.append(task.completedIterations)
    task.resume()
    thread.join(timeout=5)
    # Should not have progressed while paused
    assert completedWhenPaused[0] == countAtPause or completedWhenPaused[0] <= countAtPause + 1


def test_cancelWhilePaused(qtbot):
    """cancel() unblocks a paused thread and ends in CANCELLED status."""
    task = SlowTask(name='CancelPausedTest', iterations=50, iterationDelayMs=50)
    task.setStatus(TaskStatus.RUNNING)
    thread = threading.Thread(target=task.run, daemon=True)
    thread.start()
    time.sleep(0.1)
    task.pause()
    time.sleep(0.05)
    assert task.status == TaskStatus.PAUSED
    with qtbot.waitSignal(task.taskFinished, timeout=3000):
        task.cancel()
    thread.join(timeout=3)
    assert task.status == TaskStatus.CANCELLED
    assert not task._isPaused


def test_pauseResumeCycle(qtbot):
    """Full pause/resume cycle: task pauses mid-execution then continues to COMPLETED."""
    task = SlowTask(name='CycleTest', iterations=10, iterationDelayMs=30)
    thread = threading.Thread(target=task.run, daemon=True)
    thread.start()
    time.sleep(0.05)
    task.pause()
    time.sleep(0.15)
    task.resume()
    with qtbot.waitSignal(task.taskFinished, timeout=5000):
        pass
    thread.join(timeout=5)
    assert task.status == TaskStatus.COMPLETED
    assert task.completedIterations == 10
