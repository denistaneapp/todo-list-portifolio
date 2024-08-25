from flask import Flask, jsonify, request, render_template, make_response
import csv
import io
from translations import translations  # Import translations from translations.py / translations.pyから翻訳をインポートします

app = Flask(__name__)

# List to store tasks / タスクを保存するリスト
tasks = []

# List to store categories / カテゴリを保存するリスト
categories = []

@app.route('/')
def index():
    # Get the language code from the URL, default to English / URLから言語コードを取得し、デフォルトは英語
    lang_code = request.args.get('lang', 'en')
    # Render the index.html template with the selected language translations / 選択した言語の翻訳でindex.htmlテンプレートをレンダリング
    return render_template('index.html', translations=translations[lang_code])

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    priority_filter = request.args.get('priority', None)

    # Filter tasks based on priority if provided / 優先度に基づいてタスクをフィルタリング（もし指定されている場合）
    filtered_tasks = tasks
    if priority_filter:
        filtered_tasks = [task for task in tasks if task['priority'] == priority_filter]

    start = (page - 1) * limit
    end = start + limit
    paginated_tasks = filtered_tasks[start:end]
    total_pages = (len(filtered_tasks) + limit - 1) // limit  # Calculate the total number of pages / ページの総数を計算
    return jsonify({
        'tasks': paginated_tasks,
        'total_pages': total_pages
    })

@app.route('/api/tasks', methods=['POST'])
def add_task():
    task = request.json
    task['id'] = len(tasks) + 1
    task['priority'] = task.get('priority', 'Média')  # Default priority is 'Média' / デフォルトの優先度は「Média」
    task['completed'] = False  # New task starts as incomplete / 新しいタスクは未完了として開始

    # Add category to the list if it doesn't exist / カテゴリが存在しない場合はリストに追加
    if task['category'] not in categories:
        categories.append(task['category'])

    tasks.append(task)
    # Sort tasks by priority / 優先度でタスクを並び替え
    tasks.sort(key=lambda x: {'Alta': 1, 'Média': 2, 'Baixa': 3}[x['priority']])
    return jsonify(task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = request.json
    for t in tasks:
        if t['id'] == task_id:
            # Update the task with new values / 新しい値でタスクを更新
            t.update({
                'text': task.get('text', t['text']),
                'category': task.get('category', t['category']),
                'priority': task.get('priority', t['priority']),
                'date': task.get('date', t['date']),
                'completed': task.get('completed', t['completed'])
            })
            return jsonify(t), 200
    return jsonify({'error': 'Task not found'}), 404  # Return 404 if task not found / タスクが見つからない場合は404を返す

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    for t in tasks:
        if t['id'] == task_id:
            t['completed'] = True  # Mark task as completed / タスクを完了済みとしてマーク
            return jsonify(t), 200
    return jsonify({'error': 'Task not found'}), 404  # Return 404 if task not found / タスクが見つからない場合は404を返す

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]  # Remove task by ID / IDでタスクを削除
    return '', 204  # Return no content status / コンテンツなしステータスを返す

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(categories)  # Return the list of categories / カテゴリのリストを返す

@app.route('/api/export', methods=['GET'])
def export_tasks():
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Text', 'Category', 'Priority', 'Date', 'Completed'])
    for task in tasks:
        cw.writerow([task['id'], task['text'], task['category'], task['priority'], task['date'], task['completed']])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=tasks.csv"
    output.headers["Content-type"] = "text/csv"
    return output  # Return the CSV file for download / ダウンロード用のCSVファイルを返す

@app.route('/api/stats', methods=['GET'])
def get_stats():
    completed_tasks = len([task for task in tasks if task['completed']])
    pending_tasks = len([task for task in tasks if not task['completed']])
    return jsonify({
        'completed_tasks': completed_tasks,  # Number of completed tasks / 完了したタスクの数
        'pending_tasks': pending_tasks  # Number of pending tasks / 保留中のタスクの数
    })

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode / デバッグモードでFlaskアプリケーションを実行する
