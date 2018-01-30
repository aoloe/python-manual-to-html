import mistune # markdown library
import yaml # reading the manual settings
import os.path
import shutil # copy files

class ManualRenderer(mistune.Renderer):
    """
    Enhanced Markdown renderer
    """
    h1_level = 1
    h1_anchor = None
    toc_index = 1
    toc = []
    images = []
    def __init__(self, *args, **kwargs):
        if kwargs is not None:
            if 'h1_level' in kwargs:
                self.h1_level = kwargs['h1_level']
        super(ManualRenderer, self).__init__(*args, **kwargs)
        
    def clear(self):
        """
        clear the chapter variables
        """
        self.h1_anchor = None
        self.toc = []
        self.images = []

    def header(self, text, level, raw = None):
        """
        - add the "manual" anchor to h1, if one exists
        - add the anchors to the h#
        - set the starting h# level
        """
        if level == 1 and self.h1_anchor is not None:
            text = '<a name="{1}">{0}</a>'.format(text, self.h1_anchor)
        else:
            toc_index = 'toc-{:03d}'.format(self.toc_index)
            self.toc.append((toc_index, text))
            text = '<a name="{1}">{0}</a>'.format(text, toc_index)
            self.toc_index += 1

        level = level + self.h1_level - 1
        return super(ManualRenderer, self).header(text, level, raw)

    def image(self, src, title, alt_text):
        """
        - change the path to only retain the relative path from the file
        - create the list of used images
        """
        self.images.append(src)
        return super(ManualRenderer, self).image(src, title, alt_text)

manualRenderer = ManualRenderer(h1_level=2)
markdown = mistune.Markdown(renderer=manualRenderer)

class InlineRenderer(mistune.Renderer):
    """
    Renderer for markdown text that is shorter than a paragraph
    """
    def paragraph(self, text):
        """
        just return the text for paragraph (do not add <p>
        """
        return text

inlineMarkdown = mistune.Markdown(InlineRenderer())

# Open the manual yaml definition file
try:
    with open('manual.yaml', 'r') as f:
        manual = yaml.load(f)
except ValueError:
    # TODO: correctly give feedback on parsing or file not found
    print(Error)

# Define the paths
path_content = 'content'
path_out = 'out'
path_out_images = 'images'
path_out_css = 'css'

# Create the introductive part, with the title,
# and the introduction
html_introduction = []

if 'title' in manual:
    html_introduction.append('<h1>{}</h1>\n'.format(inlineMarkdown(manual['title'])))

if 'introduction' in manual:
    try:
        f = open(manual['introduction'], 'r')
    except IOError:
        # TODO: error handling
        pass
    else:
        with f:
            content = f.read()
            html_introduction.append(markdown(content))

# Read all the files in the toc list
html = []    
toc = {}
images = []
for section, title in manual['toc'].items():
    # TODO: check if filename and title are set
    # TODO: is there a better way to get the key values?
    # section_id = list(section.keys())[0]
    # title = list(section.values())[0]
    filename = section + '.md'
    path_section = os.path.join(path_content, section)
    path_markdown = os.path.join(path_section, filename)
    content = None
    try:
        f = open(path_markdown, 'r')
    except IOError:
        # TODO: error handling
        pass
    else:
        with f:
            content = f.read()

    if content is not None:
        manualRenderer.clear()
        manualRenderer.h1_anchor = section
        html.append(markdown(content))
        toc[(section, title)] = manualRenderer.toc
        for image in manualRenderer.images:
            images.append((section, image))

# Add the table of contents to the introductive part
content = ""
content += "<ul>\n"
for section, item in toc.items():
    content += '<li><a href="{}">{}</a>\n'.format(section[0], section[1])
    if item:
        content += "<ul>\n"
        for toc_entry in item:
            content += '<li><a href="{}">{}</a></li>\n'.format('#'+toc_entry[0], toc_entry[1])
        content += "</ul>\n"

content += "</li></ul>\n"

html_introduction += content


# Ensure the directories structure
if not os.path.exists(path_out):
    os.mkdir(path_out)
if not os.path.exists(os.path.join(path_out, path_out_images)):
    os.mkdir(os.path.join(path_out, path_out_images))
if not os.path.exists(os.path.join(path_out, path_out_css)):
    os.mkdir(os.path.join(path_out, path_out_css))

# Copy the images in the out directory
for image in images:
    image_src_path = os.path.join(path_content, image[0], image[1])
    if os.path.isfile(image_src_path):
        image_filename = os.path.basename(image[1])
        image_out = os.path.join(path_out, 'images', image_filename)
        shutil.copy2(image_src_path, image_out)

# If a theme is defined, use it
html_template = {}
if 'theme' in manual:
    # Copy the css files
    if 'css' in manual['theme']:
        for css in manual['theme']['css']:
            shutil.copy2(css, os.path.join(path_out, path_out_css))


    # Read the html template
    if 'template' in manual['theme']:
        if isinstance(manual['theme']['template'], dict):
            pass
        else:
            if os.path.isfile(manual['theme']['template']):
                f = open(manual['theme']['template'], 'r')
                html_template['index.html'] = f.read()
            else:
                # TODO: warn about the missing template
                pass

# If none defined, use the default template
if not 'index.html' in html_template:
    html_template['index.html'] = """
<!doctype html>
<html lang={lang}>
<head>
    <meta charset=utf-8>
    <title>{title}</title>
</head>
<body>
{content}
</body>
</html>
    """

with open(os.path.join(path_out, 'index.html'), 'w') as f:
    f.write(html_template['index.html'].format(title = manual['title'], content=''.join(html_introduction + html), lang = 'en'))
