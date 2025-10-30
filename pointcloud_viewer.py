# Suggested filename: pointcloud_viewer_toggle.py
#
# Point cloud viewer for bucket_volume_pointcloud_demo.json
# Lets you pick a JSON file via Tkinter and toggle between
# empty_bucket, fill_points, and full_bucket.
#
# Requirements:
#   pip install plotly

import json
import tkinter as tk
from tkinter import filedialog
import plotly.graph_objects as go

def main():
    # File picker
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select point cloud JSON",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if not file_path:
        print("No file selected.")
        return

    with open(file_path, "r") as f:
        data = json.load(f)

    # Extract groups if present
    empty_points = data.get("empty_bucket", [])
    fill_points  = data.get("fill_points", [])
    full_points  = data.get("full_bucket", [])

    fig = go.Figure()

    traces = []
    labels = []

    if empty_points:
        xs, ys, zs = zip(*empty_points)
        traces.append(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="markers",
            marker=dict(size=2, color="blue", opacity=0.6),
            name="Empty Bucket",
            visible=True
        ))
        labels.append("Empty Bucket")

    if fill_points:
        xs, ys, zs = zip(*fill_points)
        traces.append(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="markers",
            marker=dict(size=2, color="orange", opacity=0.6),
            name="Fill Points",
            visible=True
        ))
        labels.append("Fill Points")

    if full_points:
        xs, ys, zs = zip(*full_points)
        traces.append(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="markers",
            marker=dict(size=2, color="green", opacity=0.6),
            name="Full Bucket",
            visible=True
        ))
        labels.append("Full Bucket")

    for t in traces:
        fig.add_trace(t)

    # Build dropdown buttons
    n = len(traces)
    buttons = []
    buttons.append(dict(label="All", method="update",
                        args=[{"visible": [True]*n}]))
    for i, label in enumerate(labels):
        vis = [False]*n
        vis[i] = True
        buttons.append(dict(label=label, method="update",
                            args=[{"visible": vis}]))

    fig.update_layout(
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True
        )],
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z"
        ),
        title=f"Point Cloud Viewer: {file_path}"
    )

    fig.show()

if __name__ == "__main__":
    main()
