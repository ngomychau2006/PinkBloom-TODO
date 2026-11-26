from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from pathlib import Path
from datetime import datetime, date, timedelta

app = Flask(__name__)
app.secret_key = "pinkbloom-todo-local-secret"
DB_PATH = Path(__file__).with_name("todo.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'Cá nhân',
            priority TEXT DEFAULT 'Trung bình',
            status TEXT DEFAULT 'Chưa bắt đầu',
            due_date TEXT DEFAULT '',
            important INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def fetch_tasks(search="", status="", category="", priority=""):
    conn = get_db()
    sql = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if search:
        sql += " AND (title LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if status:
        sql += " AND status=?"
        params.append(status)
    if category:
        sql += " AND category=?"
        params.append(category)
    if priority:
        sql += " AND priority=?"
        params.append(priority)
    sql += """ ORDER BY important DESC,
        CASE priority WHEN 'Cao' THEN 1 WHEN 'Trung bình' THEN 2 ELSE 3 END,
        CASE WHEN due_date='' THEN 1 ELSE 0 END, due_date ASC, id DESC"""
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def build_context(page):
    conn = get_db()
    all_tasks = [dict(row) for row in conn.execute("SELECT * FROM tasks").fetchall()]
    conn.close()

    total = len(all_tasks)
    completed = sum(t["status"] == "Hoàn thành" for t in all_tasks)
    in_progress = sum(t["status"] == "Đang thực hiện" for t in all_tasks)
    pending = sum(t["status"] == "Chưa bắt đầu" for t in all_tasks)
    today = date.today()
    today_str = today.isoformat()
    three_days_later = (today + timedelta(days=3)).isoformat()
    overdue = sum(bool(t["due_date"]) and t["due_date"] < today_str and t["status"] != "Hoàn thành" for t in all_tasks)
    due_soon = sum(bool(t["due_date"]) and today_str <= t["due_date"] <= three_days_later and t["status"] != "Hoàn thành" for t in all_tasks)
    rate = round(completed / total * 100) if total else 0
    categories = ["Cá nhân", "Học tập", "Công việc", "Sức khỏe", "Khác"]
    priorities = ["Cao", "Trung bình", "Thấp"]
    category_counts = {c: sum(t["category"] == c for t in all_tasks) for c in categories}
    priority_counts = {p: sum(t["priority"] == p for t in all_tasks) for p in priorities}
    stats = {"total": total, "completed": completed, "in_progress": in_progress,
             "pending": pending, "overdue": overdue, "due_soon": due_soon, "rate": rate}

    search = request.args.get("q", "").strip() if page == "tasks" else ""
    status = request.args.get("status", "") if page == "tasks" else ""
    category = request.args.get("category", "") if page == "tasks" else ""
    priority = request.args.get("priority", "") if page == "tasks" else ""
    tasks = fetch_tasks(search, status, category, priority) if page == "tasks" else []

    return dict(page=page, page_title={"overview":"Tổng quan", "tasks":"Công việc của tôi", "statistics":"Thống kê"}[page],
                tasks=tasks, stats=stats, categories=categories, category_counts=category_counts,
                priorities=priorities, priority_counts=priority_counts,
                filters={"q":search,"status":status,"category":category,"priority":priority}, today=today_str,
                all_tasks=all_tasks)


@app.route("/")
def index():
    return render_template("index.html", **build_context("overview"))


@app.route("/tasks")
def tasks_page():
    return render_template("index.html", **build_context("tasks"))


@app.route("/statistics")
def statistics_page():
    return render_template("index.html", **build_context("statistics"))


@app.route("/task", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Vui lòng nhập tên công việc.", "error")
        return redirect(url_for("tasks_page"))
    conn = get_db()
    conn.execute("""INSERT INTO tasks(title, description, category, priority, status, due_date, important, created_at)
                    VALUES(?,?,?,?,?,?,?,?)""",
                 (title, request.form.get("description", "").strip(),
                  request.form.get("category", "Cá nhân"), request.form.get("priority", "Trung bình"),
                  request.form.get("status", "Chưa bắt đầu"), request.form.get("due_date", ""),
                  1 if request.form.get("important") else 0, datetime.now().isoformat(timespec="minutes")))
    conn.commit()
    conn.close()
    flash("Đã thêm công việc mới ✨", "success")
    return redirect(url_for("tasks_page"))


@app.route("/task/<int:task_id>/edit", methods=["POST"])
def edit_task(task_id):
    title = request.form.get("title", "").strip()
    if not title:
        flash("Tên công việc không được để trống.", "error")
        return redirect(url_for("tasks_page"))
    conn = get_db()
    conn.execute("""UPDATE tasks SET title=?, description=?, category=?, priority=?, status=?, due_date=?, important=?
                    WHERE id=?""",
                 (title, request.form.get("description", "").strip(), request.form.get("category", "Cá nhân"),
                  request.form.get("priority", "Trung bình"), request.form.get("status", "Chưa bắt đầu"),
                  request.form.get("due_date", ""), 1 if request.form.get("important") else 0, task_id))
    conn.commit()
    conn.close()
    flash("Đã cập nhật công việc.", "success")
    return redirect(url_for("tasks_page"))


@app.route("/task/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    flash("Đã xóa công việc.", "success")
    return redirect(url_for("tasks_page"))


@app.route("/task/<int:task_id>/status", methods=["POST"])
def update_status(task_id):
    new_status = request.form.get("status")
    if new_status not in ["Chưa bắt đầu", "Đang thực hiện", "Hoàn thành"]:
        return jsonify({"ok": False, "message": "Trạng thái không hợp lệ"}), 400
    conn = get_db()
    conn.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/task/<int:task_id>/important", methods=["POST"])
def toggle_important(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET important = CASE important WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (task_id,))
    conn.commit()
    row = conn.execute("SELECT important FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return jsonify({"ok": True, "important": row["important"] if row else 0})


if __name__ == "__main__":
    conn = get_db()
    conn.close()
    app.run(debug=True)
