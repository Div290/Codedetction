import os
import logging
import json
from flask import Flask, request, jsonify, render_template
from detect_code import CodeAnalyzer

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Initialize code analyzer
code_analyzer = CodeAnalyzer()

ALLOWED_EXTENSIONS = {'txt', 'py', 'js', 'java', 'cpp', 'c', 'cs', 'php', 'html', 'css', 'sql', 'ipynb'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_code_from_notebook(notebook_content):
    try:
        logger.debug("Starting notebook processing")
        nb = json.loads(notebook_content)
        code_cells = []
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                logger.debug(f"Found code cell with source type: {type(source)}")
                if isinstance(source, list):
                    code_cells.extend(source)
                else:
                    code_cells.append(source)

        extracted_code = '\n'.join(code_cells)
        logger.debug(f"Extracted code length: {len(extracted_code)}")
        return extracted_code
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse notebook JSON: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing notebook: {str(e)}")
        raise

def analyze_code(code_content):
    try:
        logger.debug("Starting code analysis")
        result = code_analyzer.analyze(code_content)
        return result
    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}")
        return {
            "probability": 50,
            "reasoning": f"Error analyzing code: {str(e)}"
        }

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        # Read file content
        file_content = file.read().decode('utf-8')
        logger.debug(f"Processing file: {file.filename}")

        # Check if file is empty
        if not file_content:
            return jsonify({"error": "File is empty"}), 400

        # If it's a Jupyter notebook, extract the code
        if file.filename.endswith('.ipynb'):
            try:
                logger.debug("Processing Jupyter notebook")
                file_content = extract_code_from_notebook(file_content)
                if not file_content.strip():
                    return jsonify({"error": "No code cells found in notebook"}), 400
                logger.debug("Successfully extracted code from notebook")
            except Exception as e:
                logger.error(f"Error processing notebook: {str(e)}")
                return jsonify({"error": "Invalid notebook format"}), 400

        # Analyze the code
        result = analyze_code(file_content)

        if not result:
            return jsonify({"error": "Failed to analyze code"}), 500

        return jsonify({
            "success": True,
            "ai_generated_probability": result["probability"],
            "reasoning": result["reasoning"],
            "filename": file.filename
        })

    except UnicodeDecodeError:
        return jsonify({"error": "File must be a text file"}), 400
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)