import tkinter as tk
from tkinter import ttk, filedialog
import requests
import os
import mimetypes

api_url = "https://canvas.instructure.com/api/v1"
access_token = "7~9qPhsR4RGA5xD4XvSlO1uR4QgUk4sN5AVbYU6GJjVyHLEKXoRFdmEEpfLcruikL9"

# Function to get all students for a given course ID
def get_students_in_role(course_id, role="student"):
    url = f"{api_url}/courses/{course_id}/users"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"enrollment_type": role}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        students = response.json()
        return students
    else:
        print(f"Error retrieving students. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None


def update_dropdowns(event):
    # Get the selected course name
    selected_course_name = course_var.get()

    # Update students
    update_students(selected_course_name)

    # Update assignments
    update_assignments(selected_course_name)


# Function to get all assignments for a given course ID
def get_all_assignments(course_id):
    url = f"{api_url}/courses/{course_id}/assignments"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        assignments = response.json()
        return assignments
    else:
        print(f"Error retrieving assignments. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None

# Function to upload feedback for a student in a specific assignmen


def upload_feedback(course_id, assignment_id, user_id, file_path):
    # Step 1: Notify Canvas about the file
    print(f"{api_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/files")
    notify_url = f"{api_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/files"
    notify_headers = {"Authorization": f"Bearer {access_token}"}

    # Get file size dynamically using os.path.getsize
    file_size = os.path.getsize(file_path)

    # Auto-detect file name and content type using os.path.splitext and mimetypes.guess_type
    file_name = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(file_name)

    notify_payload = {
        "name": file_name,  # Auto-detected file name
        "size": file_size,  # Dynamic file size
        "content_type": content_type or "application/octet-stream"  # Auto-detected content type or fallback
    }

    notify_response = requests.post(notify_url, headers=notify_headers, data=notify_payload)

    if notify_response.status_code != 200:
        print(f"Error notifying Canvas. Status code: {notify_response.status_code}")
        print(f"Response content: {notify_response.text}")
        return

    # Extract information from the notification response
    upload_url = notify_response.json().get("upload_url")
    upload_params = notify_response.json().get("upload_params")

    # Use the correct key for the file parameter
    file_param_key = upload_params.get("file_param", "file")
    
    # Step 2: Upload the file using the information from the first request
    with open(file_path, "rb") as file:
        files = {file_param_key: (file_name, file)}
        upload_response = requests.post(upload_url, files=files)

        if upload_response.status_code != 200:
            print(f"Error uploading file. Status code: {upload_response.status_code}")
            print(f"Response content: {upload_response.text}")
            return


    # Step 3: Follow the redirect to complete the upload
    completion_url = upload_response.json().get("completion_url")
    completion_response = requests.get(completion_url)

    if completion_response.status_code != 200:
        print(f"Error completing the upload. Status code: {completion_response.status_code}")
        print(f"Response content: {completion_response.text}")
        return

    print("File uploaded successfully for feedback")
# Create a map from course names to their numeric IDs
course_name_to_id = {}

# Populate course dropdown
url = f"{api_url}/courses"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    courses = response.json()
    for course in courses:
        course_name = course['name']
        course_id = course['id']
        course_name_to_id[course_name] = course_id

else:
    print(f"Error retrieving courses. Status code: {response.status_code}")

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
course_dropdown["values"] = list(course_name_to_id.keys())

# Event binding to update students and assignments when a course is selected
course_dropdown.bind("<<ComboboxSelected>>", update_dropdowns)

def update_dropdowns(event):
    # Get the selected course name
    selected_course_name = course_var.get()

    # Update students
    update_students(selected_course_name)

    # Update assignments
    update_assignments(selected_course_name)

def update_students(selected_course_name):
    # Get the course ID from the map
    selected_course_id = course_name_to_id.get(selected_course_name, None)

    if selected_course_id is not None:
        students = get_students_in_role(selected_course_id)
        if students:
            student_dropdown["values"] = [student["name"] for student in students]
            student_dropdown["state"] = "readonly"

def update_assignments(selected_course_name):
    # Get the course ID from the map
    selected_course_id = course_name_to_id.get(selected_course_name, None)

    if selected_course_id is not None:
        assignments = get_all_assignments(selected_course_id)
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

    # Get the corresponding course ID from the map
    course_id = course_name_to_id.get(course_name, None)

    # Perform the Canvas action with the numeric course ID
    if course_id is not None:
        # Call the necessary functions with course_id, student_name, assignment_name, and file_path
        students = get_students_in_role(course_id)
        selected_student = next((student for student in students if student["name"] == student_name), None)

        if selected_student:
            user_id = selected_student["id"]

            assignments = get_all_assignments(course_id)
            selected_assignment = next((assignment for assignment in assignments if assignment["name"] == assignment_name), None)

            if selected_assignment:
                assignment_id = selected_assignment["id"]
                upload_feedback(course_id, assignment_id, user_id, file_path)
            else:
                print(f"Error: Assignment '{assignment_name}' not found.")
        else:
            print(f"Error: Student '{student_name}' not found.")
    else:
        print(f"Error: Course '{course_name}' not found.")

# Run the main loop
root.mainloop()
