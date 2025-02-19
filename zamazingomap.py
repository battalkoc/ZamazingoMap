import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QTabWidget, QTextEdit,
    QLabel, QSplitter, QListWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import nmap


class NmapWorker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, target, profile):
        super().__init__()
        self.target = target
        self.profile = profile

    def run(self):
        nm = nmap.PortScanner()
        try:
            # Komut belirleme
            if self.profile == "Intense scan":
                scan_args = "-T4 -A -v"
            elif self.profile == "Intense scan plus UDP":
                scan_args = "-sS -sU -T4 -A -v"
            elif self.profile == "Intense scan, all TCP ports":
                scan_args = "-p 1-65535 -T4 -A -v"
            elif self.profile == "Intense scan, no ping":
                scan_args = "-T4 -A -v -Pn"
            elif self.profile == "Ping scan":
                scan_args = "-sn"
            elif self.profile == "Quick scan":
                scan_args = "-T4 -F"
            elif self.profile == "Quick scan plus":
                scan_args = "-T4 -A -v -F"
            elif self.profile == "Quick traceroute":
                scan_args = "--traceroute"
            elif self.profile == "Regular scan":
                scan_args = ""
            elif self.profile == "Slow comprehensive scan":
                scan_args = "-sS -sU -T1 -A -v -PE -PP -PY -g 53"
            else:
                scan_args = ""


            result = nm.scan(hosts=self.target, arguments=scan_args)
            self.result_signal.emit(str(result))
        except Exception as e:
            self.result_signal.emit(f"Error: {str(e)}")


class ZenmapClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zamazingo Map")
        self.setGeometry(200, 200, 1024, 768)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()
        self.tema()

    def setup_ui(self):

        top_bar = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter target IP or hostname")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems([
            "Intense scan",
            "Intense scan plus UDP",
            "Intense scan, all TCP ports",
            "Intense scan, no ping",
            "Ping scan",
            "Quick scan",
            "Quick scan plus",
            "Quick traceroute",
            "Regular scan",
            "Slow comprehensive scan"
        ])

        self.command_display = QLineEdit()
        self.command_display.setReadOnly(True)
        self.command_display.setPlaceholderText("Command will appear here")
        self.scan_button = QPushButton("Scan")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)

        top_bar.addWidget(QLabel("Target:"))
        top_bar.addWidget(self.target_input)
        top_bar.addWidget(QLabel("Profile:"))
        top_bar.addWidget(self.profile_combo)
        top_bar.addWidget(self.scan_button)
        top_bar.addWidget(self.cancel_button)


        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Command:"))
        command_layout.addWidget(self.command_display)


        splitter = QSplitter(Qt.Horizontal)


        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        self.hosts_list = QListWidget()
        self.services_list = QListWidget()
        self.filter_button = QPushButton("Filter Hosts")
        self.filter_button.clicked.connect(self.filter_hosts)
        left_layout.addWidget(QLabel("Hosts"))
        left_layout.addWidget(self.hosts_list)
        left_layout.addWidget(QLabel("Services"))
        left_layout.addWidget(self.services_list)
        left_layout.addWidget(self.filter_button)
        splitter.addWidget(self.left_panel)


        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)


        self.tabs = QTabWidget()
        self.output_tab = QTextEdit()
        self.output_tab.setReadOnly(True)
        self.tabs.addTab(self.output_tab, "Nmap Output")
        self.tabs.addTab(QTextEdit(), "Ports/Hosts")
        self.tabs.addTab(QTextEdit(), "Topology")
        self.tabs.addTab(QTextEdit(), "Host Details")
        self.tabs.addTab(QTextEdit(), "Scans")


        details_layout = QHBoxLayout()
        self.details_button = QPushButton("Details")
        details_layout.addStretch()
        details_layout.addWidget(self.details_button)

        right_layout.addWidget(self.tabs)
        right_layout.addLayout(details_layout)
        splitter.addWidget(self.right_panel)

        splitter.setStretchFactor(1, 3)


        self.layout.addLayout(top_bar)
        self.layout.addLayout(command_layout)
        self.layout.addWidget(splitter)


        self.scan_button.clicked.connect(self.start_scan)
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.profile_combo.currentTextChanged.connect(self.update_command)

    def update_command(self):
        profile = self.profile_combo.currentText()
        if profile == "Intense scan":
            command = "nmap -T4 -A -v"
        elif profile == "Intense scan plus UDP":
            command = "nmap -sS -sU -T4 -A -v"
        elif profile == "Intense scan, all TCP ports":
            command = "nmap -p 1-65535 -T4 -A -v"
        elif profile == "Intense scan, no ping":
            command = "nmap -T4 -A -v -Pn"
        elif profile == "Ping scan":
            command = "nmap -sn"
        elif profile == "Quick scan":
            command = "nmap -T4 -F"
        elif profile == "Quick scan plus":
            command = "nmap -T4 -A -v -F"
        elif profile == "Quick traceroute":
            command = "nmap --traceroute"
        elif profile == "Regular scan":
            command = "nmap"
        elif profile == "Slow comprehensive scan":
            command = "nmap -sS -sU -T1 -A -v -PE -PP -PY -g 53"
        else:
            command = "nmap"


        self.command_display.setText(command)

    def start_scan(self):
        target = self.target_input.text().strip()
        profile = self.profile_combo.currentText()

        if not target:
            self.output_tab.append("Please enter a target!")
            return


        self.update_command()
        command = self.command_display.text()

        self.scan_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.output_tab.append(f"Scanning {target} with profile {profile}...")


        self.worker = NmapWorker(target, profile)
        self.worker.result_signal.connect(self.display_result)
        self.worker.start()

    def cancel_scan(self):
        if self.worker.isRunning():
            self.worker.terminate()
            self.output_tab.append("Scan canceled.")
            self.scan_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def display_result(self, result):
        formatted_result = self.format_scan_result(result)
        self.output_tab.append(formatted_result)
        self.populate_ports_hosts(result)
        self.populate_topology(result)
        self.populate_host_details(result)
        self.populate_scans(result)
        self.populate_hosts(result)
        self.populate_services(result)
        self.scan_result_data = eval(result)
        self.scan_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def format_scan_result(self,result):
        try:
            nmap_data = eval(result)
            scan_info = nmap_data.get('nmap', {})
            scan_stats = scan_info.get('scanstats', {})
            scanned_hosts = nmap_data.get('scan', {})


            formatted_result = f"Nmap Command: {scan_info.get('command_line')}\n"
            formatted_result += f"Time: {scan_stats.get('timestr')}\n"
            formatted_result += f"Elapsed Time: {scan_stats.get('elapsed')} seconds\n"
            formatted_result += f"Hosts Up: {scan_stats.get('uphosts')}\n"
            formatted_result += f"Hosts Down: {scan_stats.get('downhosts')}\n\n"


            for host, data in scanned_hosts.items():
                formatted_result += f"Host: {host}\n"
                formatted_result += f"  Hostnames: {', '.join([h['name'] for h in data.get('hostnames', [])])}\n"
                formatted_result += f"  State: {data.get('status', {}).get('state')}\n"
                formatted_result += f"  Reason: {data.get('status', {}).get('reason')}\n"
                formatted_result += f"  Open Ports:\n"

                for port, port_data in data.get('tcp', {}).items():
                    if port_data['state'] == 'open':
                        formatted_result += (
                            f"    - Port {port}: {port_data['name']} "
                            f"({port_data.get('product', '')} {port_data.get('version', '')})\n"
                        )
                formatted_result += "\n"

            return formatted_result

        except Exception as e:
            return f"Error formatting result: {str(e)}"

    def populate_ports_hosts(self, result):
        try:
            nmap_data = eval(result)
            scanned_hosts = nmap_data.get('scan', {})
            content = ""

            for host, data in scanned_hosts.items():
                content += f"Host: {host}\n"
                for port, port_data in data.get('tcp', {}).items():
                    content += f"  - Port {port}: {port_data['name']} (State: {port_data['state']})\n"

            self.tabs.widget(1).setPlainText(content)
        except Exception as e:
            self.tabs.widget(1).setPlainText(f"Error: {str(e)}")

    def populate_topology(self, result):
        try:
            nmap_data = eval(result)
            scanned_hosts = nmap_data.get('scan', {})
            content = "Topology Information:\n\n"

            for host, data in scanned_hosts.items():
                content += f"Host: {host}\n"
                content += f"  State: {data.get('status', {}).get('state')}\n"
                content += f"  Reason: {data.get('status', {}).get('reason')}\n"
                content += f"  Hostnames: {', '.join([h['name'] for h in data.get('hostnames', [])])}\n\n"

            self.tabs.widget(2).setPlainText(content)
        except Exception as e:
            self.tabs.widget(2).setPlainText(f"Error: {str(e)}")

    def populate_host_details(self, result):
        try:
            nmap_data = eval(result)
            scanned_hosts = nmap_data.get('scan', {})
            content = "Host Details:\n\n"

            for host, data in scanned_hosts.items():
                content += f"Host: {host}\n"
                content += f"  IP Address: {data.get('addresses', {}).get('ipv4', 'N/A')}\n"
                content += f"  Vendor: {data.get('vendor', {}).get(data.get('addresses', {}).get('mac', ''), 'N/A')}\n"
                content += f"  State: {data.get('status', {}).get('state')}\n"
                content += f"  Reason: {data.get('status', {}).get('reason')}\n"
                content += "\n"

            self.tabs.widget(3).setPlainText(content)
        except Exception as e:
            self.tabs.widget(3).setPlainText(f"Error: {str(e)}")

    def populate_scans(self, result):
        try:
            nmap_data = eval(result)
            scan_info = nmap_data.get('nmap', {})
            scan_stats = scan_info.get('scanstats', {})
            content = "Scan Information:\n\n"

            content += f"Command Line: {scan_info.get('command_line')}\n"
            content += f"Start Time: {scan_stats.get('timestr')}\n"
            content += f"Elapsed Time: {scan_stats.get('elapsed')} seconds\n"
            content += f"Hosts Up: {scan_stats.get('uphosts')}\n"
            content += f"Hosts Down: {scan_stats.get('downhosts')}\n"
            content += f"Total Hosts: {scan_stats.get('totalhosts')}\n"

            self.tabs.widget(4).setPlainText(content)
        except Exception as e:
            self.tabs.widget(4).setPlainText(f"Error: {str(e)}")

    def populate_hosts(self, result):
        try:
            nmap_data = eval(result)
            scanned_hosts = nmap_data.get('scan', {})

            self.hosts_list.clear()

            for host, data in scanned_hosts.items():
                status = data.get('status', {}).get('state', 'unknown')
                self.hosts_list.addItem(f"{host} ({status})")
        except Exception as e:
            self.hosts_list.addItem(f"Error: {str(e)}")

    def populate_services(self, result):
        try:
            nmap_data = eval(result)
            scanned_hosts = nmap_data.get('scan', {})

            self.services_list.clear()

            for host, data in scanned_hosts.items():
                for port, port_data in data.get('tcp', {}).items():
                    if port_data['state'] == 'open':
                        self.services_list.addItem(
                            f"Host: {host}, Port: {port}, Service: {port_data['name']}"
                        )
        except Exception as e:
            self.services_list.addItem(f"Error: {str(e)}")

    def filter_hosts(self):
        try:
            filter_text = self.target_input.text().strip()
            nmap_data = self.scan_result_data
            scanned_hosts = nmap_data.get('scan', {})

            self.hosts_list.clear()

            for host, data in scanned_hosts.items():
                status = data.get('status', {}).get('state', 'unknown')


                if (status == "up" and filter_text in host) or (filter_text in host):
                    self.hosts_list.addItem(f"{host} ({status})")
        except Exception as e:
            self.hosts_list.addItem(f"Error: {str(e)}")

    def tema(self):
        dark_mor_stylesheet = """
        QMainWindow {
            background-color: #2D2D30;
            color: #FFFFFF;
        }

        QWidget {
            background-color: #2D2D30;
            color: #FFFFFF;
            font-size: 14px;
        }

        QLineEdit {
            background-color: #3C3C3C;
            color: #FFFFFF;
            border: 1px solid #6A0DAD;
            padding: 5px;
            border-radius: 5px;
        }

        QPushButton {
            background-color: #6A0DAD;
            color: #FFFFFF;
            border: none;
            padding: 8px;
            border-radius: 5px;
        }

        QPushButton:hover {
            background-color: #7E3DAF;
        }

        QPushButton:disabled {
            background-color: #4B4B4B;
            color: #A0A0A0;
        }

        QComboBox {
            background-color: #3C3C3C;
            color: #FFFFFF;
            border: 1px solid #6A0DAD;
            padding: 5px;
            border-radius: 5px;
        }

        QComboBox QAbstractItemView {
            background-color: #3C3C3C;
            color: #FFFFFF;
            selection-background-color: #6A0DAD;
        }

        QLabel {
            color: #FFFFFF;
        }

        QTabWidget::pane {
            background-color: #3C3C3C;
            border: 1px solid #6A0DAD;
            border-radius: 5px;
        }

        QTabBar::tab {
            background-color: #3C3C3C;
            color: #FFFFFF;
            border: 1px solid #6A0DAD;
            padding: 10px;
            border-radius: 5px;
        }

        QTabBar::tab:selected {
            background-color: #6A0DAD;
            color: #FFFFFF;
        }

        QTabBar::tab:hover {
            background-color: #7E3DAF;
        }

        QTextEdit {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #6A0DAD;
            padding: 5px;
            border-radius: 5px;
        }

        QListWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #6A0DAD;
            padding: 5px;
            border-radius: 5px;
        }

        QSplitter::handle {
            background-color: #6A0DAD;
        }

        QSplitter::handle:hover {
            background-color: #7E3DAF;
        }

        QScrollBar:vertical, QScrollBar:horizontal {
            background-color: #3C3C3C;
            border: none;
            width: 10px;
            margin: 0px;
        }

        QScrollBar::handle {
            background-color: #6A0DAD;
            border-radius: 5px;
        }

        QScrollBar::handle:hover {
            background-color: #7E3DAF;
        }

        QScrollBar::add-line, QScrollBar::sub-line {
            background: none;
        }
        """
        self.setStyleSheet(dark_mor_stylesheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZenmapClone()
    window.show()
    sys.exit(app.exec_())
