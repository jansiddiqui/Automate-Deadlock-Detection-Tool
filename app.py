from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

def detect_deadlock(dependencies):
    graph = {}
    for process, resource in dependencies:
        graph.setdefault(process, set()).add(resource)
        graph.setdefault(resource, set())

    visited = set()
    rec_stack = set()
    path = []

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                path.append(neighbor)
                return True

        rec_stack.remove(node)
        path.pop()
        return False

    for node in graph:
        if node not in visited:
            if has_cycle(node):
                # Extract cycle from path
                cycle_start = path.index(path[-1])
                cycle_path = path[cycle_start:]
                return True, cycle_path

    return False, []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect_deadlock", methods=["POST"])
def check_deadlock():
    data = request.get_json()
    dependencies = data.get("dependencies", [])
    is_deadlock, cycle_path = detect_deadlock(dependencies)
    if is_deadlock:
        return jsonify({"message": "⚠️ Deadlock Detected!", "deadlockPath": cycle_path})
    else:
        return jsonify({"message": "✅ No Deadlock Detected.", "deadlockPath": []})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
