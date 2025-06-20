import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/api/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get("code", "")
    test_cases = data.get("testCases", [])

    results = []

    for i, test_case in enumerate(test_cases):
        js_code = f"{code}\nconsole.log({test_case['input']});"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w") as temp_file:
            temp_file.write(js_code)
            temp_file_path = temp_file.name

        try:
            output = subprocess.check_output(["node", temp_file_path], stderr=subprocess.STDOUT, text=True)
            expected = test_case["expected"]
            normalized_output = output.replace(" ", "").strip()
            normalized_expected = expected.replace(" ", "").strip()
            status = "✅ Passed" if normalized_output == normalized_expected else f"❌ Failed - Expected {expected} but got {output}"
        except subprocess.CalledProcessError as e:
            status = f"❌ Error - {e.output.strip()}"

        results.append({
            "testCase": i + 1,
            "status": status
        })

        os.unlink(temp_file_path)  # Clean up temp file

    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
