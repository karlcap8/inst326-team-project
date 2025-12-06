class Pipeline:
    def __init__(self, steps):
        self.steps = steps
        self.history = []

    def run(self, df):
        out = df.copy()
        for step in self.steps:
            out = step.apply(out)
            self.history.extend(step.history())
        return out
