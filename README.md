# Create an HTML manual from the markdown sources

This is not one more static site / manual generator.

This is my bundle of existing python libraries for generating a static html manual from markdown sources.

Your free to use it for anything you see fit, but be aware that it's 100% tailored to my own needs. You probably should rather get inspiration from the code to create your own script or use one of the many _real_ static site generators.

## Install and run

```sh
pip install -r requirements.txt
```

`cd` to your manual, create a `manual.yaml` project file with the list of the files to be converted, and run the `main.py` script.

## Project structure

the project can have each chapter:

- in markdown files directly in the `content` directory (TODO: not implemented yet)
- in sub directories of `content`, with a markdown file with the same name in each directory.

## The `manual.yaml` file

- `title`: The title of the manual
- `introduction`: path to a markdown file with the text preceding the first chapter
- `toc`: list or dictionary with the list of sections
  - the dictionary's keys are the file name without the `.md` extension and the values each section's title
  - the list only contain the file names without the `md` extension (the title being read from the last `h1` title in the file; TODO: not implemented yet).
- `theme`:
  - `template`: path to an html file.
  - `css`: css files to be copied to the `out/` directory

## The Html template

For now, it only supports a main template defining the whole page and providing three fields:

- `lang`: the country code for the document language
- `title`: the title of the page (mostly, the name of the manual)
- `content`: the full content

## Todo

Planned features:

- Add for each section a link to the github sources ("This page is open source. Noticed a typo? Or something unclear? Improve this page on GitHub"
- Option for multiple html files output
- Find a good way to show the list of contributors and the copyright notice.
