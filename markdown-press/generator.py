import os, markdown
from templates import get_html_template

def generate_site(source_dir='source', output_dir='public'):
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    for filename in os.listdir(source_dir):
        if filename.endswith('.md'):
            with open(os.path.join(source_dir, filename), 'r') as f:
                text = f.read()
            html = markdown.markdown(text)
            title = text.split('\n')[0].strip('# ')
            full_html = get_html_template(title, html)
            out_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.html')
            with open(out_file, 'w') as f: f.write(full_html)
            print(f"-> Converted {filename} to {out_file}")