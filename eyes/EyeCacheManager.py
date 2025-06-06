import numpy as np
from helpers.global_config import EYE_CACHE_PATH
import hashlib
import time


class EyeCacheManager:
    def __init__(self, texture_name="default"):
        self.base_dir = EYE_CACHE_PATH
        self.texture_name = texture_name

        self.pupil_dir = self.base_dir / texture_name / "pupil"
        self.spherical_dir = self.base_dir / texture_name / "spherical"
        self.gaze_dir = self.base_dir / texture_name / "gaze"
        self.lid_mask_dir = self.base_dir / texture_name / "lids"

        self.pupil_dir.mkdir(parents=True, exist_ok=True)
        self.spherical_dir.mkdir(parents=True, exist_ok=True)
        self.gaze_dir.mkdir(parents=True, exist_ok=True)
        self.lid_mask_dir.mkdir(parents=True, exist_ok=True)

        self.pupil_maps = {}
        self.spherical_maps = {}
        self.gaze_cache = {}
        self.lid_mask_cache = {}

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

        if kind == "pupil" and key in self.pupil_maps:
            return self.pupil_maps[key]

        if kind == "spherical" and key in self.spherical_maps:
            return self.spherical_maps[key]

        # Not in memory, attempt to load from disk
        file_path = self._get_path(key_dict, kind)
        if not file_path.exists():
            return None  # If no existing cache, get_or_generate will create a new one

        try:
            if kind == "spherical":
                with np.load(file_path, allow_pickle=True) as data:
                    result = (data["map_x"], data["map_y"])
                    self.spherical_maps[key] = result
                    return result
            else:
                data = np.load(file_path, allow_pickle=True)
                self.pupil_maps[key] = data
                return data
        except Exception:
            try:
                file_path.unlink()
            except:
                pass
            return None

    def exists(self, key_dict, kind="pupil"):
        return self._get_path(key_dict, kind).exists()

    """
        # self.deformer.cache.warm_up_cache(kind="spherical", verbose=False)
        # self.deformer.cache.warm_up_cache(kind="pupil", verbose=False)
        # 10,000 plus cache files, crash pi, bad news, remove until/if we add alternate
        # cache warmup.  will be testing eventually with things like maxfiles
    """    

    def warm_up_cache(self, kind="pupil", verbose=False, max_files=None):
        print(__file__)
        print("Running from", __name__)
        ext = ".npz" if kind == "spherical" else ".npy"
        cache_dir = self.pupil_dir if kind == "pupil" else self.spherical_dir
        log_file = self.base_dir / f"bad_cache_{kind}.log"

        map_dict = self.pupil_maps if kind == "pupil" else self.spherical_maps
        map_dict.clear()

        loaded = 0
        skipped = 0
        deleted = 0
        errors = []

        files = list(cache_dir.glob(f"*{ext}"))
        total_files = len(files)

        if max_files is not None:
            files = files[:max_files]

        if verbose:
            print(f"[Cache Warm-Up] Loading {len(files)} {kind} files into memory (of {total_files} total)...")

        for file in files:
            try:
                key = file.stem

                if ext == ".npy":
                    data = np.load(file)
                    if data is None or not hasattr(data, 'shape'):
                        raise ValueError("Empty or malformed .npy")
                    map_dict[key] = data

                else:
                    with np.load(file) as data:
                        if "map_x" not in data or "map_y" not in data:
                            raise ValueError("Missing keys in .npz")
                        map_dict[key] = (data["map_x"], data["map_y"])

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

        if errors:
            with open(log_file, "a") as log:
                log.write(f"\n[Run at {time.ctime()}] Errors in {kind} cache:\n")
                for e in errors:
                    log.write(f"- {e}\n")

        if verbose:
            print(f"[Cache Warm-Up] Done. Loaded: {loaded}, Deleted: {deleted}, Errors: {len(errors)}")

        return loaded
    