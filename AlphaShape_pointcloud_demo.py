#!/usr/bin/env python3
"""
AlphaShape_pointcloud_demo.py
-----------------------------
Generates a LiDAR-style bucket point cloud and estimates volumes
using an Alpha-Shape ("concave hull") algorithm.

Requires:
    pip install alphashape shapely numpy scipy

Outputs:
    bucket_pointcloud_alpha.json
"""

import numpy as np
import json
import math
import alphashape
from shapely.geometry import MultiPoint
from scipy.spatial import ConvexHull

# ==========================
# Configurable parameters
# ==========================
bucket_radius = 0.1          # meters
bucket_height = 0.2          # meters
fill_ratio = 0.5             # fraction of height filled (0–1)
num_points_wall = 8000
num_points_bottom = 16000
num_points_fill_surface = 8000
alpha_value = 2.0            # smaller = tighter tent
output_file = "AlphaShape_pointcloud_demo_data.json"

np.random.seed(0)

# ==========================
# Geometry generation
# ==========================
def generate_cylinder_wall(radius, height, n_points):
    theta = np.random.rand(n_points) * 2 * np.pi
    z = np.random.rand(n_points) * height
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return np.column_stack((x, y, z))

def generate_bottom(radius, n_points):
    r = np.sqrt(np.random.rand(n_points)) * radius
    theta = np.random.rand(n_points) * 2 * np.pi
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.zeros_like(r)
    return np.column_stack((x, y, z))

def generate_fill_surface(radius, height, fill_ratio, n_points):
    z_fill = fill_ratio * height
    r = np.sqrt(np.random.rand(n_points)) * radius
    theta = np.random.rand(n_points) * 2 * np.pi
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = np.ones_like(r) * z_fill
    return np.column_stack((x, y, z))

# ==========================
# Volume estimation
# ==========================
def estimate_volumes(bottom_pts, wall_pts, fill_pts, radius, height, fill_ratio, alpha):
    analytic_capacity = math.pi * radius**2 * height
    analytic_fill = analytic_capacity * fill_ratio
    fill_region = np.vstack((bottom_pts, fill_pts))

    # subsample for alpha-shape speed
    if fill_region.shape[0] > 5000:
        idx = np.random.choice(fill_region.shape[0], 5000, replace=False)
        fill_region = fill_region[idx]

    try:
        shape = alphashape.alphashape(fill_region, alpha)
        alpha_vol = shape.volume if hasattr(shape, "volume") else 0.0
    except Exception:
        from scipy.spatial import ConvexHull
        alpha_vol = ConvexHull(fill_region).volume

    hull_full = ConvexHull(np.vstack((bottom_pts, wall_pts, fill_pts)))

    return {
        "analytic_capacity_m3": analytic_capacity,
        "analytic_fill_m3": analytic_fill,
        "convex_hull_full_m3": hull_full.volume,
        "alpha_shape_fill_m3": alpha_vol
    }


# ==========================
# Main
# ==========================
if __name__ == "__main__":
    wall_pts = generate_cylinder_wall(bucket_radius, bucket_height, num_points_wall)
    bottom_pts = generate_bottom(bucket_radius, num_points_bottom)
    fill_pts = generate_fill_surface(bucket_radius, bucket_height, fill_ratio, num_points_fill_surface)
    empty_bucket = np.vstack((wall_pts, bottom_pts))
    full_bucket = np.vstack((empty_bucket, fill_pts))

    vols = estimate_volumes(bottom_pts, wall_pts, fill_pts,
                            bucket_radius, bucket_height, fill_ratio, alpha_value)

    metadata = {
        "bucket_radius": bucket_radius,
        "bucket_height": bucket_height,
        "fill_ratio": fill_ratio,
        "num_points_wall": num_points_wall,
        "num_points_bottom": num_points_bottom,
        "num_points_fill_surface": num_points_fill_surface,
        "alpha_value": alpha_value,
        "analytic_capacity_m3": round(vols["analytic_capacity_m3"], 6),
        "analytic_capacity_liters": round(vols["analytic_capacity_m3"] * 1000, 3),
        "analytic_fill_m3": round(vols["analytic_fill_m3"], 6),
        "analytic_fill_liters": round(vols["analytic_fill_m3"] * 1000, 3),
        "convex_hull_full_m3": round(vols["convex_hull_full_m3"], 6),
        "convex_hull_full_liters": round(vols["convex_hull_full_m3"] * 1000, 3),
        "alpha_shape_fill_m3": round(vols["alpha_shape_fill_m3"], 6),
        "alpha_shape_fill_liters": round(vols["alpha_shape_fill_m3"] * 1000, 3)
    }

    data = {
        "metadata": metadata,
        "empty_bucket": empty_bucket.tolist(),
        "fill_surface": fill_pts.tolist(),
        "full_bucket": full_bucket.tolist()
    }

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {output_file}")
    print(f"Bucket capacity: {metadata['analytic_capacity_liters']} L")
    print(f"Analytic fill: {metadata['analytic_fill_liters']} L")
    print(f"Alpha-shape fill volume: {metadata['alpha_shape_fill_liters']} L")
