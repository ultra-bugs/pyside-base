#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
import threading
import time

from PySide6.QtCore import QObject, Signal

from core import logger
from core.TaskSystem import TaskManager


class TaskSchedule:
    def __init__(self, task, run_at = None, repeat_interval = None):
        self.task = task
        self.run_at = run_at  # Thời gian chạy (timestamp)
        self.repeat_interval = repeat_interval  # Khoảng thời gian lặp lại (giây)
        self.last_run = None
        self.enabled = True
    
    def should_run(self, current_time):
        if not self.enabled:
            return False
        
        if self.run_at and current_time >= self.run_at:
            # Chạy một lần theo lịch
            if not self.repeat_interval:
                return not self.last_run  # Chỉ chạy nếu chưa từng chạy
            
            # Chạy lặp lại
            if not self.last_run or (current_time - self.last_run) >= self.repeat_interval:
                return True
        
        return False
    
    def mark_as_run(self):
        self.last_run = time.time()
        
        # Nếu không lặp lại, vô hiệu hóa
        if not self.repeat_interval:
            self.enabled = False
    
    def get_time_remaining(self):
        """Trả về thời gian còn lại (giây) trước khi task được chạy"""
        if not self.enabled:
            return None
        
        current_time = time.time()
        
        if self.run_at and current_time < self.run_at:
            return self.run_at - current_time
        
        if self.repeat_interval and self.last_run:
            next_run = self.last_run + self.repeat_interval
            if current_time < next_run:
                return next_run - current_time
        
        return 0  # Sẵn sàng chạy ngay


class TaskSchedulerService(QObject):
    scheduleAdded = Signal(object)  # TaskSchedule
    scheduleRemoved = Signal(str)  # task_id
    scheduleUpdated = Signal(object)  # TaskSchedule
    
    def __init__(self, task_manager = None):
        super().__init__()
        self.task_manager = task_manager or TaskManager()
        self.schedules = {}  # task_id -> TaskSchedule
        self.running = False
        self.scheduler_thread = None
        self.check_interval = 1  # Kiểm tra mỗi 1 giây
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("Task scheduler started")
    
    def stop(self):
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(2)
        logger.info("Task scheduler stopped")
    
    def _scheduler_loop(self):
        while self.running:
            current_time = time.time()
            
            # Kiểm tra các lịch
            for task_id, schedule in list(self.schedules.items()):
                if schedule.should_run(current_time):
                    self._run_scheduled_task(schedule)
                    schedule.mark_as_run()
                    self.scheduleUpdated.emit(schedule)
            
            # Ngủ
            time.sleep(self.check_interval)
    
    def _run_scheduled_task(self, schedule):
        # Chạy task
        self.task_manager.run_task(schedule.task)
    
    def add_schedule(self, task, run_at = None, repeat_interval = None):
        schedule = TaskSchedule(task, run_at, repeat_interval)
        self.schedules[task.id] = schedule
        self.scheduleAdded.emit(schedule)
        return schedule
    
    def remove_schedule(self, task_id):
        if task_id in self.schedules:
            del self.schedules[task_id]
            self.scheduleRemoved.emit(task_id)
            return True
        return False
    
    def get_schedule(self, task_id):
        return self.schedules.get(task_id)
    
    def get_all_schedules(self):
        return list(self.schedules.values())
