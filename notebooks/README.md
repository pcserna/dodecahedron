# notebooks/

## `RDORP_Reproduction.ipynb`

Every quantitative claim the project makes, recomputed from the master database
and from first principles, ending in a cell that asserts each headline figure.

It does **not** read the documents. It derives each number independently and
then checks it against what RDORP-012 publishes, so a corpus change that is not
carried into the prose makes the notebook fail rather than agree.

Part 8 recomputes the seven computational experiments (`EXP-0002` to
`EXP-0007`). Those results had been recorded as prose in the `experiments`
table and **the code that produced them was never committed**, so until now
nobody could check them.

Part 11 prints every result in one place. Part 12 asserts them.

## Regenerating

```bash
python run_pipeline.py                       # rebuild the database first
python notebooks/build_notebook.py --exec    # rebuild the notebook and run it
```

The notebook is **generated** from `build_notebook.py`, not edited by hand:
edits made in Jupyter are lost on the next build. Change the cells in
`build_notebook.py` and rebuild.

The committed `.ipynb` carries its outputs, and `database/test_render_docs.py`
fails if it does not — a notebook with no outputs proves nothing.

## `cell_index.json`

Generated. Maps each finding to the notebook cell that establishes it.
`database/render_docs.py` turns it into the reproduction index in RDORP-012
§1A, and `test_render_docs.py` fails if any link points at a cell that no
longer exists.

Cell ids are anchors. Renaming one breaks every cross-reference to it, so
`cid=` values in `build_notebook.py` should be treated as stable identifiers.
