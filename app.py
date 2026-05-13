"""Flask web application for EDIFACT file viewer."""

import os
from flask import Flask, render_template, request, jsonify
from edifact_parser import parse_edifact

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/parse", methods=["POST"])
def parse():
    if "file" not in request.files and "text" not in request.form:
        return jsonify({"error": "Keine Datei oder Text übermittelt"}), 400

    try:
        if "file" in request.files and request.files["file"].filename:
            file = request.files["file"]
            content = file.read().decode("utf-8", errors="replace")
        else:
            content = request.form.get("text", "")

        if not content.strip():
            return jsonify({"error": "Leerer Inhalt"}), 400

        result = parse_edifact(content)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Fehler beim Parsen: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
