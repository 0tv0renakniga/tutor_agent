import os
import subprocess
import argparse

'''

this script can help with the following tasks

1. Convert class lectures/handouts to formated latex file and keyword/concept
   summary txt file
   note: summary txt file is desgned to be fed to prompt_eng.xml and genrate 
         new tutor prompt that is intended to help with hw and learning 
         course material
   input parts needed:
   - src_file: abs. path to pdf, ppt, doc, etc. (only tested pdf)
   - input_prompt: what xml prompt to update based on inputs (src_file,
     output_txt_dir, output_tex_dir)
   - output_txt_dir: path where keyword/concept txt file is saved
     - txt_filename: what to name the text file
   - output_tex_dir: path where src tex file is saved
     - tex_filename: what to name the text file

   generate the following based on inputs
   - gemini instructions: read and follow the prompt outlined in @{input_prompt}
     then follow instructions outlined in xml using @{src_file}
     ex: 
     gemini_inst = f"\"Please read and follow the prompt step by step in the 
         xml @{output_dir}/prompts/lec_to_tex.xml then follow the instructions 
         outlined in the xml using @{input_pdf}\""
   - updated prompt

'''
def parse_script_args():
    '''
    Initalize parser object and variable passed to script
    '''
    parser = argparse.ArgumentParser(
        description="Process a source document with Gemini to generate LaTeX and keyword summary files.",
        formatter_class=argparse.RawTextHelpFormatter # For better help formatting
    )

    parser.add_argument(
        "--src_file",
        type=str,
        required=True,
        help="Absolute path to the source document (e.g., PDF, PPT, DOC)."
    )
    parser.add_argument(
        "--prompt_path",
        type=str,
        required=True,
        help="Absolute path to the template XML prompt file containing instructions."
    )
    parser.add_argument(
        "--output_txt_dir",
        type=str,
        required=True,
        help="Path to the directory where the keyword/concept text file will be saved."
    )
    parser.add_argument(
        "--txt_filename",
        type=str,
        required=True,
        help="Name for the keyword/concept text file (e.g., 'my_keywords.txt')."
    )
    parser.add_argument(
        "--output_tex_dir",
        type=str,
        required=True,
        help="Path to the directory where the LaTeX (.tex) file will be saved."
    )
    parser.add_argument(
        "--tex_filename",
        type=str,
        required=True,
        help="Name for the LaTeX file (e.g., 'my_document.tex')."
    )
    parser.add_argument(
        "--task_type",
        type=str,
        required=True,
        help="Type of task (e.g., 'pdf2tex','generate_tutor','hw_help')."
    )

    args = parser.parse_args()

    inputs = {}
    inputs['src_file'] = args.src_file
    inputs['prompt_path'] = args.prompt_path
    inputs['txt_path'] = args.output_txt_dir
    inputs['txt_name'] = args.txt_filename
    inputs['tex_path'] = args.output_tex_dir
    inputs['tex_name'] = args.tex_filename
    inputs['task_type'] = args.task_type

    return inputs


def check_paths(inputs):
    '''
    takes inputs dict and creates output dirs if DNE
    '''
    for out_dir in [inputs['txt_path'], inputs['tex_path']]:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)


def update_metaprompt(inputs):
    '''
    read prompt template, make copy, and update paths in prompt copy
    '''
    # read xml metaprompt
    cmd = f"cat {inputs['prompt_path']}"
    xml_prompt = os.popen(cmd).read()
    
    # create copy of xml prompt and update prompt path to point at the copy
    new_xml_prompt = inputs['prompt_path'].replace('.xml', '_new.xml') 
    inputs['prompt_path'] = new_xml_prompt

    # check what strings to replace
    task_type_dict = {
        'pdf2tex': {
            'TXT_NAME': inputs['txt_name'],
            'TXT_PATH': inputs['txt_path'],
            'SRC_FILE': inputs['src_file'], 
            'TEX_NAME': inputs['tex_name'],
            'TEX_PATH': inputs['tex_path']
        },
        'generate_tutor': [],
        'hw_help': []
    }

    # replace filenames and paths in xml prompt
    for string in task_type_dict[inputs['task_type']].keys():
        xml_prompt = xml_prompt.replace(string, inputs[string.lower()])

    # write new prompt
    for i,j in enumerate(xml_prompt.split('\n')):
        if i == 0:
            cmd = f"echo \"{j}\" > {new_xml_prompt}"
            os.system(cmd)
        else:
            cmd = f"echo \"{j}\" >> {new_xml_prompt}"
            os.system(cmd)

    return inputs


def generate_gemini_cmd(prompt,src_file):
    '''
    generate instruction and cmd for gemini
    '''
    gemini_instruction = "\"Please follow the prompt step by step in the xml "
    gemini_instruction += f"@{prompt} then follow the instructions outlined "
    gemini_instruction += f"in the xml using @{src_file}\""

    gemini_cmd = f"gemini --yolo -p {gemini_instruction}"

    return gemini_cmd

def change_to_common_parent_dir(inputs):
    os.chdir('/home/scotty/')

def main():
    # parse args passed
    inputs = parse_script_args()

    # check paths exist
    check_paths(inputs)

    # update metaprompt
    inputs = update_metaprompt(inputs)

    # generate gemini cmd
    gemini_cmd = generate_gemini_cmd(inputs['prompt_path'], inputs['src_file'])

    # run gemini cmd
    print(gemini_cmd)
    change_to_common_parent_dir(inputs)
    subprocess.run(gemini_cmd, shell=True)

main()
