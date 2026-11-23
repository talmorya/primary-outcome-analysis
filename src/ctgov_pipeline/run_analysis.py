"""Execute analysis/outcome_analysis.ipynb in place (figures, tables and cell outputs are refreshed).

Called by `finalize_cohort` on every rebuild; can also be run alone:
    PYTHONPATH=src python -m ctgov_pipeline.run_analysis
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from .analysis_data import ANALYSIS_DIR

NOTEBOOK = ANALYSIS_DIR / "outcome_analysis.ipynb"


def run_analysis_notebook(path: Path = NOTEBOOK, *, timeout: int = 900) -> Path:
    import nbformat
    from nbclient import NotebookClient

    notebook = nbformat.read(path, as_version=4)
    with tempfile.TemporaryDirectory() as tmp:
        # A throwaway kernel spec that runs the notebook with the same interpreter as the pipeline.
        spec_dir = Path(tmp) / "kernels" / "ctgov_pipeline_python"
        spec_dir.mkdir(parents=True)
        spec = {
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "ctgov pipeline",
            "language": "python",
        }
        (spec_dir / "kernel.json").write_text(json.dumps(spec), encoding="utf-8")
        os.environ["JUPYTER_PATH"] = os.pathsep.join(filter(None, [tmp, os.environ.get("JUPYTER_PATH", "")]))
        client = NotebookClient(
            notebook,
            timeout=timeout,
            kernel_name="ctgov_pipeline_python",
            resources={"metadata": {"path": str(path.parent)}},
        )
        client.execute()
    notebook.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbformat.write(notebook, path)
    return path


def main() -> None:
    print(f"Executed {run_analysis_notebook()}")


if __name__ == "__main__":
    main()
