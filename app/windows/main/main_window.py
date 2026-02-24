# -*- coding: utf-8 -*-

#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMenuBar,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName('MainWindow')
        MainWindow.resize(900, 650)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName('actionExit')
        self.actionNewTask = QAction(MainWindow)
        self.actionNewTask.setObjectName('actionNewTask')
        self.actionNewScheduledTask = QAction(MainWindow)
        self.actionNewScheduledTask.setObjectName('actionNewScheduledTask')
        self.actionRunConcurrentTasks = QAction(MainWindow)
        self.actionRunConcurrentTasks.setObjectName('actionRunConcurrentTasks')
        self.actionCpuIntensiveTask = QAction(MainWindow)
        self.actionCpuIntensiveTask.setObjectName('actionCpuIntensiveTask')
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName('verticalLayout')
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName('tabWidget')
        self.tabTasks = QWidget()
        self.tabTasks.setObjectName('tabTasks')
        self.verticalLayout_2 = QVBoxLayout(self.tabTasks)
        self.verticalLayout_2.setObjectName('verticalLayout_2')
        self.groupBoxActions = QGroupBox(self.tabTasks)
        self.groupBoxActions.setObjectName('groupBoxActions')
        self.horizontalLayout = QHBoxLayout(self.groupBoxActions)
        self.horizontalLayout.setObjectName('horizontalLayout')
        self.btnAddSimpleTask = QPushButton(self.groupBoxActions)
        self.btnAddSimpleTask.setObjectName('btnAddSimpleTask')
        self.horizontalLayout.addWidget(self.btnAddSimpleTask)
        self.btnAddScheduledTask = QPushButton(self.groupBoxActions)
        self.btnAddScheduledTask.setObjectName('btnAddScheduledTask')
        self.horizontalLayout.addWidget(self.btnAddScheduledTask)
        self.btnAddConditionTask = QPushButton(self.groupBoxActions)
        self.btnAddConditionTask.setObjectName('btnAddConditionTask')
        self.horizontalLayout.addWidget(self.btnAddConditionTask)
        self.btnAddLoopTask = QPushButton(self.groupBoxActions)
        self.btnAddLoopTask.setObjectName('btnAddLoopTask')
        self.horizontalLayout.addWidget(self.btnAddLoopTask)
        self.verticalLayout_2.addWidget(self.groupBoxActions)
        self.groupBoxConcurrent = QGroupBox(self.tabTasks)
        self.groupBoxConcurrent.setObjectName('groupBoxConcurrent')
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxConcurrent)
        self.horizontalLayout_2.setObjectName('horizontalLayout_2')
        self.btnAddConcurrentTasks = QPushButton(self.groupBoxConcurrent)
        self.btnAddConcurrentTasks.setObjectName('btnAddConcurrentTasks')
        self.horizontalLayout_2.addWidget(self.btnAddConcurrentTasks)
        self.btnAddCpuIntensiveTask = QPushButton(self.groupBoxConcurrent)
        self.btnAddCpuIntensiveTask.setObjectName('btnAddCpuIntensiveTask')
        self.horizontalLayout_2.addWidget(self.btnAddCpuIntensiveTask)
        self.btnAddChainTask = QPushButton(self.groupBoxConcurrent)
        self.btnAddChainTask.setObjectName('btnAddChainTask')
        self.horizontalLayout_2.addWidget(self.btnAddChainTask)
        self.btnAddRetryChainTask = QPushButton(self.groupBoxConcurrent)
        self.btnAddRetryChainTask.setObjectName('btnAddRetryChainTask')
        self.horizontalLayout_2.addWidget(self.btnAddRetryChainTask)
        self.lblActiveTasks = QLabel(self.groupBoxConcurrent)
        self.lblActiveTasks.setObjectName('lblActiveTasks')
        self.horizontalLayout_2.addWidget(self.lblActiveTasks)
        self.verticalLayout_2.addWidget(self.groupBoxConcurrent)
        self.tableTasks = QTableWidget(self.tabTasks)
        if self.tableTasks.columnCount() < 5:
            self.tableTasks.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableTasks.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableTasks.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableTasks.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableTasks.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableTasks.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tableTasks.setObjectName('tableTasks')
        self.tableTasks.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalLayout_2.addWidget(self.tableTasks)
        self.tabWidget.addTab(self.tabTasks, '')
        self.tabSchedules = QWidget()
        self.tabSchedules.setObjectName('tabSchedules')
        self.verticalLayout_3 = QVBoxLayout(self.tabSchedules)
        self.verticalLayout_3.setObjectName('verticalLayout_3')
        self.tableSchedules = QTableWidget(self.tabSchedules)
        if self.tableSchedules.columnCount() < 5:
            self.tableSchedules.setColumnCount(5)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableSchedules.setHorizontalHeaderItem(0, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableSchedules.setHorizontalHeaderItem(1, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableSchedules.setHorizontalHeaderItem(2, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableSchedules.setHorizontalHeaderItem(3, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableSchedules.setHorizontalHeaderItem(4, __qtablewidgetitem9)
        self.tableSchedules.setObjectName('tableSchedules')
        self.tableSchedules.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalLayout_3.addWidget(self.tableSchedules)
        self.tabWidget.addTab(self.tabSchedules, '')
        self.tabLogs = QWidget()
        self.tabLogs.setObjectName('tabLogs')
        self.verticalLayout_4 = QVBoxLayout(self.tabLogs)
        self.verticalLayout_4.setObjectName('verticalLayout_4')
        self.txtLogs = QTextEdit(self.tabLogs)
        self.txtLogs.setObjectName('txtLogs')
        self.txtLogs.setReadOnly(True)
        self.verticalLayout_4.addWidget(self.txtLogs)
        self.tabWidget.addTab(self.tabLogs, '')
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName('menubar')
        self.menubar.setGeometry(QRect(0, 0, 900, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName('menuFile')
        self.menuTask = QMenu(self.menubar)
        self.menuTask.setObjectName('menuTask')
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName('statusbar')
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTask.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuTask.addAction(self.actionNewTask)
        self.menuTask.addAction(self.actionNewScheduledTask)
        self.menuTask.addSeparator()
        self.menuTask.addAction(self.actionRunConcurrentTasks)
        self.menuTask.addAction(self.actionCpuIntensiveTask)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate('MainWindow', 'MainWindow', None))
        self.actionExit.setText(QCoreApplication.translate('MainWindow', 'Exit', None))
        self.actionNewTask.setText(QCoreApplication.translate('MainWindow', 'New Task', None))
        self.actionNewScheduledTask.setText(QCoreApplication.translate('MainWindow', 'New Scheduled Task', None))
        self.actionRunConcurrentTasks.setText(QCoreApplication.translate('MainWindow', 'Run Concurrent Tasks', None))
        self.actionCpuIntensiveTask.setText(QCoreApplication.translate('MainWindow', 'CPU Intensive Task', None))
        self.groupBoxActions.setTitle(QCoreApplication.translate('MainWindow', 'Basic Tasks', None))
        self.btnAddSimpleTask.setText(QCoreApplication.translate('MainWindow', 'Add Simple Task', None))
        self.btnAddScheduledTask.setText(QCoreApplication.translate('MainWindow', 'Add Scheduled Task (15s)', None))
        self.btnAddConditionTask.setText(QCoreApplication.translate('MainWindow', 'Add Condition Task', None))
        self.btnAddLoopTask.setText(QCoreApplication.translate('MainWindow', 'Add Loop Task', None))
        self.groupBoxConcurrent.setTitle(QCoreApplication.translate('MainWindow', 'Concurrent Execution', None))
        self.btnAddConcurrentTasks.setText(QCoreApplication.translate('MainWindow', 'Run 5 Concurrent Tasks', None))
        self.btnAddCpuIntensiveTask.setText(QCoreApplication.translate('MainWindow', 'Add CPU Intensive Task', None))
        self.btnAddChainTask.setText(QCoreApplication.translate('MainWindow', 'Add Chain Task', None))
        self.btnAddRetryChainTask.setText(QCoreApplication.translate('MainWindow', 'Add Retry Chain', None))
        self.lblActiveTasks.setText(QCoreApplication.translate('MainWindow', 'Active Tasks: 0/10', None))
        ___qtablewidgetitem = self.tableTasks.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate('MainWindow', 'ID', None))
        ___qtablewidgetitem1 = self.tableTasks.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate('MainWindow', 'Name', None))
        ___qtablewidgetitem2 = self.tableTasks.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate('MainWindow', 'Status', None))
        ___qtablewidgetitem3 = self.tableTasks.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate('MainWindow', 'Progress', None))
        ___qtablewidgetitem4 = self.tableTasks.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate('MainWindow', 'Created', None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTasks), QCoreApplication.translate('MainWindow', 'Tasks', None))
        ___qtablewidgetitem5 = self.tableSchedules.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate('MainWindow', 'Task ID', None))
        ___qtablewidgetitem6 = self.tableSchedules.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate('MainWindow', 'Task Name', None))
        ___qtablewidgetitem7 = self.tableSchedules.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate('MainWindow', 'Status', None))
        ___qtablewidgetitem8 = self.tableSchedules.horizontalHeaderItem(3)
        ___qtablewidgetitem8.setText(QCoreApplication.translate('MainWindow', 'Next Run', None))
        ___qtablewidgetitem9 = self.tableSchedules.horizontalHeaderItem(4)
        ___qtablewidgetitem9.setText(QCoreApplication.translate('MainWindow', 'Remaining', None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSchedules), QCoreApplication.translate('MainWindow', 'Schedules', None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLogs), QCoreApplication.translate('MainWindow', 'Logs', None))
        self.menuFile.setTitle(QCoreApplication.translate('MainWindow', 'File', None))
        self.menuTask.setTitle(QCoreApplication.translate('MainWindow', 'Task', None))

    # retranslateUi
