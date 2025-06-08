import tkinter as tk
from tkinter import messagebox, simpledialog
from task_mgmt import Task, TaskManager, Level
from datetime import datetime, timedelta

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.manager = TaskManager()

        # Current user
        self.current_user = simpledialog.askstring("Login", "Enter your username:")

        # GUI Elements
        self.text_area = tk.Text(root, width=100, height=25)
        self.text_area.pack()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="List Tasks", command=self.list_tasks).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Refresh Due Tasks", command=self.refresh_due).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Rescue by Tag", command=self.rescue_task).grid(row=0, column=3, padx=5)

    def add_task(self):
        title = simpledialog.askstring("Title", "Task Title:")
        if not title:
            return

        description = simpledialog.askstring("Description", "Task Description:")
        impact = simpledialog.askstring("Impact", "Impact (High/Low):", initialvalue="High")
        effort = simpledialog.askstring("Effort", "Effort (High/Low):", initialvalue="Low")
        tags = simpledialog.askstring("Tags", "Comma-separated tags:")
        owner = simpledialog.askstring("Owner", "Delegate to (username):", initialvalue=self.current_user)

        deadline_str = simpledialog.askstring("Deadline", "Deadline (YYYY-MM-DD) or leave blank:")
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date as YYYY-MM-DD.")
                return

        task = Task(
            title=title,
            description=description or "",
            impact=Level(impact.capitalize()),
            effort=Level(effort.capitalize()),
            tags=[t.strip() for t in tags.split(",")] if tags else [],
            user=self.current_user,
            owner=owner or self.current_user,
            deadline=deadline
        )

        self.manager.add_task(task)
        self.manager.save()
        messagebox.showinfo("Added", f"Task '{title}' added.")
        self.list_tasks()

    def list_tasks(self):
        self.text_area.delete("1.0", tk.END)
        for name, queue in self.manager.queues.items():
            visible = [t for t in queue.tasks if t.user == self.current_user]
            if visible:
                self.text_area.insert(tk.END, f"=== {name} ===\n")
                for task in visible:
                    self.text_area.insert(tk.END, f"- {task.title} [{task.status}%] | Owner: {task.owner}\n")
                    self.text_area.insert(tk.END, f"  Tags: {', '.join(task.tags)} | Due: {task.deadline}\n")
                self.text_area.insert(tk.END, "\n")

    def refresh_due(self):
        try:
            self.manager.refresh_due_tasks(self.current_user)
            self.manager.save()
            messagebox.showinfo("Refreshed", "Due tasks checked and moved if needed.")
            self.list_tasks()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def rescue_task(self):
        tag = simpledialog.askstring("Rescue", "Enter tag to rescue from 'Someday or Never':")
        if tag:
            self.manager.rescue_task_from_someday(tag_match=tag, user=self.current_user)
            self.manager.save()
            self.list_tasks()

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()