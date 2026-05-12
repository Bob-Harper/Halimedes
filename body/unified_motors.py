class UnifiedMotors:
    def __init__(self, base, extended):
        self.base = base
        self.ext = extended

    def __getattr__(self, name):
        # Prefer expressive motions if they exist
        if hasattr(self.ext, name):
            return getattr(self.ext, name)
        # Fall back to raw Picrawler
        return getattr(self.base, name)

    # Conversational hooks expected by ActionExecutor
    def do_idle_fidget(self):
        # pick a small expressive motion
        return self.ext.sway_all_legs()

    def do_expressive_motion(self):
        # pick a medium expressive motion
        return self.ext.wave(speed=50, leg='rf')

    def do_full_body_motion(self):
        # pick a big expressive motion
        return self.ext.stretch_out()
