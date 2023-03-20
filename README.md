# imi_datasets


## Data Privacy

- `nogit_data` : files are ignored for git commits (definited .gitignore)
Place large files and/or files with PII (personally identifiable
information) in these folders.


- To ensure data is not leaked through juypter notebook output,
  additionally run

 `git config filter.strip-notebook-output.clean 'jupyter nbconvert --ClearOutputPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=ERROR'  `

 As well as create a `.gitattributes` file with `*.ipynb filter=strip-notebook-output` 

Note: May require pip install jupyter if you are getting "error: external filter failed jupyter: not found"
