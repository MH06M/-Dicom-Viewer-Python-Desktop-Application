from PyQt5.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

class TagLoaderThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, tag_info):
        super().__init__()
        self.tag_info = tag_info
        self.chunk_size = 50

    def run(self):
        lines = self.tag_info.split('\n')
        for i in range(0, len(lines), self.chunk_size):
            chunk = '\n'.join(lines[i:i + self.chunk_size])
            self.progress.emit(chunk)
        self.finished.emit()

class TagViewerWindow(QMainWindow):
    def __init__(self, tag_info):
        super().__init__()
        self.tag_info = tag_info
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DICOM Tags')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        search_frame = QHBoxLayout()
        search_label = QLabel('Search Tag:')
        self.search_entry = QLineEdit()
        search_button = QPushButton('Search')
        next_button = QPushButton('Next')

        search_frame.addWidget(search_label)
        search_frame.addWidget(self.search_entry)
        search_frame.addWidget(search_button)
        search_frame.addWidget(next_button)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        layout.addLayout(search_frame)
        layout.addWidget(self.text_edit)

        search_button.clicked.connect(self.search)
        next_button.clicked.connect(self.find_next)
        self.search_entry.returnPressed.connect(self.search)

        self.loader_thread = TagLoaderThread(self.tag_info)
        self.loader_thread.progress.connect(self.append_text)
        self.loader_thread.finished.connect(self.loading_finished)
        self.loader_thread.start()

    def append_text(self, text):
        self.text_edit.append(text)

    def loading_finished(self):
        print("Tag loading completed")

    def search(self):
        search_term = self.search_entry.text().strip().lower()
        if not search_term:
            return

        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.Start)
        self.text_edit.setTextCursor(cursor)

        format = self.text_edit.currentCharFormat()
        format.setBackground(Qt.white)
        cursor.select(cursor.Document)
        cursor.mergeCharFormat(format)

        while self.text_edit.find(search_term):
            format = self.text_edit.currentCharFormat()
            format.setBackground(Qt.yellow)
            self.text_edit.mergeCurrentCharFormat(format)

    def find_next(self):
        search_term = self.search_entry.text().strip().lower()
        if not search_term:
            return
        
        self.text_edit.find(search_term)
