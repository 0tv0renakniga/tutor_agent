#!/bin/bash

# This script executes the Python tutor_agent.py script with predefined arguments.

# --- Configuration Variables ---
# Absolute path to your Python script
PYTHON_SCRIPT="/home/scotty/tutor_agent/src/tutor_agent.py"

# Input file (PDF, PPT, DOC, etc. - currently tested with PDF)
SRC_FILE="/home/scotty/dsc_257/cse_examples/lectures/lec3.pdf"

# XML prompt file to update based on inputs
PROMPT_PATH="/home/scotty/school_workflow_v2/prompts/lec_to_tex.xml"

# Directory where keyword/concept text file will be saved
OUTPUT_TXT_DIR="/home/scotty/school_workflow_v2/latex_keywords/"
# Name for the keyword/concept text file
TXT_FILENAME="dsc_257_lec3_shell_test.txt"

# Directory where source LaTeX (.tex) file will be saved
OUTPUT_TEX_DIR="/home/scotty/school_workflow_v2/latex_lectures/"
# Name for the LaTeX file
TEX_FILENAME="dsc_257_lec3_shell_test.tex"

# Type of task for the agent
TASK_TYPE="pdf2tex"

# --- Execution ---
echo "Starting Tutor Agent script..."
echo "Source File: $SRC_FILE"
echo "Prompt Path: $PROMPT_PATH"
echo "Output Text Directory: $OUTPUT_TXT_DIR"
echo "Text Filename: $TXT_FILENAME"
echo "Output LaTeX Directory: $OUTPUT_TEX_DIR"
echo "LaTeX Filename: $TEX_FILENAME"
echo "Task Type: $TASK_TYPE"
echo "----------------------------------------"

# Execute the Python script with all arguments
python3 "$PYTHON_SCRIPT" \
    --src_file "$SRC_FILE" \
    --prompt_path "$PROMPT_PATH" \
    --output_txt_dir "$OUTPUT_TXT_DIR" \
    --txt_filename "$TXT_FILENAME" \
    --output_tex_dir "$OUTPUT_TEX_DIR" \
    --tex_filename "$TEX_FILENAME" \
    --task_type "$TASK_TYPE"

# Check the exit status of the Python script
if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo "Tutor Agent script completed successfully!"
else
    echo "----------------------------------------"
    echo "Tutor Agent script"
