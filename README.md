# notter-grader
*It's not the otter-grader, it's yet anotter-grader!*

## Usage with Gradescope
To prepare an autograder.zip for an assignment:

1. Clone a copy of the repo:
```
git clone https://github.com/gandres42/notter-grader
```

2. Add any required files, e.g. datasets or helper function classes, into the files folder.  These behave the same as otter-grader, with files being moved into the workspace where submissions are graded.

3. Add tests into the tests folder.  These are the same as otter-grader, so refer to their docs for creation.

4. Set configuration options in the config.json.

5. Compress the files into autograder.zip, and it's ready to upload to gradescope.


## Configuration Options
notter-grader can be configured in config.json using the included flags:

`max_score`: The gradescope max score that tests will be normalized to.

`grade_restarted`: If True adds include an additional test to check if the notebook has been restarted and all cells run before submission, if False just grades tests.

`only_display_outputs`: If True the grader extracts images and formats them as HTML, then sets them as the Gradescope output.  If False, it outputs individual test results and total scores.


## Why notter?
Otter-grader already includes integration with Gradescope, but has a few limitations:
 - Non-configuable grader outputs, which makes manually grading long assignments tedious
 - Does not generate plot outputs when submissions are only partially run
 - Very heavyweight, requiring a hefty conda environment and taking a long time to build on Gradescope

Notter works to address these by essentially re-implementing otter-grader's run_grader function.  Notter is based on a uv environment and use nbformat to run custom checks/seperate out graph outputs.
