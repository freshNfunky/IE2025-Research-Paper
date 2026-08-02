"""Production depth source: LiDAR projected into the image (stub).

The spike uses monocular depth (depth.py). In production the *same* per-box
flatness/foreground test is fed by LiDAR, which gives METRIC depth and is not
fooled by monocular scale ambiguity. Implementing this needs synchronized
camera + LiDAR + calibration (e.g. KITTI: velodyne .bin, calib P2 / R0_rect /
Tr_velo_to_cam), plus pykitti/open3d. Interface intended:

    class LidarFrame:
        def __init__(self, image, points_xyz, calib): ...
        def sparse_depth(self) -> np.ndarray:   # project points -> HxW depth
            ...
        # then reuse depth.flatness(sparse_depth, box)

Deferred: needs LiDAR data (GBs) and calibration handling; see
docs/spikes/open_world_feasibility.md section C.
"""
raise NotImplementedError("LiDAR depth source is a production stub; see depth.py for the spike.")
