import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QColor
import pybithumb
import time

tickers = ["BTC", "ETH", "BCH", "ETC"]
form_class = uic.loadUiType("table.ui")[0]

class Worker(QThread):
    finished = pyqtSignal(dict)

    def run(self):
        while True:
            data = {}
            for ticker in tickers:
                data[ticker] = self.get_market_infos(ticker)
            self.finished.emit(data)
            time.sleep(2)

    def get_market_infos(self, ticker):
        try:
            df = pybithumb.get_ohlcv(ticker)
            ma5 = df['close'].rolling(window=5).mean()
            last_ma5 = ma5[-2]
            price = pybithumb.get_current_price(ticker)

            state = "상승장" if price > last_ma5 else "하락장"
            return price, last_ma5, state
        except:
            return None, None, None

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # QTableWidget 크기 자동 조정
        self.tableWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.worker = Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()

    @pyqtSlot(dict)
    def update_table_widget(self, data):
        for ticker, infos in data.items():
            index = tickers.index(ticker)
            self.tableWidget.setItem(index, 0, QTableWidgetItem(ticker))
            self.tableWidget.setItem(index, 1, QTableWidgetItem(str(infos[0])))
            self.tableWidget.setItem(index, 2, QTableWidgetItem(str(infos[1])))
            
            state_item = QTableWidgetItem(str(infos[2]))
            if infos[2] == "상승장":
                state_item.setForeground(QBrush(QColor("green")))
            elif infos[2] == "하락장":
                state_item.setForeground(QBrush(QColor("red")))
            self.tableWidget.setItem(index, 3, state_item)

app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()