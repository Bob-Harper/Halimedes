# eyes/cache_manager.py

import time
import numpy as np
from helpers.global_config import EYE_CACHE_PATH
import hashlib

class EyeCacheManager:
    def __init__(self, texture_name="default"):
        self.base_dir = EYE_CACHE_PATH
        self.texture_name = texture_name
        self.pupil_dir = self.base_dir / texture_name / "pupil"
        self.spherical_dir = self.base_dir / texture_name / "spherical"
        self.pupil_dir.mkdir(parents=True, exist_ok=True)
        self.spherical_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, **kwargs):
        key_string = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_path(self, key_dict, kind="pupil"):
        filename = self._generate_key(**key_dict)
        ext = ".npz" if kind == "spherical" else ".npy"
        target_dir = self.spherical_dir if kind == "spherical" else self.pupil_dir
        return target_dir / f"{filename}{ext}"

    def save_map(self, key_dict, data, kind="pupil"):
        path = self._get_path(key_dict, kind)
        if kind == "spherical":
            np.savez_compressed(path, map_x=data[0], map_y=data[1])
        else:
            np.save(path, data)

    def load_map(self, key_dict, kind="pupil"):
        key = self._generate_key(**key_dict)

        if hasattr(self, '_preloaded_maps') and key in self._preloaded_maps:
            print(f"[CacheManager] Used preloaded map for key {key}")
            return self._preloaded_maps[key]
            # Fallback to disk load
        ext = ".npz" if kind == "spherical" else ".npy"
        file_path = (self.pupil_dir if kind == "pupil" else self.spherical_dir) / (key + ext)

        if file_path.exists():
            if kind == "spherical":
                with np.load(file_path) as data:
                    return data["map_x"], data["map_y"]
            else:
                return np.load(file_path)

        return None

    def exists(self, key_dict, kind="pupil"):
        return self._get_path(key_dict, kind).exists()

    def warm_up_cache(self, kind="pupil", verbose=False):
        ext = ".npz" if kind == "spherical" else ".npy"
        cache_dir = self.pupil_dir if kind == "pupil" else self.spherical_dir
        log_file = self.base_dir / f"bad_cache_{kind}.log"

        loaded = 0
        skipped = 0
        deleted = 0
        errors = []

        if verbose:
            print(f"[Cache Warm-Up] Preloading '{kind}' maps from {cache_dir}...")

        for file in cache_dir.glob(f"*{ext}"):
            try:
                if ext == ".npy":
                    data = np.load(file)
                    if data is None or not hasattr(data, 'shape'):
                        raise ValueError("Empty or malformed .npy")
                else:
                    with np.load(file) as data:
                        if "map_x" not in data or "map_y" not in data:
                            raise ValueError("Missing keys in .npz")

                loaded += 1

            except Exception as e:
                error_msg = f"{file.name} - {e}"
                errors.append(error_msg)
                if verbose:
                    print(f"[Cache Warm-Up] Corrupt: {error_msg}")
                try:
                    file.unlink()
                    deleted += 1
                except Exception as del_err:
                    err_msg = f"Failed to delete {file.name} - {del_err}"
                    errors.append(err_msg)
                    if verbose:
                        print(f"[Cache Warm-Up] {err_msg}")
                skipped += 1

        # Write log
        if errors:
            with open(log_file, "a") as log:
                log.write(f"\n[Run at {time.ctime()}] Errors in {kind} cache:\n")
                for e in errors:
                    log.write(f"- {e}\n")

        if verbose:
            print(f"[Cache Warm-Up] Complete. Loaded: {loaded}, Deleted: {deleted}, Errors Logged: {len(errors)}")


        def __getattr__(self, name):
            if name == "texture_cache_dir":
                raise AttributeError("Use pupil_dir or spherical_dir instead of texture_cache_dir.")

    def debug_key(self, **kwargs):
        print(f"[DEBUG] Key: {self._generate_key(**kwargs)}")