#!/usr/bin/env python3
"""
ConvexHull_pointcloud_demo.py
--------------------------------
Generates a synthetic LiDAR-style point cloud of a cylindrical bucket and its fill,
then estimates volumes using ConvexHull “tent” geometry.
Outputs: bucket_pointcloud.json
"""

import numpy as np
import json
import math
from scipy.spatial import ConvexHull

# ==========================
# Configurable parameters
# ==========================
bucket_radius = 0.1          # meters
bucket_height = 0.2          # meters
fill_ratio = 0.5             # 0.0–1.0
num_points_wall = 8000
num_points_bottom = 16000
num_points_fill_surface = 8000
output_file = "ConvexHull_pointcloud_demo_data.json"

np.random.seed(0)

# ==========================
# Point cloud generators
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

def estimate_volumes(bottom_pts, wall_pts, fill_pts, radius, height, fill_ratio):
    # Analytical reference
    analytic_capacity = math.pi * radius**2 * height
    analytic_fill = analytic_capacity * fill_ratio

    # ConvexHull “tent” volumes
    full_bucket_pts = np.vstack((bottom_pts, wall_pts, fill_pts))
    hull_full = ConvexHull(full_bucket_pts)
    hull_fill = ConvexHull(np.vstack((bottom_pts, fill_pts)))

    return {
        "analytic_capacity_m3": analytic_capacity,
        "analytic_fill_m3": analytic_fill,
        "convex_hull_full_m3": hull_full.volume,
        "convex_hull_fill_m3": hull_fill.volume
    }

# ==========================
# Main
# ==========================

if __name__ == "__main__":
    # Generate points
    wall_pts = generate_cylinder_wall(bucket_radius, bucket_height, num_points_wall)
    bottom_pts = generate_bottom(bucket_radius, num_points_bottom)
    fill_pts = generate_fill_surface(bucket_radius, bucket_height, fill_ratio, num_points_fill_surface)
    empty_bucket = np.vstack((wall_pts, bottom_pts))
    full_bucket = np.vstack((empty_bucket, fill_pts))

    # Compute volumes
    vols = estimate_volumes(bottom_pts, wall_pts, fill_pts, bucket_radius, bucket_height, fill_ratio)

    # Prepare metadata
    metadata = {
        "bucket_radius": bucket_radius,
        "bucket_height": bucket_height,
        "fill_ratio": fill_ratio,
        "num_points_wall": num_points_wall,
        "num_points_bottom": num_points_bottom,
        "num_points_fill_surface": num_points_fill_surface,
        "analytic_capacity_m3": round(vols["analytic_capacity_m3"], 6),
        "analytic_capacity_liters": round(vols["analytic_capacity_m3"] * 1000, 3),
        "analytic_fill_m3": round(vols["analytic_fill_m3"], 6),
        "analytic_fill_liters": round(vols["analytic_fill_m3"] * 1000, 3),
        "convex_hull_full_m3": round(vols["convex_hull_full_m3"], 6),
        "convex_hull_full_liters": round(vols["convex_hull_full_m3"] * 1000, 3),
        "convex_hull_fill_m3": round(vols["convex_hull_fill_m3"], 6),
        "convex_hull_fill_liters": round(vols["convex_hull_fill_m3"] * 1000, 3),
    }

    # JSON payload
    data = {
        "metadata": metadata,
        "empty_bucket": empty_bucket.tolist(),
        "fill_surface": fill_pts.tolist(),
        "full_bucket": full_bucket.tolist()
    }

    # Save to JSON
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {output_file}")
    print(f"Bucket capacity: {metadata['analytic_capacity_liters']} L")
    print(f"Analytic fill: {metadata['analytic_fill_liters']} L")
    print(f"Convex-hull fill volume: {metadata['convex_hull_fill_liters']} L")
