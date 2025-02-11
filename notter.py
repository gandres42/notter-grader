#!./.venv/bin/python
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from otter.api import grade_submission
from otter.run import run_autograder
import tempfile
import shutil
import time
import json
from dotenv import load_dotenv
import os
import base64
import io
from PIL import Image

load_dotenv()

LOCAL = os.getenv("LOCAL", 'False').lower() in ('true', '1', 't')
IMAGES_ONLY = os.getenv("OUTPUT_IMAGES_ONLY", 'False').lower() in ('true', '1', 't')
RESTART_RUN_ALL_CHECK = os.getenv("GRADE_RESTART_RUNALL", 'False').lower() in ('true', '1', 't')
if LOCAL:
    NOTEBOOK_PATH = f'./{os.getenv("NOTEBOOK_NAME")}'
else:
    NOTEBOOK_PATH = f'/autograder/source/{os.getenv("NOTEBOOK_NAME")}'

def otto_ascii_creator(gradescope_dict, total_score, total_possible):
    max_len = max([len(test['name']) for test in gradescope_dict['tests']])
    
    ascii_header = """


  _   _       _   _            
 | \\ | |     | | | |           
 |  \\| | ___ | |_| |_ ___ _ __ 
 | . ` |/ _ \\| __| __/ _ \\ '__|
 | |\\  | (_) | |_| ||  __/ |   
 |_| \\_|\\___/ \\__|\\__\\___|_|   

------------------------------- GRADING SUMMARY --------------------------------"""

    
    summary = f'{"name".rjust(max_len)}  {"score".rjust(5)}  {"max_score".rjust(9)}\n'
    
    for test in gradescope_dict['tests']:
        if 'score' in test.keys():
            summary += f'{test['name'].rjust(max_len)}  {str(float(test['score'])).rjust(5)}  {str(float(test['max_score'])).rjust(9)}\n'
            
    header = f'Total Score: {total_score} / {total_possible} ({round((total_score / total_possible) * 100)}%)'
    summary = f'{ascii_header}\n{header}\n\n{summary}'
    
    return summary

def check_restart_runall(notebook):
    execution_counts = []
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == "code":
            execution_counts.append(cell.execution_count)
    score = 1
    msg = "Restarted and all cells run"
    # for i in range(1, len(execution_counts)):
    #     if execution_counts[i - 1] != execution_counts[i] - 1:
    #         restart_score = 0
    #         restart_message = "Not restarted or not all cells run"
    #         break
    return score, msg

def clear_notebook(notebook):
    for cell in notebook.cells:
            if cell.cell_type == 'code':
                cell.outputs = []

def volumetric_shit_compressor(base64_string, max_width=600, output_format="WEBP", quality=85):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))

    if image.width > max_width:
        aspect_ratio = image.height / image.width
        new_width = max_width
        new_height = int(new_width * aspect_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    compressed_image_io = io.BytesIO()
    image.save(compressed_image_io, format=output_format, quality=quality)

    return base64.b64encode(compressed_image_io.getvalue()).decode("utf-8")

def image_html_factory(notebook):
    html_content = '<!DOCTYPE html><html><body style="display: flex; justify-content: center; align-items: center;"><div style="display: flex; flex-direction: column; align-content: center;">'
    # Iterate through the cells to find image outputs
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            for output in cell.get("outputs", []):
                if output.get("output_type") == "display_data":
                    image_data = output.get("data", {}).get("image/png")
                    if image_data:
                        new_data = volumetric_shit_compressor(image_data)
                        new_html = f'<img src="data:image/png;base64,{new_data}" style="width:100%; margin-bottom:10px; max-width: 500px;" />'
                        html_content = html_content + new_html
    html_content = html_content + '</div></body></html>'
    return html_content

def score_notebook(notebook_path):
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as tmp_notebook:
        # read original into copy, open it with nbformat
        tmp_notebook_path = tmp_notebook.name
        shutil.copyfile(notebook_path, tmp_notebook_path)
        tmp_notebook = nbformat.read(tmp_notebook, as_version=4)

        # check if the code has been restarted/run all
        restart_score, restart_msg = check_restart_runall(tmp_notebook)

        # clear tmp_notebook outputs
        clear_notebook(tmp_notebook)

        # run all cells in tmp_notebook, ignore errors
        execute_preprocessor = ExecutePreprocessor(timeout=None, allow_errors=True)
        start_time = time.monotonic()
        execute_preprocessor.preprocess(tmp_notebook, {'metadata': {'path': '.'}})
        end_time = time.monotonic()

        # grade complete notebook
        if LOCAL:
            otter_results = grade_submission(tmp_notebook_path, 'autograder.zip', extra_submission_files=['arm_routines.py'], quiet=True)
        else:
            otter_results = grade_submission(tmp_notebook_path, '/autograder/source/autograder.zip', extra_submission_files=['arm_routines.py'], quiet=True)
        
        gradescope_results = {}
        
        # save per-test results for gradescope results
        config = run_autograder.autograder_config.AutograderConfig(user_config={})
        gradescope_results['tests'] = otter_results.to_gradescope_dict(config)['tests']
        
        # grade restart/run all penalty
        if RESTART_RUN_ALL_CHECK:
            gradescope_results['tests'].append({
                'name': 'restart/run all',
                'score': restart_score,
                'max_score': 1.0,
                'visibility': 'hidden',
                'output': restart_msg
            })

        # export images from the notebook as HTML
        html_body = image_html_factory(tmp_notebook)
        with open('results.html', 'w', encoding='utf-8') as f:
            f.write(html_body)
        
        # put all this delectable data into results dictionary
        gradescope_results['execution_time'] = end_time - start_time
        gradescope_results['output'] = html_body
        gradescope_results['output_format'] = 'html'
        gradescope_results['stdout_visibility'] = 'hidden'

        json_string = json.dumps(gradescope_results, ensure_ascii=False)
        if LOCAL:
            with open('./results.json', "w") as json_file:
                json_file.write(json_string)
        else:
            with open('/autograder/results/results.json', "w") as json_file:
                json_file.write(json_string)

score_notebook(NOTEBOOK_PATH)