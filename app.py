from flask import Flask, render_template, request, jsonify
from collections import defaultdict

app = Flask(__name__)

def detect_deadlock(dependencies):
    # Convert list of dependencies into an adjacency list (graph)
    graph = {}
    for process, resource in dependencies:
        if process not in graph:
            graph[process] = set()
        if resource not in graph:
            graph[resource] = set()
        graph[process].add(resource)
    
    # Helper function for cycle detection using DFS
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False

    # Detect cycles
    visited = set()
    rec_stack = set()
    
    for node in graph:
        if node not in visited:
            if has_cycle(node, visited, rec_stack):
                return True  # Deadlock detected

    return False  # No deadlock detected

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect_deadlock", methods=["POST"])

def check_deadlock():
    data = request.get_json()
    dependencies = data.get("dependencies", [])
    print(dependencies)  # Debugging statement to check the structure
    if detect_deadlock(dependencies):
        return jsonify({"message": "⚠️ Deadlock Detected!"})
    else:
        return jsonify({"message": "✅ No Deadlock Detected."})

if __name__ == "__main__":
    app.run(debug=True)
