# imi_datasets


## Data Privacy

- `nogit_data` : files are ignored for git commits (definited .gitignore)
Place large files and/or files with PII (personally identifiable
information) in these folders.


- To ensure data is not leaked through juypter notebook output,
  additionally run

nano .git/config

```
[filter "strip-notebook-output"]
    clean = "/Users/owls/v3/bin/jupyter nbconvert --to=notebook --ClearOutputPreprocessor.enabled=True --stdout %f"
    smudge = cat
    required
```

 As well as create a `.gitattributes` file with `*.ipynb filter=strip-notebook-output` 

Note: May require pip install jupyter if you are getting "error: external filter failed jupyter: not found"
NOTE: if you are experiencing lag in the bash prompts in this repository.
Make sure to run `git add --renormalize .` after adding the git attribute.
See https://zhauniarovich.com/post/2020/2020-10-clearing-jupyter-output-p3/

# Output altair to pdf

to output to pdf... need... npm 0_o
https://github.com/altair-viz/altair_saver#installation

```
apt install node
npm install vega-lite vega-cli canvas
```

# install scrubadub addresses

scrub address is separate (phone is built-in)
requires a make install:
https://scrubadub.readthedocs.io/en/latest/addresses.html

