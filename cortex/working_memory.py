class WorkingMemory:
    def __init__(self):
        self.turns = []

    def add(self, speaker, text):
        self.turns.append((speaker, text))
        if len(self.turns) > 5:
            self.turns.pop(0)

    def summarize(self):
        # optional: collapse older turns into a short summary
        pass

    def clear(self):
        self.turns = []
