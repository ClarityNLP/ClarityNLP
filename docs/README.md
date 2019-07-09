## ClarityNLP documentation

ClarityNLP uses [Sphinx Documentation](https://www.sphinx-doc.org/en/master/usage/quickstart.html).
Once installed, the ClarityNLP documentation site can be ran locally via
[Sphinx Autobuild](https://pypi.org/project/sphinx-autobuild/) or via `make`. Documentation can use `.rst` (ReStructured Text) 
or `'.md` (Markdown) file types.

### Deployment

ClarityNLP Documentation is auto-deployed via [ReadTheDocs](https://readthedocs.org). ClarityNLP has two 
main branches auto-deployed:

* [development](claritynlpdev.readthedocs.io)
* [master](http://claritynlp.readthedocs.io/) ([alternate link](http://clarity-nlp.readthedocs.io/))

### FAQs

You may need to install the custom theme as well to run the project locally.
```python
pip install sphinx_rtd_theme
```

To run locally, and after installing Sphinx Autobuild (see above), from ClarityNLP root directory, run:
```bash
sphinx-autobuild docs docs/_build/html
```
