import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory
from matplotlib.ticker import PercentFormatter
from matplotlib.colors import ListedColormap, BoundaryNorm

def grouped_bar_chart(groups, data, title="Chart Title"):
    group_count = len(groups)
    category_count = len(data)

    # Every category needs one value per group
    for name, values in data.items():
        if len(values) != group_count:
            raise ValueError(
                f"'{name}' needs {group_count} values "
                f"(one for each group)."
            )

    x = np.arange(group_count)

    colors = ["#4472C4", "#A5A5A5", "#ED7D31", "#FFC000", "#A246DB"]

    group_width = 0.8
    bar_width = group_width / category_count

    # Positions of the five small bars around each group centre
    offsets = (
        np.arange(category_count) - (category_count - 1) / 2
    ) * bar_width

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (name, values) in enumerate(data.items()):
        values = np.array(values, dtype=float)
        positions = x + offsets[i]

        ax.bar(
            positions,
            values,
            width=bar_width,
            label=name,
            color=colors[i % len(colors)],
            edgecolor="black"
        )

        # Count above each bar
        for bar_x, value in zip(positions, values):
            if value > 0:
                ax.text(
                    bar_x,
                    value,
                    f"{value:g}",
                    ha="center",
                    va="bottom",
                    fontsize=9
                )

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_title(title)
    ax.set_ylabel("Number of findings")
    ax.set_ylim(bottom=0)

    ax.grid(axis="y", alpha=0.4)
    ax.set_axisbelow(True)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=category_count,
        frameon=False
    )

    plt.subplots_adjust(bottom=0.18)
    plt.show()

    return fig, ax

def plot_model_summary(
    metrics,
    title="Model comparison: discovery and severity consistency",
):
    """
    Example metrics:

    metrics = {
        "Known-bug recall": {
            "LLM A": 100,
            "LLM B": 67,
            "LLM C": 100,
        },
        "Discovery consistency": {
            "LLM A": 87,
            "LLM B": 67,
            "LLM C": 100,
        },
        "Severity consistency": {
            "LLM A": 80,
            "LLM B": 50,
            "LLM C": 100,
        },
    }
    """

    metric_names = list(metrics.keys())
    models = list(next(iter(metrics.values())).keys())

    colors = ["#4472C4", "#ED7D31", "#8A8A8A", "#A5A5A5", "#7030A0"]
    markers = ["o", "s", "D", "^", "X"]

    # Slight vertical separation so model markers do not overlap
    spacing = 0.18
    offsets = [
        (index - (len(models) - 1) / 2) * spacing
        for index in range(len(models))
    ]

    y_positions = list(range(len(metric_names)))

    fig, ax = plt.subplots(figsize=(10, 5))

    for model_index, model in enumerate(models):
        values = [metrics[metric][model] for metric in metric_names]
        y_values = [
            y + offsets[model_index]
            for y in y_positions
        ]

        ax.scatter(
            values,
            y_values,
            label=model,
            color=colors[model_index % len(colors)],
            marker=markers[model_index % len(markers)],
            s=85,
            zorder=3,
        )

        # Percentage labels beside each marker
        for value, y in zip(values, y_values):
            ax.text(
                value + 1.5,
                y,
                f"{value}%",
                va="center",
                fontsize=9,
            )

    ax.set_title(title)
    ax.set_xlabel("Percentage across repeated runs")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(metric_names)

    ax.set_xlim(0, 110)
    ax.set_xticks(range(0, 101, 25))
    ax.set_xticklabels([f"{value}%" for value in range(0, 101, 25)])

    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.invert_yaxis()  # Keeps Known-bug recall at the top

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        title="Model",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0,
    )
    
    fig.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

    return fig, ax

