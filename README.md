# Flask Task Manager




##  Features

* Create, list, update, and filter tasks
* Search tasks by title or description
* Filter tasks by status
* Sort tasks by date fields
* Safe parameterized SQL queries


##  Project Structure

```text
project-root/
│
├── app.py                # Main Flask application
├── database.db           # SQLite database
├── templates/
│   └── tasks.html        # HTML template for tasks page
├── static/               # CSS
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

---



###  Clone the Repository

```bash
git clone https://github.com/asrar000/https://github.com/asrar000/simple_task_manager.git
cd flask-task-manager
```

---

###  Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\\Scripts\\activate      # Windows
```

---

###  Install Dependencies

```bash
pip install -r requirements.txt
```

---

###  Run the Application

```bash
flask run
```

or

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000/tasks
```

---

##  Web Routes (HTML Pages)

### `/tasks`

* Displays all tasks
* Supports filtering by status

Example:

```
/tasks
/tasks?status=done
```

---

### `/tasks/done/<task_id>`

* Marks a task as `done`
* Redirects back to `/tasks`

Example:

```
/tasks/done/3
```

---

##  API Routes (JSON)

### `GET /api/tasks`

List tasks with optional filters.

**Query Parameters:**

* `status` → filter by status
* `q` → search in title or description
* `sort` → `due_date` or `created_at`

Example:

```
/api/tasks?status=done&q=meeting&sort=due_date
```

---

### `PUT /api/tasks/<task_id>`

Update task fields.

**Request Body (JSON):**

```json
{
  "title": "Finish report",
  "status": "in_progress"
}
```

**Responses:**

* `200` → task updated
* `400` → invalid input
* `404` → task not found

---

##  Github Link

GitHub: [https://github.com/asrar000](https://github.com/asrar000)

---

