import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from otter.api import grade_submission
from otter.run import run_autograder
import tempfile
import shutil

def otto_ascii_creator(gradescope_dict, total_score, total_possible):
    max_len = max([len(test['name']) for test in gradescope_dict['tests']])
    
    ascii_header = """
   ____    _     _           
  / __ \\  | |   | |          
 | |  | | | |_  | |_    ___  
 | |  | | | __| | __|  / _ \\ 
 | |__| | | |_  | |_  | (_) |
  \\____/   \\__|  \\__|  \\___/ 

------------------------------- GRADING SUMMARY --------------------------------"""

    
    summary = f'{"name".rjust(max_len)}  {"score".rjust(5)}  {"max_score".rjust(9)}\n'
    
    for test in gradescope_dict['tests']:
        if 'score' in test.keys():
            summary += f'{test['name'].rjust(max_len)}  {str(float(test['score'])).rjust(5)}  {str(float(test['max_score'])).rjust(9)}\n'
            
    header = f'Total Score: {total_score} / {total_possible} ({round((total_score / total_possible) * 100)}%)'
    summary = f'{ascii_header}\n{header}\n\n{summary}'
    
    return summary
    
def score_notebook(notebook_path):
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as tmp_notebook:
        # read original into copy, open it with nbformat
        tmp_notebook_path = tmp_notebook.name
        shutil.copyfile(notebook_path, tmp_notebook_path)
        tmp_notebook = nbformat.read(tmp_notebook, as_version=4)

        # clear tmp_notebook outputs and lower header weights
        for cell in tmp_notebook.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
            elif cell.cell_type == 'markdown':
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

        # run all cells in tmp_notebook, ignore errors
        execute_preprocessor = ExecutePreprocessor(timeout=None, allow_errors=True)
        execute_preprocessor.preprocess(tmp_notebook, {'metadata': {'path': '.'}})

        # grade complete notebook
        otter_results = grade_submission(tmp_notebook_path, 'autograder.zip', extra_submission_files=['arm_routines.py'], quiet=True)
        gradescope_results = {}
        
        # save per-test results for gradescope results
        config = run_autograder.autograder_config.AutograderConfig(user_config={})
        gradescope_results['tests'] = otter_results.to_gradescope_dict(config)['tests']
        
        
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
        gradescope_results['output'] = html_body
        gradescope_results['output_format'] = 'html'
        gradescope_results['stdout_visibility'] = 'hidden'
        
# Provide the path to your notebook
notebook_path = 'HW_3_robot_arm.ipynb'
score_notebook(notebook_path)