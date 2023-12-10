import requests
import os
import mimetypes

class Canvas:
    def __init__(self, api_url, access_token):
        self.api_url = api_url
        self.access_token = access_token

    def get(self, url, params=None, headers=None):
        full_url = f"{self.api_url}/{url}"
        headers = headers or {}
        headers["Authorization"] = f"Bearer {self.access_token}"

        response = requests.get(full_url, params=params, headers=headers)

        if response.status_code == 200:
            return response
        else:
            print(f"Error in GET request. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return None

    def get_all_courses(self):
        url = f"{self.api_url}/courses"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            courses = response.json()
            return courses
        else:
            print(f"Error retrieving courses. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return None
    
    def get_all_assignments(self, course_id):
        url = f"{self.api_url}/courses/{course_id}/assignments"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            assignments = response.json()
            return assignments
        else:
            print(f"Error retrieving assignments. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return None

    def get_students_in_role(self, course_id, role="student"):
        url = f"{self.api_url}/courses/{course_id}/users"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"enrollment_type": role}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            students = response.json()
            return students
        else:
            print(f"Error retrieving students. Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return None

    def notify_canvas(self, course_id, assignment_id, user_id, file_path):
        notify_url = f"{self.api_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}/comments/files"
        notify_headers = {"Authorization": f"Bearer {self.access_token}"}

        # Get file size dynamically using os.path.getsize
        file_size = os.path.getsize(file_path)

        # Auto-detect file name and content type using os.path.splitext and mimetypes.guess_type
        file_name = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_name)

        notify_payload = {
            "name": file_name,
            "size": file_size,
            "content_type": content_type or "application/octet-stream"
        }

        notify_response = requests.post(notify_url, headers=notify_headers, data=notify_payload)

        if notify_response.status_code != 200:
            print(f"Error notifying Canvas. Status code: {notify_response.status_code}")
            print(f"Response content: {notify_response.text}")
            return None

        # Extract information from the notification response
        upload_url = notify_response.json().get("upload_url")
        upload_params = notify_response.json().get("upload_params")

        # Use the correct key for the file parameter
        file_param_key = upload_params.get("file_param", "file")

        return upload_url, file_param_key

    def upload_file(self, upload_url, file_param_key, file_path):
        with open(file_path, "rb") as file:
            files = {file_param_key: (os.path.basename(file_path), file)}
            upload_response = requests.post(upload_url, files=files)
            file_id = upload_response.json().get("id")

            if upload_response.status_code != 201:
                print(f"Error uploading file. Status code: {upload_response.status_code}")
                print(f"Response content: {upload_response.text}")
                return None

        return file_id

    def complete_upload(self, completion_url):
        completion_response = requests.get(completion_url, headers={"Authorization": f"Bearer {self.access_token}"})

        if completion_response.status_code == 200:
            return True
        else:
            print(f"Error completing upload. Status code: {completion_response.status_code}")
            print(f"Response content: {completion_response.text}")
            return False

    def update_submission(self, course_id, assignment_id, user_id, file_ids):
        submission_url = f"{self.api_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"
        payload = {
            "submission_type": "online_upload",
            "comment": {
                "file_ids": [file_ids],
                # Add any other necessary fields
            }
        }

        put_response = requests.put(submission_url, headers={"Authorization": f"Bearer {self.access_token}"}, json=payload)

        if put_response.status_code == 200:
            print("Submission updated successfully")
        else:
            print(f"Error updating submission. Status code: {put_response.status_code}")
            print(f"Response content: {put_response.text}")

    def upload_feedback(self, course_id, assignment_id, user_id, file_path):
        try:
            # Step 1: Notify Canvas about the file
            upload_url, file_param_key = self.notify_canvas(course_id, assignment_id, user_id, file_path)

            if upload_url is None:
                return

            # Step 2: Upload the file using the information from the first request
            file_id = self.upload_file(upload_url, file_param_key, file_path)

            if file_id is None:
                return
           
            # Step 4: Update the submission with the uploaded file
            self.update_submission(course_id, assignment_id, user_id, file_id)
       

        except Exception as e:
            print(f"An error occurred: {str(e)}")
