# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 650)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionNewTask = QAction(MainWindow)
        self.actionNewTask.setObjectName(u"actionNewTask")
        self.actionNewScheduledTask = QAction(MainWindow)
        self.actionNewScheduledTask.setObjectName(u"actionNewScheduledTask")
        self.actionRunConcurrentTasks = QAction(MainWindow)
        self.actionRunConcurrentTasks.setObjectName(u"actionRunConcurrentTasks")
        self.actionCpuIntensiveTask = QAction(MainWindow)
        self.actionCpuIntensiveTask.setObjectName(u"actionCpuIntensiveTask")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabTasks = QWidget()
        self.tabTasks.setObjectName(u"tabTasks")
        self.verticalLayout_2 = QVBoxLayout(self.tabTasks)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxActions = QGroupBox(self.tabTasks)
        self.groupBoxActions.setObjectName(u"groupBoxActions")
        self.horizontalLayout = QHBoxLayout(self.groupBoxActions)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnAddSimpleTask = QPushButton(self.groupBoxActions)
        self.btnAddSimpleTask.setObjectName(u"btnAddSimpleTask")

        self.horizontalLayout.addWidget(self.btnAddSimpleTask)

        self.btnAddScheduledTask = QPushButton(self.groupBoxActions)
        self.btnAddScheduledTask.setObjectName(u"btnAddScheduledTask")

        self.horizontalLayout.addWidget(self.btnAddScheduledTask)

        self.btnAddConditionTask = QPushButton(self.groupBoxActions)
        self.btnAddConditionTask.setObjectName(u"btnAddConditionTask")

        self.horizontalLayout.addWidget(self.btnAddConditionTask)

        self.btnAddLoopTask = QPushButton(self.groupBoxActions)
        self.btnAddLoopTask.setObjectName(u"btnAddLoopTask")

        self.horizontalLayout.addWidget(self.btnAddLoopTask)


        self.verticalLayout_2.addWidget(self.groupBoxActions)

        self.groupBoxConcurrent = QGroupBox(self.tabTasks)
        self.groupBoxConcurrent.setObjectName(u"groupBoxConcurrent")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxConcurrent)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btnAddConcurrentTasks = QPushButton(self.groupBoxConcurrent)
        self.btnAddConcurrentTasks.setObjectName(u"btnAddConcurrentTasks")

        self.horizontalLayout_2.addWidget(self.btnAddConcurrentTasks)

        self.btnAddCpuIntensiveTask = QPushButton(self.groupBoxConcurrent)
        self.btnAddCpuIntensiveTask.setObjectName(u"btnAddCpuIntensiveTask")

        self.horizontalLayout_2.addWidget(self.btnAddCpuIntensiveTask)

        self.btnAddChainTask = QPushButton(self.groupBoxConcurrent)
        self.btnAddChainTask.setObjectName(u"btnAddChainTask")

        self.horizontalLayout_2.addWidget(self.btnAddChainTask)

        self.btnAddRetryChainTask = QPushButton(self.groupBoxConcurrent)
        self.btnAddRetryChainTask.setObjectName(u"btnAddRetryChainTask")

        self.horizontalLayout_2.addWidget(self.btnAddRetryChainTask)

        self.lblActiveTasks = QLabel(self.groupBoxConcurrent)
        self.lblActiveTasks.setObjectName(u"lblActiveTasks")

        self.horizontalLayout_2.addWidget(self.lblActiveTasks)


        self.verticalLayout_2.addWidget(self.groupBoxConcurrent)

        self.tableTasks = QTableWidget(self.tabTasks)
        if (self.tableTasks.columnCount() < 5):
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
        self.tableTasks.setObjectName(u"tableTasks")
        self.tableTasks.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout_2.addWidget(self.tableTasks)

        self.tabWidget.addTab(self.tabTasks, "")
        self.tabSchedules = QWidget()
        self.tabSchedules.setObjectName(u"tabSchedules")
        self.verticalLayout_3 = QVBoxLayout(self.tabSchedules)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tableSchedules = QTableWidget(self.tabSchedules)
        if (self.tableSchedules.columnCount() < 5):
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
        self.tableSchedules.setObjectName(u"tableSchedules")
        self.tableSchedules.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout_3.addWidget(self.tableSchedules)

        self.tabWidget.addTab(self.tabSchedules, "")
        self.tabLogs = QWidget()
        self.tabLogs.setObjectName(u"tabLogs")
        self.verticalLayout_4 = QVBoxLayout(self.tabLogs)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.txtLogs = QTextEdit(self.tabLogs)
        self.txtLogs.setObjectName(u"txtLogs")
        self.txtLogs.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.txtLogs)

        self.tabWidget.addTab(self.tabLogs, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuTask = QMenu(self.menubar)
        self.menuTask.setObjectName(u"menuTask")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionNewTask.setText(QCoreApplication.translate("MainWindow", u"New Task", None))
        self.actionNewScheduledTask.setText(QCoreApplication.translate("MainWindow", u"New Scheduled Task", None))
        self.actionRunConcurrentTasks.setText(QCoreApplication.translate("MainWindow", u"Run Concurrent Tasks", None))
        self.actionCpuIntensiveTask.setText(QCoreApplication.translate("MainWindow", u"CPU Intensive Task", None))
        self.groupBoxActions.setTitle(QCoreApplication.translate("MainWindow", u"Basic Tasks", None))
        self.btnAddSimpleTask.setText(QCoreApplication.translate("MainWindow", u"Add Simple Task", None))
        self.btnAddScheduledTask.setText(QCoreApplication.translate("MainWindow", u"Add Scheduled Task (15s)", None))
        self.btnAddConditionTask.setText(QCoreApplication.translate("MainWindow", u"Add Condition Task", None))
        self.btnAddLoopTask.setText(QCoreApplication.translate("MainWindow", u"Add Loop Task", None))
        self.groupBoxConcurrent.setTitle(QCoreApplication.translate("MainWindow", u"Concurrent Execution", None))
        self.btnAddConcurrentTasks.setText(QCoreApplication.translate("MainWindow", u"Run 5 Concurrent Tasks", None))
        self.btnAddCpuIntensiveTask.setText(QCoreApplication.translate("MainWindow", u"Add CPU Intensive Task", None))
        self.btnAddChainTask.setText(QCoreApplication.translate("MainWindow", u"Add Chain Task", None))
        self.btnAddRetryChainTask.setText(QCoreApplication.translate("MainWindow", u"Add Retry Chain", None))
        self.lblActiveTasks.setText(QCoreApplication.translate("MainWindow", u"Active Tasks: 0/10", None))
        ___qtablewidgetitem = self.tableTasks.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem1 = self.tableTasks.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Name", None));
        ___qtablewidgetitem2 = self.tableTasks.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtablewidgetitem3 = self.tableTasks.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Progress", None));
        ___qtablewidgetitem4 = self.tableTasks.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Created", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTasks), QCoreApplication.translate("MainWindow", u"Tasks", None))
        ___qtablewidgetitem5 = self.tableSchedules.horizontalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Task ID", None));
        ___qtablewidgetitem6 = self.tableSchedules.horizontalHeaderItem(1)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Task Name", None));
        ___qtablewidgetitem7 = self.tableSchedules.horizontalHeaderItem(2)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtablewidgetitem8 = self.tableSchedules.horizontalHeaderItem(3)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Next Run", None));
        ___qtablewidgetitem9 = self.tableSchedules.horizontalHeaderItem(4)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"Remaining", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSchedules), QCoreApplication.translate("MainWindow", u"Schedules", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLogs), QCoreApplication.translate("MainWindow", u"Logs", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuTask.setTitle(QCoreApplication.translate("MainWindow", u"Task", None))
    # retranslateUi

