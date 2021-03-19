import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp
from PyQt5.QtCore import QSize, Qt, QThread
from pynput.keyboard import Listener
import win32gui
import win32con
import win32api
import winxpgui


class Test(QThread):
    def run(self):
        self.listener()

    def listener(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        keyStore = set()

        print(key)
        # handle = win32gui.GetForegroundWindow()
        # wintitle = win32gui.GetWindowText(handle)
        #
        # print(handle)
        # print(wintitle)
        #
        # win32gui.SetWindowLong(handle, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # winxpgui.SetLayeredWindowAttributes(handle, win32api.RGB(0, 0, 0), 50, win32con.LWA_ALPHA)


class MainWindow(QMainWindow):
    tray_icon = None

    def __init__(self):
        # Be sure to call the super class method
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(280, 80))  # Set sizes
        self.setWindowTitle("Windows Controller")  # Set a title
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget

        grid_layout = QGridLayout(self)  # Create a QGridLayout
        central_widget.setLayout(grid_layout)  # Set the layout into the central widget
        grid_layout.addWidget(QLabel(" test ", self), 0, 0)

        # Add a checkbox, which will depend on the behavior of the program when the window is closed
        self.check_box = QCheckBox('트레이에 숨기기')
        grid_layout.addWidget(self.check_box, 1, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        show_action = QAction("보이기", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("숨기기", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.test = Test()
        self.test.start()

    def closeEvent(self, event):
        if self.check_box.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Windows Controller",
                "프로그램이 트레이에 최소화됩니다.",
                QSystemTrayIcon.Information,
                2000
            )

    def keyPressEvent(self, e):
        print(e.key)
        if e.key() == Qt.Key_F:
            self.tray_icon.showMessage("Windows Controller", "프로그램이 트레이에 최소화됩니다.", QSystemTrayIcon.Information, 2000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
