import datetime
from pathlib import Path
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QProgressBar, QTableWidgetItem
from core import BaseController, Config, logger
from core.QtAppContext import QtAppContext
from core.taskSystem.TaskStatus import TaskStatus
from app.windows.main.main_window import Ui_MainWindow

class MainController(Ui_MainWindow, BaseController, QMainWindow):
    slot_map = {'addSimpleTask': ['btnAddSimpleTask', 'clicked'], 'addScheduledTask': ['btnAddScheduledTask', 'clicked'], 'addConditionTask': ['btnAddConditionTask', 'clicked'], 'addLoopTask': ['btnAddLoopTask', 'clicked'], 'addConcurrentTasks': ['btnAddConcurrentTasks', 'clicked'], 'createCpuIntensiveTask': ['btnAddCpuIntensiveTask', 'clicked'], 'addChainTask': ['btnAddChainTask', 'clicked'], 'addRetryChainTask': ['btnAddRetryChainTask', 'clicked'], 'exitApp': ['actionExit', 'triggered'], 'addNewTask': ['actionNewTask', 'triggered'], 'addNewScheduledTask': ['actionNewScheduledTask', 'triggered'], 'runConcurrentTasks': ['actionRunConcurrentTasks', 'triggered'], 'cpuIntensiveTask': ['actionCpuIntensiveTask', 'triggered']}

    def __init__(self, parent=None):
        ctx = QtAppContext.globalInstance()
        self.taskManager = ctx.taskManager
        self.taskProgress = {}
        super().__init__(parent)
        self.setupSignalHandlers()
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateAll)
        self.updateTimer.start(1000)
        self.initializeUi()

    def initializeUi(self):
        """Initialize UI components"""
        config = Config()
        self.setWindowTitle(config.get('app.name', 'Qt Base App - by Zuko'))
        icon_path = Path('assets/icon.png')
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
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
        self.logMessage('Application started')
        self.logMessage('Task System Demo Ready')

    def setupSignalHandlers(self):
        """Connect TaskManagerService signals for UI updates."""
        if not self.taskManager:
            logger.warning('TaskManagerService is not available from QtAppContext')
            return
        self.taskManager.taskAdded.connect(self.onTaskAdded)
        self.taskManager.taskRemoved.connect(self.updateTaskTable)
        self.taskManager.taskStatusUpdated.connect(self.onTaskStatusUpdated)
        self.taskManager.taskProgressUpdated.connect(self.onTaskProgress)
        self.taskManager.failedTaskLogged.connect(self.onFailedTaskLogged)

    def updateAll(self):
        """Update all UI components"""
        self.updateTaskTable()
        self.updateScheduleTable()
        self.updateActiveTasksCount()

    def updateActiveTasksCount(self):
        """Update the active tasks count label"""
        qs = self.taskManager.getQueueStatus() if self.taskManager else {}
        running = qs.get('running', 0)
        maxThreads = qs.get('maxConcurrent', 0)
        self.lblActiveTasks.setText(f'Active Tasks: {running}/{maxThreads}')

    def updateTaskTable(self):
        """Update the tasks table"""
        selectedRows = self.tableTasks.selectionModel().selectedRows()
        selectedId = None
        if selectedRows:
            selectedItem = self.tableTasks.item(selectedRows[0].row(), 0)
            if selectedItem:
                selectedId = selectedItem.data(Qt.UserRole)
        self.tableTasks.setRowCount(0)
        tasks = self.taskManager.getAllTasks() if self.taskManager else []
        topLevelTasks = [t for t in tasks if not t.get('isChainChild', False)]
        for row, task in enumerate(topLevelTasks):
            self.tableTasks.insertRow(row)
            uuid = task.get('uuid')
            idItem = QTableWidgetItem(uuid[:8] + '...')
            idItem.setData(Qt.UserRole, uuid)
            self.tableTasks.setItem(row, 0, idItem)
            name = task.get('name', '')
            if 'subTasks' in task:
                name = f"🔗 {name} ({len(task['subTasks'])} steps)"
            nameItem = QTableWidgetItem(name)
            self.tableTasks.setItem(row, 1, nameItem)
            statusStr = task.get('status', 'PENDING')
            statusItem = QTableWidgetItem(statusStr)
            self.tableTasks.setItem(row, 2, statusItem)
            progress = self.taskProgress.get(uuid, task.get('progress', 0))
            progressBar = QProgressBar()
            progressBar.setRange(0, 100)
            progressBar.setValue(progress)
            self.tableTasks.setCellWidget(row, 3, progressBar)
            createdIso = task.get('createdAt')
            try:
                createdTime = datetime.datetime.fromisoformat(createdIso).strftime('%Y-%m-%d %H:%M:%S') if createdIso else '-'
            except Exception:
                createdTime = createdIso or '-'
            timeItem = QTableWidgetItem(createdTime)
            self.tableTasks.setItem(row, 4, timeItem)
            if selectedId and uuid == selectedId:
                self.tableTasks.selectRow(row)

    def updateScheduleTable(self):
        """Update the schedules table"""
        self.tableSchedules.setRowCount(0)
        for row, schedule in enumerate(self.taskManager.getScheduledJobs() if self.taskManager else []):
            self.tableSchedules.insertRow(row)
            idItem = QTableWidgetItem(schedule.get('task_uuid', '')[:8] + '...')
            idItem.setData(Qt.UserRole, schedule.get('task_uuid'))
            self.tableSchedules.setItem(row, 0, idItem)
            nameItem = QTableWidgetItem(schedule.get('name', ''))
            self.tableSchedules.setItem(row, 1, nameItem)
            statusItem = QTableWidgetItem(schedule.get('trigger', 'date'))
            self.tableSchedules.setItem(row, 2, statusItem)
            nextRunIso = schedule.get('next_run_time')
            try:
                nextRun = datetime.datetime.fromisoformat(nextRunIso).strftime('%H:%M:%S') if nextRunIso else '-'
            except Exception:
                nextRun = nextRunIso or '-'
            timeItem = QTableWidgetItem(nextRun)
            self.tableSchedules.setItem(row, 3, timeItem)
            remainingText = '-'
            if nextRunIso:
                try:
                    dt = datetime.datetime.fromisoformat(nextRunIso)
                    delta = (dt - datetime.datetime.now()).total_seconds()
                    if delta > 0:
                        remainingText = f'{int(delta)} seconds'
                except Exception:
                    pass
            remainingItem = QTableWidgetItem(remainingText)
            self.tableSchedules.setItem(row, 4, remainingItem)

    def logMessage(self, message):
        """Log a message to the Logs tab"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        logText = f'[{timestamp}] {message}'
        self.txtLogs.append(logText)
        logger.info(message)

    def onScheduleAdded(self, schedule):
        """Handle when a schedule is added"""
        self.logMessage(f'Schedule added: {schedule.task.name} ({schedule.task.id[:8]})')
        self.updateScheduleTable()

    def onScheduleRemoved(self, taskId):
        """Handle when a schedule is removed"""
        self.logMessage(f'Schedule removed: {taskId[:8]}')
        self.updateScheduleTable()

    def onScheduleUpdated(self, schedule):
        """Handle when a schedule is updated"""
        self.updateScheduleTable()

    def onTaskAdded(self, uuid: str):
        try:
            taskInfo = self.taskManager._taskTracker.getTaskInfo(uuid)
            if taskInfo.get('isChainChild', False):
                parentName = taskInfo.get('parentChainName', 'Unknown Chain')
                self.logMessage(f"Chain step added: {taskInfo.get('name')} (in {parentName})")
            else:
                self.logMessage(f'Task added: {uuid[:8]}')
        except Exception:
            self.logMessage(f'Task added: {uuid[:8]}')
        self.updateTaskTable()

    def onTaskStatusUpdated(self, uuid, status):
        """Handle when a task status changes (RUNNING/COMPLETED/FAILED/CANCELLED/RETRYING)."""
        try:
            statusName = status.name if isinstance(status, TaskStatus) else str(status)
        except Exception:
            statusName = str(status)
        try:
            taskInfo = self.taskManager._taskTracker.getTaskInfo(uuid)
            name = taskInfo.get('name', uuid[:8])
            if taskInfo.get('isChainChild', False):
                parentName = taskInfo.get('parentChainName', 'Unknown Chain')
                self.logMessage(f"Step '{name}' in '{parentName}': {statusName}")
            else:
                self.logMessage(f"Task '{name}' ({uuid[:8]}): {statusName}")
        except Exception:
            self.logMessage(f'Task {uuid[:8]} status: {statusName}')
        if statusName in ('COMPLETED', 'FAILED', 'CANCELLED'):
            if statusName == 'COMPLETED':
                self.taskProgress[uuid] = 100
        self.updateTaskTable()
        self.updateActiveTasksCount()

    def onTaskProgress(self, uuid, progress):
        """Handle when a task reports progress"""
        self.taskProgress[uuid] = progress
        if progress % 25 == 0 or progress == 100:
            try:
                taskInfo = self.taskManager._taskTracker.getTaskInfo(uuid)
                if not taskInfo.get('isChainChild', False):
                    self.logMessage(f'Task progress: {uuid[:8]} - {progress}%')
            except Exception:
                pass

    def onFailedTaskLogged(self, taskInfo: dict):
        uuid = taskInfo.get('uuid', '')
        name = taskInfo.get('name', '')
        err = taskInfo.get('error', '')
        if taskInfo.get('isChainChild', False):
            parentName = taskInfo.get('parentChainName', 'Unknown Chain')
            self.logMessage(f'Step failed: {name} in {parentName} - Error: {err}')
        else:
            self.logMessage(f'Task failed logged: {name} ({uuid[:8]}) - Error: {err}')
        self.updateTaskTable()
        self.updateActiveTasksCount()

    def onTaskStarted(self, taskId):
        pass

    def onTaskCompleted(self, taskId, result):
        pass

    def onTaskFailed(self, taskId, error):
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            if self.taskManager:
                self.taskManager.shutdown()
        except Exception as e:
            logger.error(f'Error during TaskManagerService shutdown: {e}')
        self.updateTimer.stop()
        super().closeEvent(event)
