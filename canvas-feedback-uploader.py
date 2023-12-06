import tkinter as tk
from tkinter import ttk, filedialog
from canvasapi import Canvas  # Assuming you save your Canvas class in a file called canvas_class.py

api_url = "https://canvas.instructure.com/api/v1"   # Insert your own URL
access_token = "7~JbNRv3p9H0Rr0FxYS4Mt9cQUdfZhvxAz0izZBsB2ULa50CHbN4gMkDJ0MIKIuPOv"  # Use your own Token

def update_dropdowns(event):
    # Get the selected course name
    selected_course_name = course_var.get()

    # Update students
    update_students(selected_course_name)

    # Update assignments
    update_assignments(selected_course_name)

def update_students(selected_course_name):
    # Get the course ID from the list of courses
    selected_course = next((course for course in courses if course['name'] == selected_course_name), None)

    if selected_course is not None:
        selected_course_id = selected_course['id']
        students = canvas_instance.get_students_in_role(selected_course_id)

        if students:
            student_dropdown["values"] = [student["name"] for student in students]
            student_dropdown["state"] = "readonly"


def update_assignments(selected_course_name):
    # Get the course ID from the list of courses
    selected_course = next((course for course in courses if course['name'] == selected_course_name), None)

    if selected_course is not None:
        selected_course_id = selected_course['id']
        assignments = canvas_instance.get_all_assignments(selected_course_id)

        if assignments:
            assignment_dropdown["values"] = [assignment["name"] for assignment in assignments]
            assignment_dropdown["state"] = "readonly"

def browse_file(file_path_entry):
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)

def perform_canvas_action(course_var, student_var, assignment_var, file_path_entry):
    course_name = course_var.get()
    student_name = student_var.get()
    assignment_name = assignment_var.get()
    file_path = file_path_entry.get()

    # Get the corresponding course from the list of courses
    selected_course = next((course for course in courses if course['name'] == course_name), None)

    # Perform the Canvas action with the selected course
    if selected_course is not None:
        # Get the necessary information from the selected course
        course_id = selected_course['id']
        students = canvas_instance.get_students_in_role(course_id)
        selected_student = next((student for student in students if student["name"] == student_name), None)

        if selected_student:
            user_id = selected_student["id"]

            assignments = canvas_instance.get_all_assignments(course_id)
            selected_assignment = next((assignment for assignment in assignments if assignment["name"] == assignment_name), None)

            if selected_assignment:
                assignment_id = selected_assignment["id"]
                canvas_instance.upload_feedback(course_id, assignment_id, user_id, file_path)
            else:
                print(f"Error: Assignment '{assignment_name}' not found.")
        else:
            print(f"Error: Student '{student_name}' not found.")
    else:
        print(f"Error: Course '{course_name}' not found.")


# Create a Canvas instance
canvas_instance = Canvas(api_url, access_token)

# Create the main application window
root = tk.Tk()
root.title("Canvas API Support")

# Variables for dropdown selections
course_var = tk.StringVar()
student_var = tk.StringVar()
assignment_var = tk.StringVar()

# GUI widgets
course_label = tk.Label(root, text="Course:")
course_dropdown = ttk.Combobox(root, textvariable=course_var, state="readonly")
student_label = tk.Label(root, text="Student:")
student_dropdown = ttk.Combobox(root, textvariable=student_var, state="disabled")
assignment_label = tk.Label(root, text="Assignment:")
assignment_dropdown = ttk.Combobox(root, textvariable=assignment_var, state="disabled")
file_path_label = tk.Label(root, text="File Path:")
file_path_entry = tk.Entry(root, width=50)
browse_button = tk.Button(root, text="Browse", command=lambda: browse_file(file_path_entry))
action_button = tk.Button(root, text="Perform Canvas Action", command=lambda: perform_canvas_action(course_var, student_var, assignment_var, file_path_entry))

# Arrange widgets
course_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
course_dropdown.grid(row=0, column=1, padx=10, pady=10)
student_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
student_dropdown.grid(row=1, column=1, padx=10, pady=10)
assignment_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
assignment_dropdown.grid(row=2, column=1, padx=10, pady=10)
file_path_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
file_path_entry.grid(row=3, column=1, padx=10, pady=10)
browse_button.grid(row=3, column=2, padx=10, pady=10)
action_button.grid(row=4, column=0, columnspan=3, pady=20)

# Populate course dropdown with course names
courses = canvas_instance.get_all_courses()
course_dropdown["values"] = [course['name'] for course in courses]

# Event binding to update students and assignments when a course is selected
course_dropdown.bind("<<ComboboxSelected>>", update_dropdowns)

# Run the main loop
root.mainloop()
