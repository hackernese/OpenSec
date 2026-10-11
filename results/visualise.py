import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory
from matplotlib.ticker import PercentFormatter

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def stacked_bar_groups_percent(years, regions, data, title="Chart Title"):
    bars_per_year = len(regions)
    total_bars = len(years) * bars_per_year

    # Check that every data list has a value for every bar
    for name, values in data.items():
        if len(values) != total_bars:
            raise ValueError(
                f"'{name}' needs {total_bars} values "
                f"({len(years)} years × {len(regions)} regions)."
            )

    # Create bar positions with a gap between each year
    x = np.arange(total_bars) + np.repeat(
        np.arange(len(years)),
        bars_per_year
    )

    colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000"]
    text_colors = ["white", "white", "black", "black"]

    # Original counts: one row per category/colour
    values = np.array(list(data.values()), dtype=float)

    # Total count for every individual bar
    totals = values.sum(axis=0)

    # Convert each bar into percentages
    percentages = np.divide(
        values,
        totals,
        out=np.zeros_like(values),
        where=totals != 0
    ) * 100

    fig, ax = plt.subplots(figsize=(12, 7))
    bottom = np.zeros(total_bars)

    # Draw each coloured stack
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

        # Write count and percentage inside each segment
        for bar_x, raw_value, percent_value, current_bottom in zip(
            x, raw_values, percent_values, bottom
        ):
            if percent_value >= 5:  # Avoid unreadable labels on tiny segments
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

    # Region names under every bar
    ax.set_xticks(x)
    ax.set_xticklabels(regions * len(years))

    # Year names under each region group
    for i, year in enumerate(years):
        group_x = x[i * bars_per_year:(i + 1) * bars_per_year]
        middle = group_x.mean()

        ax.text(
            middle,
            -0.12,
            str(year),
            ha="center",
            transform=ax.get_xaxis_transform(),
            fontsize=12
        )

    ax.set_title(title)
    ax.set_ylim(0, 1)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.yaxis.set_major_formatter(PercentFormatter(100))

    ax.grid(axis="y", alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend()

    plt.subplots_adjust(bottom=0.18)
    plt.show()

    return fig, ax

def plot_times_with_average(data):
    """
    data example:
    {
        "Model A": [14, 16, 15, 18, 17],
        "Model B": [23, 21, 26, 25, 24],
        "Model C": [12, 13, 11, 14, 12],
    }
    """

    fig, ax = plt.subplots(figsize=(10, 6))

    colours = ["#2563EB", "#0891B2", "#7C3AED"]

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
        average = np.mean(times)

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
        ax.text(i + 0.32, average, f"{average:.1f} min", va="center")

    ax.set_title("Time taken across repeated runs", fontweight="bold")
    ax.set_ylabel("Time taken (minutes)")
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.keys())

    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.show()