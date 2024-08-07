"""Dynamic visualization of PyTensor graphs.

Author: Christof Angermueller <cangermueller@gmail.com>
"""

import json
import shutil
from pathlib import Path

from pytensor.d3viz.formatting import PyDotFormatter


__path__ = Path(__file__).parent


def replace_patterns(x, replace):
    """Replace `replace` in string `x`.

    Parameters
    ----------
    s : str
        String on which function is applied
    replace : dict
        `key`, `value` pairs where key is a regular expression and `value` a
        string by which `key` is replaced
    """
    for from_, to in replace.items():
        x = x.replace(str(from_), str(to))
    return x


def safe_json(obj):
    """Encode `obj` to JSON so that it can be embedded safely inside HTML.

    Parameters
    ----------
    obj : object
        object to serialize
    """
    return json.dumps(obj).replace("<", "\\u003c")


def d3viz(fct, outfile: Path | str, copy_deps: bool = True, *args, **kwargs):
    """Create HTML file with dynamic visualizing of an PyTensor function graph.

    In the HTML file, the whole graph or single nodes can be moved by drag and
    drop. Zooming is possible via the mouse wheel. Detailed information about
    nodes and edges are displayed via mouse-over events. Node labels can be
    edited by selecting Edit from the context menu.

    Input nodes are colored in green, output nodes in blue. Apply nodes are
    ellipses, and colored depending on the type of operation they perform.

    Edges are black by default. If a node returns a view of an
    input, the input edge will be blue. If it returns a destroyed input, the
    edge will be red.

    Parameters
    ----------
    fct : pytensor.compile.function.types.Function
        A compiled PyTensor function, variable, apply or a list of variables.
    outfile : Path | str
        Path to output HTML file.
    copy_deps : bool, optional
        Copy javascript and CSS dependencies to output directory.

    Notes
    -----
    This function accepts extra parameters which will be forwarded to
    :class:`pytensor.d3viz.formatting.PyDotFormatter`.

    """

    # Create DOT graph
    formatter = PyDotFormatter(*args, **kwargs)
    graph = formatter(fct)
    dot_graph = graph.create_dot()
    dot_graph = dot_graph.decode("utf8")

    # Create output directory if not existing
    outdir = Path(outfile).parent
    outdir.mkdir(exist_ok=True)

    # Read template HTML file
    template_file = __path__ / "html/template.html"
    template = template_file.read_text(encoding="utf-8")

    # Copy dependencies to output directory
    src_deps = __path__
    if copy_deps:
        dst_deps = outdir / "d3viz"
        for d in ("js", "css"):
            dep = dst_deps / d
            if not dep.exists():
                shutil.copytree(src_deps / d, dep)
    else:
        dst_deps = src_deps

    # Replace patterns in template
    replace = {
        "%% JS_DIR %%": dst_deps / "js",
        "%% CSS_DIR %%": dst_deps / "css",
        "%% DOT_GRAPH %%": safe_json(dot_graph),
    }
    html = replace_patterns(template, replace)

    # Write HTML file
    Path(outfile).write_text(html)


def d3write(fct, path, *args, **kwargs):
    """Convert PyTensor graph to pydot graph and write to dot file.

    Parameters
    ----------
    fct : pytensor.compile.function.types.Function
        A compiled PyTensor function, variable, apply or a list of variables.
    path: str
        Path to output file

    Notes
    -----
    This function accepts extra parameters which will be forwarded to
    :class:`pytensor.d3viz.formatting.PyDotFormatter`.

    """

    formatter = PyDotFormatter(*args, **kwargs)
    graph = formatter(fct)
    graph.write_dot(path)
