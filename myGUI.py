from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton, QFileDialog, QLineEdit
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtCore import QFileInfo
from canvasapi import Canvas
import requests
import sys
import os

class CanvasGUI(QWidget):
    def __init__(self, api_url, access_token):
        super().__init__()

        self.canvas_instance = Canvas(api_url, access_token)
        self.course_name_to_id = {}
        self.selected_course_id = None
      

        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout()

        # Course dropdown
        self.course_dropdown = QComboBox()
        self.populate_courses()
        self.course_dropdown.currentIndexChanged.connect(self.update_students_and_assignments)
        layout.addWidget(QLabel("Course:"))
        layout.addWidget(self.course_dropdown)

        # Assignment dropdown
        self.assignment_dropdown = QComboBox()
        self.assignment_dropdown.setEnabled(False)
        layout.addWidget(QLabel("Assignment:"))
        layout.addWidget(self.assignment_dropdown)

        # Student dropdown
        self.student_dropdown = QComboBox()
        self.student_dropdown.setEnabled(False)
        layout.addWidget(QLabel("Student:"))
        layout.addWidget(self.student_dropdown)

        # Drop area using QListWidget
        self.drop_area = QListWidget()
        self.drop_area.setAcceptDrops(True)
        self.drop_area.setMinimumHeight(100) # Set the minimum height (adjust as needed)
        self.drop_area.setSelectionMode(QAbstractItemView.MultiSelection)  # Allow multiple items to be selected
        self.drop_area.itemDoubleClicked.connect(self.remove_selected_item)
        self.drop_area.keyPressEvent = self.keyPressEvent  # Override keyPressEventS
        layout.addWidget(QLabel("Drop Files Here:"))
        layout.addWidget(self.drop_area)
        

        # Browse button
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        layout.addWidget(browse_button)

        # Perform Canvas Action button
        action_button = QPushButton("Upload Feedback")
        action_button.clicked.connect(self.perform_canvas_action)
        layout.addWidget(action_button)

        self.setLayout(layout)

        # Enable drag and drop for the entire widget
        self.setAcceptDrops(True)

        script_path = os.path.abspath(__file__)

        # Get the directory of the script
        script_directory = os.path.dirname(script_path)

        # Set window icon using the icon file in the same directory
        icon_path = os.path.join(script_directory, 'icon.png')
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)

        self.setGeometry(500, 200, 400, 450)
        self.setWindowTitle('Canvas Feedback Tool')
        self.show()

    def remove_selected_files(self):
        for item in self.drop_area.selectedItems():
            self.drop_area.takeItem(self.drop_area.row(item))

    def dropEvent(self, event):
        mime_data = event.mimeData()

        for url in mime_data.urls():
            file_path = url.toLocalFile()
            if file_path:
                # Check if the path points to a file
                if os.path.isfile(file_path):
                    # Extract the filename from the full path
        
                    item = QListWidgetItem(file_path)
                    self.drop_area.addItem(item)

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            event.acceptProposedAction()

    def remove_selected_item(self, item):
        self.drop_area.takeItem(self.drop_area.row(item))

    
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.perform_canvas_action()

        if event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            for item in self.drop_area.selectedItems():
                row = self.drop_area.row(item)
                self.drop_area.takeItem(row)

    def populate_courses(self):
        courses = self.canvas_instance.get_all_courses()

        if courses:
            # Clear existing items
            self.course_dropdown.clear()

            # Add default item
            self.course_dropdown.addItem("Select a Course")

            for course in courses:
                course_name = course['name']
                course_id = course['id']
                self.course_name_to_id[course_name] = course_id
                self.course_dropdown.addItem(course_name)

            
    def update_students_and_assignments(self):
        self.selected_course_id = self.course_name_to_id.get(self.course_dropdown.currentText())

        if self.selected_course_id:
            students = self.canvas_instance.get_students_in_role(self.selected_course_id)

            if students:
                self.student_dropdown.clear()
               

                for student in students:
                    self.student_dropdown.addItem(student["name"])
                self.student_dropdown.setEnabled(True)

            assignments = self.canvas_instance.get_all_assignments(self.selected_course_id)

            if assignments:
                self.assignment_dropdown.clear()
                self.assignment_dropdown.addItems([assignment["name"] for assignment in assignments])
                self.assignment_dropdown.setEnabled(True)

    def browse_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Open Files", "", "All Files (*);;Text Files (*.txt)")
        # Display the filenames in the drag and drop box
        self.add_files_to_drop_area(file_paths)

    def add_files_to_drop_area(self, file_names):
        # Add the filenames to the drag and drop box
        self.drop_area.addItems(file_names)
    
    def clear_drop_area(self):
        self.drop_area.clear()


    def perform_canvas_action(self):
        course_name = self.course_dropdown.currentText()
        student_name = self.student_dropdown.currentText()
        assignment_name = self.assignment_dropdown.currentText()
        file_paths = [self.drop_area.item(i).text() for i in range(self.drop_area.count())]

        if not file_paths:
            print("Error: File path is empty.")
            return


        if self.selected_course_id:
            students = self.canvas_instance.get_students_in_role(self.selected_course_id)
            selected_student = next((student for student in students if student["name"] == student_name), None)

            if selected_student:
                user_id = selected_student["id"]

                assignments = self.canvas_instance.get_all_assignments(self.selected_course_id)
                selected_assignment = next((assignment for assignment in assignments if assignment["name"] == assignment_name), None)

                if selected_assignment:
                    assignment_id = selected_assignment["id"]
                    self.canvas_instance.upload_feedback_batch(self.selected_course_id, assignment_id, user_id, file_paths)
                else:
                    print(f"Error: Assignment '{assignment_name}' not found.")
            else:
                print(f"Error: Student '{student_name}' not found.")
        else:
            print(f"Error: Course '{course_name}' not found.")

        self.clear_drop_area()
