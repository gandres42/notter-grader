#!./.venv/bin/python
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from otter.api import grade_submission
from otter.run import run_autograder
import tempfile
import shutil
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

IMAGES_ONLY = os.getenv("OUTPUT_IMAGES_ONLY", 'False').lower() in ('true', '1', 't')
RESTART_RUN_ALL_CHECK = os.getenv("GRADE_RESTART_RUNALL", 'False').lower() in ('true', '1', 't')
# NOTEBOOK_PATH = f'/autograder/source/{os.getenv("NOTEBOOK_NAME")}'
NOTEBOOK_PATH = f'./{os.getenv("NOTEBOOK_NAME")}'

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

def unindent_notebook(notebook):
    for cell in notebook.cells:
        if cell.cell_type == 'markdown':
            lines = cell.source.splitlines()
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    # Count the number of `#` characters to determine the header level
                    header_level = line.count('#')
                    if header_level < 6:  # If header is not already at the smallest level
                        # Reduce the header level by one
                        new_line = '#' * (header_level + 1) + line.lstrip('#')
                        lines[i] = new_line
            # Join the modified lines back together
            cell.source = '\n'.join(lines)

def score_notebook(notebook_path):
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as tmp_notebook:
        # read original into copy, open it with nbformat
        tmp_notebook_path = tmp_notebook.name
        shutil.copyfile(notebook_path, tmp_notebook_path)
        tmp_notebook = nbformat.read(tmp_notebook, as_version=4)

        # check if the code has been restarted/run all
        restart_score, restart_msg = check_restart_runall(tmp_notebook)

        # clear tmp_notebook outputs and lower header weights by one
        clear_notebook(tmp_notebook)
        unindent_notebook(tmp_notebook)

        # run all cells in tmp_notebook, ignore errors
        execute_preprocessor = ExecutePreprocessor(timeout=None, allow_errors=True)
        start_time = time.monotonic()
        execute_preprocessor.preprocess(tmp_notebook, {'metadata': {'path': '.'}})
        end_time = time.monotonic()

        # grade complete notebook
        # otter_results = grade_submission(tmp_notebook_path, '/autograder/source/autograder.zip', extra_submission_files=['arm_routines.py'], quiet=True)
        otter_results = grade_submission(tmp_notebook_path, 'autograder.zip', extra_submission_files=['arm_routines.py'], quiet=False)
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
        
        # filter out only images
        if IMAGES_ONLY:
            filtered_cells = []
            for i, cell in enumerate(tmp_notebook.cells):
                # only keep images and the relevant titles
                if cell.cell_type == "code":
                    has_image = any(
                        output.get("output_type") == "display_data" and "image/png" in output.get("data", {})
                        for output in cell.get("outputs", []))
                    if has_image: filtered_cells.append(cell)
                else:
                    filtered_cells.append(cell)
            tmp_notebook.cells = filtered_cells
            
        
        # format top-level results and append to top of notebook
        grader_title_cell = nbformat.v4.new_markdown_cell("# Submission Score")
        grader_output_cell = nbformat.v4.new_code_cell(otto_ascii_creator(gradescope_results, otter_results.total, otter_results.possible))
        notebook_divider_cell = nbformat.v4.new_markdown_cell("# Submission Output")
        tmp_notebook.cells.insert(0, notebook_divider_cell)
        tmp_notebook.cells.insert(0, grader_output_cell)
        tmp_notebook.cells.insert(0, grader_title_cell)

        # export the notebook as HTML
        html_exporter = HTMLExporter()
        html_body, _ = html_exporter.from_notebook_node(tmp_notebook)

        html_file_path = notebook_path.replace('.ipynb', '.html')
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_body)
        
        # put all this delectable data into results dictionary
        gradescope_results['execution_time'] = end_time - start_time
        gradescope_results['output'] = html_body
        gradescope_results['output_format'] = 'html'
        gradescope_results['stdout_visibility'] = 'hidden'
        # with open('/autograder/results/results.json', "w") as json_file:
        with open('./results.json', "w") as json_file:
            json.dump(gradescope_results, json_file)

score_notebook(NOTEBOOK_PATH)