def plot_bugs_per_run(
    results,
    title="Individual-run comparison: bugs found per LLM",
    ylabel="Number of bugs found",
    styles=None,
    figsize=(8, 5),
    y_max=None,
):
    """
    Plot the number of bugs found by each LLM across experimental runs.

    Parameters
    ----------
    results : dict
        Example:
        {
            "LLM A": [4, 5, 4],
            "LLM B": [3, 4, 3],
        }
    title : str
        Chart title.
    ylabel : str
        Y-axis label.
    styles : dict, optional
        Per-model plot styles, e.g. {"LLM A": {"color": "#4472C4", "marker": "o"}}.
    figsize : tuple
        Figure size as (width, height).
    y_max : int, optional
        Maximum y-axis value. Calculated automatically if omitted.

    Returns
    -------
    fig, ax
        Matplotlib figure and axes objects.
    """
    run_count = len(next(iter(results.values())))
    runs = list(range(1, run_count + 1))

    default_styles = [
        {"color": "#ED7D31", "marker": "o"},
        {"color": "#4472C4", "marker": "s"},
        {"color": "#BB45FF", "marker": "D"},
        {"color": "#A5A5A5", "marker": "^"},
        {"color": "#FFC000", "marker": "P"},
    ]

    if styles is None:
        styles = {
            model: default_styles[i % len(default_styles)]
            for i, model in enumerate(results)
        }

    fig, ax = plt.subplots(figsize=figsize)

    for i, (model, findings) in enumerate(results.items()):
        style = styles.get(model, default_styles[i % len(default_styles)])

        ax.plot(
            runs,
            findings,
            label=model,
            linewidth=2,
            markersize=8,
            **style,
        )

    max_value = max(max(findings) for findings in results.values())
    if y_max is None:
        y_max = max_value + 1

    ax.set_title(title)
    ax.set_xlabel("Experimental run")
    ax.set_ylabel(ylabel)

    ax.set_xticks(runs)
    ax.set_xticklabels([f"Run {run}" for run in runs])

    ax.set_ylim(0, y_max)
    ax.set_yticks(range(0, y_max + 1))

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(title="Model")

    plt.tight_layout()
    plt.show()

    return fig, ax

def stacked_bar_groups_percent(years, regions, data, total, title="Chart Title"):
    bars_per_year = len(regions)
    total_bars = len(years) * bars_per_year

    for name, values in data.items():
        if len(values) != total_bars:
            raise ValueError(
                f"'{name}' needs {total_bars} values "
                f"({len(years)} years × {len(regions)} regions)."
            )

    if total <= 0:
        raise ValueError("'total' must be greater than 0.")

    x = np.arange(total_bars) + np.repeat(
        np.arange(len(years)),
        bars_per_year
    )

    colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#A246DB"]
    text_colors = ["white", "white", "black", "black", "white"]

    values = np.array(list(data.values()), dtype=float)

    # Each value is now a percentage of the total you supplied.
    percentages = (values / total) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    bottom = np.zeros(total_bars)

    for i, ((name, _), raw_values, percent_values) in enumerate(
        zip(data.items(), values, percentages)
    ):
        ax.bar(
            x,
            percent_values,
            bottom=bottom,
            label=name,
            color=colors[i % len(colors)],
            edgecolor="black"
        )

        for bar_x, raw_value, percent_value, current_bottom in zip(
            x, raw_values, percent_values, bottom
        ):
            if percent_value >= 5:
                ax.text(
                    bar_x,
                    current_bottom + percent_value / 2,
                    f"{raw_value:g}\n({percent_value:.0f}%)",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=text_colors[i % len(text_colors)]
                )

        bottom += percent_values

    ax.set_xticks(x)
    ax.set_xticklabels(regions * len(years))

    for i, year in enumerate(years):
        group_x = x[i * bars_per_year:(i + 1) * bars_per_year]

        ax.text(
            group_x.mean(),
            -0.12,
            str(year),
            ha="center",
            transform=ax.get_xaxis_transform(),
            fontsize=12
        )

    ax.set_title(title)
    ax.set_ylim(0, 100)  # Changed from (0, 1)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.yaxis.set_major_formatter(PercentFormatter(100))

    ax.grid(axis="y", alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=len(data),
        frameon=False
    )

    plt.subplots_adjust(bottom=0.18)
    plt.show()

    return fig, ax

def plot_dot_with_median(data, title, subtitle, unit):
    """
    data example:
    {
        "Model A": [14, 16, 15, 18, 17],
        "Model B": [23, 21, 26, 25, 24],
        "Model C": [12, 13, 11, 14, 12],
    }
    """

    fig, ax = plt.subplots(figsize=(10, 6))

    colours = ["#FFA845", "#2563EB", "#7C3AED"]

    for i, (name, times) in enumerate(data.items()):
        # Spread dots slightly horizontally so they do not overlap
        x_positions = np.full(len(times), i) + np.linspace(-0.13, 0.13, len(times))

        # Individual runs
        ax.scatter(
            x_positions,
            times,
            s=70,
            color=colours[i % len(colours)],
            alpha=0.8,
            label="Individual run" if i == 0 else None
        )

        # Average
        average = np.median(times)

        # Horizontal average line
        ax.hlines(
            average,
            i - 0.28,
            i + 0.28,
            color="#111827",
            linewidth=2.5,
            label="Average time" if i == 0 else None
        )

        # Diamond in the centre of the average line
        ax.scatter(i, average, marker="D", s=90, color="#111827", zorder=3)

        # Average label
        ax.text(i + 0.32, average, f"{average:.1f} {unit}", va="center")

    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(subtitle)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.keys())

    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()