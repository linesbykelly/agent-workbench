import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from typing import List, Optional, Literal, Dict
import logging

from agents import function_tool
from utils import _get_files_path


logger = logging.getLogger(__name__)


def generate_plot(
    x: List,
    y: List,
    kind: Literal["line", "bar", "scatter", "hist"] = "line",
    hue: Optional[List] = None,
    title: Optional[str] = "Data Plot",
    x_label: Optional[str] = "X",
    y_label: Optional[str] = "Y",
    filename: str = "plot.png"
) -> Dict:

    figure = None

    try:
        if not x:
            raise ValueError("'x' must contain at least one value")

        if not y:
            raise ValueError("'y' must contain at least one value")

        if len(x) != len(y):
            raise ValueError(
                "Length of 'x' must match length of 'y'"
            )

        if hue is not None and len(hue) != len(x):
            raise ValueError(
                "Length of 'hue' must match length of 'x' and 'y'"
            )

        if kind not in {"line", "bar", "scatter", "hist"}:
            raise ValueError(
                f"Unsupported kind: {kind}"
            )

        data = {
            "x": x,
            "y": y
        }

        if hue is not None:
            data["hue"] = hue

        df = pd.DataFrame(data)

        figure = plt.figure(
            figsize=(10, 6)
        )

        plot_args = {
            "data": df,
            "x": "x",
            "y": "y"
        }

        if hue is not None:
            plot_args["hue"] = "hue"

        if kind == "line":
            sns.lineplot(**plot_args)

        elif kind == "bar":
            sns.barplot(**plot_args)

        elif kind == "scatter":
            sns.scatterplot(**plot_args)

        elif kind == "hist":
            sns.histplot(
                data=df,
                x="x",
                hue="hue" if hue is not None else None
            )

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # All generated files go into the shared files directory.
        output_path = _get_files_path(filename)

        figure.savefig(output_path)

        logger.info(
            "Plot saved to: %s",
            output_path
        )

        return {
            "success": True,
            "data": str(output_path.resolve()),
            "error": None
        }

    except Exception as e:

        logger.exception(
            "Failed to generate plot: %s",
            filename
        )

        return {
            "success": False,
            "data": None,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }

    finally:

        if figure is not None:
            plt.close(figure)


@function_tool
def plot_data_tool(
    x: List,
    y: List,
    kind: Literal["line", "bar", "scatter", "hist"] = "line",
    hue: Optional[List] = None,
    title: Optional[str] = "Data Plot",
    x_label: Optional[str] = "X",
    y_label: Optional[str] = "Y",
    filename: str = "plot.png"
) -> Dict:
    """
    Create a plot and save it to the shared files directory.

    Args:
        x: X-axis values.
        y: Y-axis values.
        kind: Type of plot: line, bar, scatter, or hist.
        hue: Optional grouping values.
        title: Plot title.
        x_label: X-axis label.
        y_label: Y-axis label.
        filename: Filename for the generated image.

    Returns:
        A result indicating whether the plot was created successfully.
    """

    return generate_plot(
        x,
        y,
        kind,
        hue,
        title,
        x_label,
        y_label,
        filename
    )