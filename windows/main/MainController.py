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
#
import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QProgressBar, QTableWidgetItem

from core import (BaseController, Config, QtAppContext, TaskManager, logger)
from services.TaskSchedulerService import TaskSchedulerService
from windows.main.main_window import Ui_MainWindow


class MainController(Ui_MainWindow, BaseController, QMainWindow):
    slot_map = {
        "add_simple_task": ["btnAddSimpleTask", "clicked"],
        "add_scheduled_task": ["btnAddScheduledTask", "clicked"],
        "add_condition_task": ["btnAddConditionTask", "clicked"],
        "add_loop_task": ["btnAddLoopTask", "clicked"],
        "add_concurrent_tasks": ["btnAddConcurrentTasks", "clicked"],
        "create_cpu_intensive_task": ["btnAddCpuIntensiveTask", "clicked"],
        "exit_app": ["actionExit", "triggered"],
        "add_new_task": ["actionNewTask", "triggered"],
        "add_new_scheduled_task": ["actionNewScheduledTask", "triggered"],
        "run_concurrent_tasks": ["actionRunConcurrentTasks", "triggered"],
        "cpu_intensive_task": ["actionCpuIntensiveTask", "triggered"]
    }
    
    def __init__(self, parent = None):
        # Initialize task manager with maximum concurrent threads
        self.task_manager = TaskManager(max_threads=10)
        self.scheduler_service = TaskSchedulerService(self.task_manager)
        self.scheduler_service.start()
        
        # Set context
        QtAppContext.set("task_manager", self.task_manager)
        QtAppContext.set("scheduler_service", self.scheduler_service)
        
        # Task progress tracking
        self.task_progress = {}  # task_id -> progress percentage
        
        super().__init__(parent)
        self.setup_signal_handlers()
        
        # Timer for updating tables and stats
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_all)
        self.update_timer.start(1000)  # Update every second
        
        # Initialize UI
        self.initialize_ui()
    
    def initialize_ui(self):
        """Initialize UI components"""
        config = Config()
        self.setWindowTitle(config.get("app.name", "Qt Base App - by Zuko"))
        
        # Set window icon
        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Configure table columns
        self.tableTasks.setColumnWidth(0, 100)
        self.tableTasks.setColumnWidth(1, 200)
        self.tableTasks.setColumnWidth(2, 100)
        self.tableTasks.setColumnWidth(3, 150)
        self.tableTasks.setColumnWidth(4, 200)
        
        self.tableSchedules.setColumnWidth(0, 100)
        self.tableSchedules.setColumnWidth(1, 200)
        self.tableSchedules.setColumnWidth(2, 100)
        self.tableSchedules.setColumnWidth(3, 150)
        self.tableSchedules.setColumnWidth(4, 100)
        
        # Log messages
        self.log_message("Application started")
        self.log_message("Task System Demo Ready")
    
    def setup_signal_handlers(self):
        """Set up signal handlers for task and scheduler events"""
        # Scheduler signals
        self.scheduler_service.scheduleAdded.connect(self.on_schedule_added)
        self.scheduler_service.scheduleRemoved.connect(self.on_schedule_removed)
        self.scheduler_service.scheduleUpdated.connect(self.on_schedule_updated)
    
    def update_all(self):
        """Update all UI components"""
        self.update_task_table()
        self.update_schedule_table()
        self.update_active_tasks_count()
    
    def update_active_tasks_count(self):
        """Update the active tasks count label"""
        active_count = self.task_manager.get_active_tasks_count()
        max_threads = self.task_manager.get_max_threads()
        self.lblActiveTasks.setText(f"Active Tasks: {active_count}/{max_threads}")
    
    def update_task_table(self):
        """Update the tasks table"""
        # Save current selection
        selected_rows = self.tableTasks.selectionModel().selectedRows()
        selected_id = None
        if selected_rows:
            selected_item = self.tableTasks.item(selected_rows[0].row(), 0)
            if selected_item:
                selected_id = selected_item.data(Qt.UserRole)
        
        self.tableTasks.setRowCount(0)
        
        for row, task in enumerate(self.task_manager.get_all_tasks()):
            self.tableTasks.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(task.id[:8] + "...")
            id_item.setData(Qt.UserRole, task.id)
            self.tableTasks.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(task.name)
            self.tableTasks.setItem(row, 1, name_item)
            
            # Status
            status_item = QTableWidgetItem(task.status.value)
            self.tableTasks.setItem(row, 2, status_item)
            
            # Progress
            progress = self.task_progress.get(task.id, 0)
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(progress)
            self.tableTasks.setCellWidget(row, 3, progress_bar)
            
            # Created time
            created_time = datetime.datetime.fromtimestamp(task.created_at).strftime("%Y-%m-%d %H:%M:%S")
            time_item = QTableWidgetItem(created_time)
            self.tableTasks.setItem(row, 4, time_item)
            
            # Restore selection if this was the selected row
            if selected_id and task.id == selected_id:
                self.tableTasks.selectRow(row)
    
    def update_schedule_table(self):
        """Update the schedules table"""
        self.tableSchedules.setRowCount(0)
        
        for row, schedule in enumerate(self.scheduler_service.get_all_schedules()):
            self.tableSchedules.insertRow(row)
            
            # Task ID
            id_item = QTableWidgetItem(schedule.task.id[:8] + "...")
            id_item.setData(Qt.UserRole, schedule.task.id)
            self.tableSchedules.setItem(row, 0, id_item)
            
            # Task Name
            name_item = QTableWidgetItem(schedule.task.name)
            self.tableSchedules.setItem(row, 1, name_item)
            
            # Status
            status = "Enabled" if schedule.enabled else "Disabled"
            status_item = QTableWidgetItem(status)
            self.tableSchedules.setItem(row, 2, status_item)
            
            # Next Run Time
            next_run = "-"
            if schedule.run_at and not schedule.last_run:
                next_run = datetime.datetime.fromtimestamp(schedule.run_at).strftime("%H:%M:%S")
            elif schedule.repeat_interval and schedule.last_run:
                next_run_time = schedule.last_run + schedule.repeat_interval
                next_run = datetime.datetime.fromtimestamp(next_run_time).strftime("%H:%M:%S")
            
            time_item = QTableWidgetItem(next_run)
            self.tableSchedules.setItem(row, 3, time_item)
            
            # Remaining Time
            remaining = schedule.get_time_remaining()
            remaining_text = "-"
            if remaining is not None and remaining > 0:
                remaining_text = f"{int(remaining)} seconds"
            
            remaining_item = QTableWidgetItem(remaining_text)
            self.tableSchedules.setItem(row, 4, remaining_item)
    
    def log_message(self, message):
        """Log a message to the Logs tab"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_text = f"[{timestamp}] {message}"
        self.txtLogs.append(log_text)
        logger.info(message)
    
    def on_schedule_added(self, schedule):
        """Handle when a schedule is added"""
        self.log_message(f"Schedule added: {schedule.task.name} ({schedule.task.id[:8]})")
        self.update_schedule_table()
    
    def on_schedule_removed(self, task_id):
        """Handle when a schedule is removed"""
        self.log_message(f"Schedule removed: {task_id[:8]}")
        self.update_schedule_table()
    
    def on_schedule_updated(self, schedule):
        """Handle when a schedule is updated"""
        self.update_schedule_table()
    
    def register_task_signals(self, task):
        """Register task signals for UI updates"""
        task.signals.started.connect(lambda task_id: self.on_task_started(task_id))
        task.signals.progress.connect(lambda task_id, progress: self.on_task_progress(task_id, progress))
        task.signals.completed.connect(lambda task_id, result: self.on_task_completed(task_id, result))
        task.signals.failed.connect(lambda task_id, error: self.on_task_failed(task_id, error))
    
    def on_task_started(self, task_id):
        """Handle when a task is started"""
        task = self.task_manager.get_task(task_id)
        if task:
            self.log_message(f"Task started: {task.name} ({task_id[:8]})")
            self.task_progress[task_id] = 0
            self.update_task_table()
            self.update_active_tasks_count()
    
    def on_task_progress(self, task_id, progress):
        """Handle when a task reports progress"""
        task = self.task_manager.get_task(task_id)
        if task:
            self.task_progress[task_id] = progress
            # Only log major progress steps to avoid too many log entries
            if progress % 25 == 0 or progress == 100:
                self.log_message(f"Task progress: {task.name} ({task_id[:8]}) - {progress}%")
    
    def on_task_completed(self, task_id, result):
        """Handle when a task is completed"""
        task = self.task_manager.get_task(task_id)
        if task:
            self.log_message(f"Task completed: {task.name} ({task_id[:8]})")
            self.task_progress[task_id] = 100
            self.update_task_table()
            self.update_active_tasks_count()
    
    def on_task_failed(self, task_id, error):
        """Handle when a task fails"""
        task = self.task_manager.get_task(task_id)
        if task:
            self.log_message(f"Task failed: {task.name} ({task_id[:8]}) - Error: {error}")
            self.update_task_table()
            self.update_active_tasks_count()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop scheduler
        self.scheduler_service.stop()
        # Stop timer
        self.update_timer.stop()
        
        super().closeEvent(event)
