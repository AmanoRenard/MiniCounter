# coding:utf-8
from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QDateTime
from qframelesswindow import FramelessMainWindow
from qfluentwidgets import FluentIcon, MessageBoxBase, LineEdit, SubtitleLabel
from PyQt6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem
from PyQt6.QtGui import QIcon, QKeyEvent
from Counter_ui import Ui_Form

from pathlib import Path
SRC_PATH = Path.absolute(Path(__file__)).parent

DIR_PATH = Path("C:/ProgramData/MiniCounter")
CNT_FILE = "Counter_1.cnt"
SETTINGS = Path("C:/ProgramData/MiniCounter/settings.ini")
Count = 0
History = []
HistoryText = []

class FileMsgBox(MessageBoxBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.widget.setFixedSize(300,200)
        self._label = SubtitleLabel("请输入文件名", self)
        self._edit = LineEdit(self)
        self._edit.setPlaceholderText("请输入文件昵称，不需要带后缀名。")
        self._edit.setText("Counter_")
        ke = self._edit.keyPressEvent
        self._edit.keyPressEvent = lambda e: self.yesButton.click() if e.key() == Qt.Key.Key_Return else ke(e)
        self.viewLayout.addWidget(self._label)
        self.viewLayout.addWidget(self._edit)
        self.yesButton.setEnabled(False)
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")
        self._edit.textChanged.connect(lambda: self.yesButton.setEnabled(False) if self._edit.text() == "" else self.yesButton.setEnabled(True))

class LoadMsgBox(MessageBoxBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.widget.setFixedSize(300,200)
        self._label = SubtitleLabel("文件已存在，覆盖或导入？", self)
        self.yesButton.setText("覆盖")
        self.cancelButton.setText("导入")
        self.viewLayout.addWidget(self._label)

class Window(FramelessMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setResizeEnabled(False)
        self.titleBar.maxBtn.deleteLater()
        self.titleBar._isDoubleClickEnabled = False
        self.titleBar.raise_()

        self.stackedWidget.setCurrentIndex(0)
        self.NavigationBar.addItem("count", FluentIcon.STOP_WATCH, "计数", onClick=lambda: self.stackedWidget.setCurrentIndex(0))
        self.NavigationBar.addItem("records", FluentIcon.DICTIONARY, "记录", onClick=lambda: self.stackedWidget.setCurrentIndex(1))
        self.NavigationBar.setCurrentItem("count")
        self.NavigationBar.raise_()

        self.lbl_dirpath.setText(str(DIR_PATH))
        self.lbl_filename.setText(CNT_FILE)
        self.lbl_count.setNum(Count)

        self.btn_add.clicked.connect(lambda: self._count(1))
        self.btn_minus.clicked.connect(lambda: self._count(-1))

        if Count == 10000:
            self.btn_add.setEnabled(False)
        if Count == 0:
            self.btn_minus.setEnabled(False)

        self.btn_filename.clicked.connect(self._set_filename)
        self.btn_pathselect.clicked.connect(self._set_dirpath)

        ke = self.edit_desc.keyPressEvent
        self.edit_desc.keyPressEvent = lambda e: self.btn_add.click() if e.key() == Qt.Key.Key_Return else ke(e)

        self._list_records()

        self.setWindowIcon(QIcon(str(SRC_PATH / "fox.ico")))
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MiniCounter")

    def _list_records(self):
        self.TreeWidget.clear()
        _dates = set([i[1].split()[0] for i in History])
        for records in History:
            _date, _time = records[1].split()
            if _date not in _dates or self.TreeWidget.topLevelItem(0) == None or self.TreeWidget.topLevelItem(0).text(0) != _date:
                _item = QTreeWidgetItem()
                _item.setText(0, _date)
                self.TreeWidget.insertTopLevelItem(0, _item)
            _child = QTreeWidgetItem()
            _child.setText(0, records[0] + "              ")
            _child.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
            _child.setText(1, _time + "    ")
            _child.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            _child.setText(2, records[2] + "    ")
            _child.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)
            self.TreeWidget.topLevelItem(0).insertChild(0, _child)
        if self.TreeWidget.topLevelItem(0) != None:
            self.TreeWidget.topLevelItem(0).setExpanded(True)


    def _count(self, num):
        global Count, History, HistoryText
        Count = Count + num
        self.lbl_count.setNum(Count)
        if num == 1:
            if Count == 10000:
                self.btn_add.setEnabled(False)
            if not self.btn_minus.isEnabled():
                self.btn_minus.setEnabled(True)
            _desc = self.edit_desc.text().replace('|','')
            with open(DIR_PATH / CNT_FILE, "r+", encoding="utf-8") as f:
                f.seek(0,0)
                f.write(f"CNT|{Count:0>5}\n")
                f.seek(0,2)
                text = f"{Count}|{QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')}|{_desc}\n"
                f.write(text)
            History.append(text.strip().split("|"))
            HistoryText.append(text)
            self.edit_desc.setText("")

            _date = QDateTime.currentDateTime().toString("yyyy-MM-dd")
            if self.TreeWidget.topLevelItem(0) == None or self.TreeWidget.topLevelItem(0).text(0) != _date:
                _item = QTreeWidgetItem()
                _item.setText(0, _date)
                self.TreeWidget.insertTopLevelItem(0, _item)
            self.TreeWidget.topLevelItem(0).setExpanded(True)
            _child = QTreeWidgetItem()
            _child.setText(0, str(Count) + "              ")
            _child.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
            _child.setText(1, QDateTime.currentDateTime().toString("HH:mm:ss    "))
            _child.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            _child.setText(2, _desc + "    ")
            _child.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)
            self.TreeWidget.topLevelItem(0).insertChild(0, _child)
        else:
            if Count == 0:
                self.btn_minus.setEnabled(False)
            if not self.btn_add.isEnabled():
                self.btn_add.setEnabled(True)
            with open(DIR_PATH / CNT_FILE, "r+", encoding="utf-8") as f:
                f.seek(0,0)
                _lines = f.readlines()
                _lines[0] = f"CNT|{Count:0>5}\n"
                f.seek(0, 0)
                f.truncate(0)
                f.writelines(_lines[:-1])

            '''
            f.seek(0,0)
            f.write(bytes(f"CNT|{Count:0>5}\n", encoding="utf-8"))
            f.seek(0,2)
            _pos = f.tell() - 5
            while (_pos) > 0:
                f.seek(_pos)
                _char = f.read(1)
                if _char == bytes("\n", encoding="utf-8"):
                    f.truncate(_pos + 1)
                    break
                _pos -= 1
            '''
            if self.TreeWidget.topLevelItem(0) != None and self.TreeWidget.topLevelItem(0).child(0) != None:
                History = History[:-1]
                HistoryText = HistoryText[:-1]
                self.TreeWidget.topLevelItem(0).takeChild(0)
                if self.TreeWidget.topLevelItem(0).child(0) == None:
                    self.TreeWidget.takeTopLevelItem(0)



    def _set_filename(self):
        global CNT_FILE
        msg = FileMsgBox(self)
        msg._edit.setCursorPosition(8)
        msg._edit.setFocus()
        if msg.exec():
            CNT_FILE = msg._edit.text() + ".cnt"
            if not (cnt := DIR_PATH / CNT_FILE).exists() or (not cnt.is_file() and cnt.exists()):
                with open(cnt, "w", encoding="utf-8") as f:
                    f.write(f"CNT|{Count:0>5}\n")
                    f.writelines(HistoryText)

            else:
                self._load_file()
                with open(SETTINGS, "w", encoding="utf-8") as f:
                    f.writelines([f"DIR_PATH|{DIR_PATH}\n", f"CNT_FILE|{CNT_FILE}\n"])
            self.lbl_filename.setText(CNT_FILE)

    def _load_file(self):
        global Count, HistoryText, History
        _w = LoadMsgBox(self)
        if _w.exec():
            with open(DIR_PATH / CNT_FILE, "w", encoding="utf-8") as f:
                f.write(f"CNT|{Count:0>5}\n")
                f.writelines(HistoryText)
        else:
            with open(DIR_PATH / CNT_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if len(lines) < 1 or not lines[0].startswith("CNT|"):
                with open(DIR_PATH / CNT_FILE, "w", encoding="utf-8") as f:
                    f.write(f"CNT|{Count:0>5}\n")
                    f.writelines(HistoryText)
            else:
                self.edit_desc.setText("")
                Count = int(lines[0][4:].strip())
                self.lbl_count.setNum(Count)
                HistoryText = lines[1:]
                History = [i.strip().split("|") for i in HistoryText]
                self._list_records()

    def _set_dirpath(self):
        global DIR_PATH
        _dir = QFileDialog.getExistingDirectory(self, "选择计数文件保存目录", str(DIR_PATH))
        if not _dir:
            return
        if not (init_path:=Path(_dir)).exists() or (not init_path.is_dir() and init_path.exists()):
            init_path.mkdir(parents=True)
        DIR_PATH = Path(_dir)
        self.lbl_dirpath.setText(str(DIR_PATH))
        with open(SETTINGS, "w", encoding="utf-8") as f:
            f.writelines([f"DIR_PATH|{DIR_PATH}\n", f"CNT_FILE|{CNT_FILE}\n"])
        if not (cnt := DIR_PATH / CNT_FILE).exists() or (not cnt.is_file() and cnt.exists()):
            with open(cnt, "w", encoding="utf-8") as f:
                f.write(f"CNT|{Count:0>5}\n")
                f.writelines(HistoryText)
        else:
                self._load_file()

if __name__ == '__main__':
    if not (init_path:=DIR_PATH).exists() or (not init_path.is_dir() and init_path.exists()):
        init_path.mkdir(parents=True)
    if not (init_settings:=SETTINGS).exists() or (init_settings.exists() and not init_settings.is_file()):
        with open(SETTINGS, "w", encoding="utf-8") as f:
            f.writelines(["DIR_PATH|C:/ProgramData/MiniCounter\n", "CNT_FILE|Counter_1.cnt\n"])
    else:
        config = []
        with open(SETTINGS, "r", encoding="utf-8") as f:
            config = f.read().splitlines()
        if len(config) != 2 or not config[0].startswith("DIR_PATH|") or not config[1].startswith("CNT_FILE|"):
            with open(SETTINGS, "w", encoding="utf-8") as f:
                f.writelines(["DIR_PATH|C:/ProgramData/MiniCounter\n", "CNT_FILE|Counter_1.cnt\n"])
        else:
            DIR_PATH = Path(config[0][9:])
            if not (init_path:=DIR_PATH).exists() or (not init_path.is_dir() and init_path.exists()):
                init_path.mkdir(parents=True)
            CNT_FILE = config[1][9:]
    if not (cnt := DIR_PATH / CNT_FILE).exists() or (not cnt.is_file() and cnt.exists()):
        with open(cnt, "w", encoding="utf-8") as f:
            f.write("CNT|00000\n")
    else:
        with open(cnt, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) < 1 or not lines[0].startswith("CNT|"):
            with open(cnt, "w", encoding="utf-8") as f:
                f.write("CNT|00000\n")
        else:
            Count = int(lines[0][4:])
            History = [i.strip().split("|") for i in lines[1:]]
            HistoryText = lines[1:]


    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication([])
    w = Window()
    w.show()
    app.exec()