import sys
import io
import folium
import plotly.express as px
import pandas as pd
import ephem
import tempfile
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QProgressDialog, QDialog, QVBoxLayout, QDateTimeEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from datetime import datetime, timedelta


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LEO Satellite Pass Checker')
        self.window_width, self.window_height = 1200, 900
        self.setMinimumSize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        file_layout = QHBoxLayout()
        layout.addLayout(file_layout)

        file_label_1 = QLabel("TLE File:")
        self.file_input_1 = QLineEdit()
        file_layout.addWidget(file_label_1)
        file_layout.addWidget(self.file_input_1)
        file_button_1 = QPushButton("Browse")
        file_layout.addWidget(file_button_1)
        file_button_1.clicked.connect(self.read_tle)

        file_label_2 = QLabel("GST:")
        self.file_input_2 = QLineEdit()
        file_layout.addWidget(file_label_2)
        file_layout.addWidget(self.file_input_2)
        file_button_2 = QPushButton("Browse")
        file_layout.addWidget(file_button_2)
        file_button_2.clicked.connect(self.read_gst)

        datetime_layout = QHBoxLayout()
        layout.addLayout(datetime_layout)

        start_label = QLabel("Start Datetime:")
        self.start_datetime_edit = QDateTimeEdit()
        self.start_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_datetime_edit.setDateTime(datetime(2020, 1, 1, 0, 0, 0))
        datetime_layout.addWidget(start_label)
        datetime_layout.addWidget(self.start_datetime_edit)

        end_label = QLabel("End Datetime:")
        self.end_datetime_edit = QDateTimeEdit()
        self.end_datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_datetime_edit.setDateTime(datetime(2020, 1, 1, 23, 59, 59))
        datetime_layout.addWidget(end_label)
        datetime_layout.addWidget(self.end_datetime_edit)

        # Computation Button
        self.compute_button = QPushButton("Compute")
        self.compute_button.setEnabled(False)  # Disable initially
        layout.addWidget(self.compute_button)
        self.compute_button.clicked.connect(self.start_computation)
        
        # Plot Gantt Button
        self.gantt_button = QPushButton("Plot")
        self.gantt_button.setEnabled(False)  # Disable initially
        layout.addWidget(self.gantt_button)
        self.gantt_button.clicked.connect(self.plot_gantt)

        # Map
        coordinate = (51.4934, 0.0098)
        self.map = folium.Map(location=coordinate, zoom_start=3)

        # Save map data to data object
        data = io.BytesIO()
        self.map.save(data, close_file=False)

        self.webView = QWebEngineView()
        self.webView.setHtml(data.getvalue().decode())
        layout.addWidget(self.webView)


    def start_computation(self):
        self.progress_dialog = QProgressDialog("Computing...", "Close", 0, 100)
        self.progress_dialog.setWindowTitle("Progress")
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.show()
        self.progress_dialog.setValue(0)  # Reset progress

        start_datetime = self.start_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_datetime = self.end_datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        date_format = "%Y-%m-%d %H:%M:%S"
        start_datetime = datetime.strptime(start_datetime, date_format)
        end_datetime = datetime.strptime(end_datetime, date_format)

        entries = []

        for _ in range(len(self.gst_coordinates)):
            entry = {"Start Time": 0, "End Time": 0}
            entries.append(entry)

        # Create the dataframe from the list of entries
        df = pd.DataFrame(entries)

        # Perform your computation here using start_datetime and end_datetime
        total = 86400 * len(self.gst_coordinates)
        current = 0
        gantt_list = []


        for i in range(len(self.gst_coordinates)):
            current_datetime = start_datetime
            observer = ephem.Observer()
            observer.lat = str(self.gst_coordinates[i][0])
            observer.lon = str(self.gst_coordinates[i][1])
            observer.elevation = self.gst_coordinates[i][2]

            last_active = None
            
            while current_datetime < end_datetime:
                current += 1
                progress = int((current / total) * 100)
                self.progress_dialog.setValue(progress)
                self.progress_dialog.setLabelText(f"Computing... {progress}%")
                QApplication.processEvents()
                    
                observer.date = current_datetime
                sat_count = len(self.tles)
                for j in range(sat_count):
                    satellite = ephem.readtle(
                        self.tles[j][0], self.tles[j][1], self.tles[j][2]
                    )
                    satellite.compute(observer)
                    los_distance_km = satellite.range / 1000.0

                    if los_distance_km < 1000:
                        if last_active is None:
                            last_active = current_datetime
                        break
                    else:
                        if last_active is not None and (j == sat_count - 1):
                            # active_ranges.append((last_active, current_datetime))
                            gantt_list.append(
                                dict(Task=self.tles[j][0], Start=last_active, Finish=current_datetime, Resource=str(self.gst_coordinates[i][3]))
                            )
                            last_active = None
                current_datetime += timedelta(seconds=1)
                
        print(len(gantt_list))
        self.gantt_df = pd.DataFrame(gantt_list)
        self.gantt_button.setEnabled(True)
        self.progress_dialog.setLabelText("Computation Complete")

    def plot_gantt(self):
        print(self.gantt_df.columns)
        fig = px.timeline(self.gantt_df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
        fig.update_xaxes(tickformat="%Y-%m-%d %H:%M:%S")

        # Save plot as HTML file in a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            plot_filename = f"{temp_dir}/plot.html"
            fig.write_html(plot_filename)

            plot_dialog = QDialog(self)
            plot_dialog.setWindowTitle("Computation Result")
            plot_dialog.resize(400, 300)
            plot_layout = QVBoxLayout(plot_dialog)
            plot_view = QWebEngineView(plot_dialog)
            plot_layout.addWidget(plot_view)

            # Load and display the plot in the dialog
            plot_view.setUrl(QtCore.QUrl.fromLocalFile(plot_filename))
            plot_dialog.exec_()

    def read_tle(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select TLE File")
        self.file_input_1.setText(file_name)
        with open(file_name, "r") as tle_file:
            self.tle_lines = tle_file.readlines()
        self.tles = []

        for i in range(0, len(self.tle_lines), 3):
            line1 = (self.tle_lines[i].strip())[2:]
            line2 = self.tle_lines[i + 1].strip()
            line3 = self.tle_lines[i + 2].strip()

            self.tles.append((line1, line2, line3))
        self.enable_compute_button()

    def read_gst(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select GST File")
        self.file_input_2.setText(file_name)
        self.plot_coordinates(file_name)
        self.enable_compute_button()

    def enable_compute_button(self):
        if self.file_input_1.text() and self.file_input_2.text():
            self.compute_button.setEnabled(True)
        else:
            self.compute_button.setEnabled(False)

    def plot_coordinates(self, file_path):
        self.map = folium.Map(location=[51.4934, 0.0098], zoom_start=3)
        self.gst_coordinates = []
        with open(file_path, 'r') as file:
            for line in file:
                coordinates = line.strip().split(',')
                if len(coordinates) == 3:
                    latitude, longitude, elevation, label = coordinates[0], coordinates[1], float(coordinates[2]), coordinates[3]
                    folium.Marker([float(latitude), float(longitude)], popup=label).add_to(self.map)
                    self.gst_coordinates.append([latitude, longitude, elevation, label])

        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.webView.setHtml(data.getvalue().decode())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
