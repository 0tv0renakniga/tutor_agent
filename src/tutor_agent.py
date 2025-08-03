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

    #gemini_cmd = f"gemini --yolo -p {gemini_instruction}"
    gemini_cmd = f"gemini '-y -m gemini-2.5-flash {gemini_instruction}'"
    return gemini_cmd


def pdf_to_txt(pdf_file):
    '''
    when 2.5 model limit reached you need to create txt file from pdf

    need:
      - pymupdf and tesseract(ocr functionality)
      - setup venv for this project since extra libs needed
        - add requirments.txt for pip
        - add shell script to create venv and activate
      - determine when ocr needed vs regular text extraction
    '''
    doc = fitz.open(pdf_file)
    full_text = []

    print(f"Processing PDF file: {os.path.basename(pdf_path)}...")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
            
        # First, try to extract text directly from the PDF page
        text = page.get_text()

        # If the direct extraction yields no text, it's likely a scanned PDF
        if not text.strip():
            print(f"Page {page_num + 1}: No direct text found. Using OCR...")
                
            # Render the page as a high-resolution image (Pixmap)
            # A higher DPI can improve OCR accuracy
            pix = page.get_pixmap(dpi=300)
                
            # Convert the Pixmap to a Pillow Image object
            img = Image.open(io.BytesIO(pix.tobytes()))
                
            # Use Tesseract to perform OCR on the image
            ocr_text = pytesseract.image_to_string(img)
            full_text.append(ocr_text)
        else:
            print(f"Page {page_num + 1}: Extracted text directly.")
            full_text.append(text)

        doc.close()
        
    # Join all page texts and return
    joined_txt = "\n".join(full_text)
    print(f"joined all text found in {pdf}")
    print(f"saving as {pdf_file.replace('.pdf','.txt')}")
    pdf_file = pdf_file.replace('.pdf','.txt')
    with open(pdf_file, "w", encoding="utf-8") as f:
        f.write(joined_text)
        print(f"Text successfully saved to '{output_path}'")


def run_gemini(gemini_cmd):
    os.chdir('/home/scotty/')
    try:
        print(gemini_cmd)
        result = subprocess.run(
            gemini_cmd, shell=True, check=True, text=True, capture_output=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("pro model quota reach for today")
        print("trying gemini-2.5-flash")
        gemini_cmd = gemini_cmd.replace('--yolo ', '-y -m gemini-2.5-flash ')
        print(gemini_cmd)
        subprocess.run(gemini_cmd, shell=True)

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
    run_gemini(gemini_cmd)
    
main()
