import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp, QDialog, QLineEdit, QPushButton, QSlider
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, QCoreApplication
from pynput.keyboard import Listener, Key, KeyCode
import win32gui
import win32con
import win32api
import winxpgui


class Transparency(QDialog):
    def __init__(self):
        QWidget.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.setupUI()

    def setupUI(self):
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle("윈도우 투명도")
        self.setWindowIcon(QIcon('icon.png'))

        target_label = QLabel("적용대상 : ")
        target_name = QLabel(self.wintitle)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(100)
        self.sliderVal_label = QLabel(str(self.slider.value()))
        self.pushButton1= QPushButton("적용")
        self.slider.valueChanged.connect(self.sliderValue)

        layout = QGridLayout()
        layout.addWidget(target_label, 0, 0)
        layout.addWidget(target_name, 0, 1)
        layout.addWidget(self.slider, 1, 0)
        layout.addWidget(self.sliderVal_label, 1, 1)
        layout.addWidget(self.pushButton1, 2, 0)

        self.setLayout(layout)

    def sliderValue(self):
        sliderVal = self.slider.value()
        self.sliderVal_label.setText(str(sliderVal))

        handle = self.handle
        wintitle = self.wintitle
        tranVal = int(self.slider.value())
        tranVal = round(tranVal * 2.55)

        if wintitle != "윈도우 투명도" and wintitle != "Windows Controller":
            win32gui.SetWindowLong(handle, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            winxpgui.SetLayeredWindowAttributes(handle, win32api.RGB(0, 0, 0), tranVal, win32con.LWA_ALPHA)


def windows_transparency():
    Transparency.handle = win32gui.GetForegroundWindow()
    Transparency.wintitle = win32gui.GetWindowText(Transparency.handle)

    dlg = Transparency()
    dlg.exec_()


def always_on_top():
    handle = win32gui.GetForegroundWindow()

    # win32gui.SetWindowPos(핸들, 옵션, x, y, ox, oy, flag)
    win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


def always_on_top_off():
    handle = win32gui.GetForegroundWindow()

    # win32gui.SetWindowPos(핸들, 옵션, x, y, ox, oy, flag)
    win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


class GetKeyInput(QThread):
    keySign = pyqtSignal(object)
    keyStore = set()
    HOT_KEYS = {
        "windows_transparency": set([Key.ctrl_l, Key.alt_l, Key.f1])
        , "always_on_top": set([Key.ctrl_l, Key.alt_l, Key.f2])
        , "always_on_top_off": set([Key.ctrl_l, Key.alt_l, Key.f3])
    }

    def __init__(self, parent):
        QThread.__init__(self, parent)

    def addKeyInputEventListener(self, listener):
        self.keySign.connect(listener)

    def onPress(self, key):
        self.keyStore.add(key)

        for action, trigger in self.HOT_KEYS.items():
            check = all([True if triggerKey in self.keyStore else False for triggerKey in trigger])

            if check:
                self.keySign.emit(action)

    def onRelease(self, key):
        if key in self.keyStore:
            self.keyStore.remove(key)

    def run(self):
        with Listener(on_press=self.onPress, on_release=self.onRelease) as listener:
            listener.join()


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(280, 80))  # Set sizes
        self.setWindowTitle("Windows Controller")  # Set a title
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget

        grid_layout = QGridLayout(self)  # Create a QGridLayout
        central_widget.setLayout(grid_layout)  # Set the layout into the central widget

        transparency_label = QLabel("ctrl + alt + F1 = 화면 투명도")
        alwaysOnTop_label = QLabel("ctrl + alt + F2 = 화면 최상위")
        alwaysOnTopOff_label = QLabel("ctrl + alt + F3 = 화면 최상위 해제")
        grid_layout.addWidget(transparency_label, 0, 0)
        grid_layout.addWidget(alwaysOnTop_label, 1, 0)
        grid_layout.addWidget(alwaysOnTopOff_label, 2, 0)

        # Add a checkbox, which will depend on the behavior of the program when the window is closed
        self.check_box = QCheckBox('트레이에 숨기기')
        grid_layout.addWidget(self.check_box, 3, 0)
        grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 3, 1)

        git_label = QLabel('<a href="https://github.com/jo94kr/windowsController">Made By Jo</a>')
        git_label.setOpenExternalLinks(True)
        grid_layout.addWidget(git_label, 3, 3)

        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

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

        self.__get_Key_Input_thread = GetKeyInput(self)
        self.__get_Key_Input_thread.addKeyInputEventListener(self.onKeyInputEvent)
        self.__get_Key_Input_thread.start()

    def onKeyInputEvent(self, action):
        try:
            action = eval(action)
            if callable(action):
                action()
        except NameError as e:
            pass

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
        else:
            QCoreApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 다이얼로그창 닫아도 프로그램 종료 유무 옵션
    QApplication.setQuitOnLastWindowClosed(False)

    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
