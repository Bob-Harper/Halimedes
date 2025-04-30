# sequencers/eye_behaviours.py

from sequencers.eye_channels import GazeChannel, ExpressionChannel, ActionChannel

class EyeBehaviorManager:
    def __init__(
        self,
        gaze: GazeChannel,
        expr: ExpressionChannel,
        action: ActionChannel,
    ) -> None:
        self.gaze   = gaze
        self.expr   = expr
        self.action = action

    def update(self, dt: float) -> None:
        if self.action.queue:        # VSCode now knows action is ActionChannel
            self.action.update(dt)
            return

        if self.expr.mood:           # VSCode now knows expr is ExpressionChannel
            self.expr.update(dt)
            return

        self.gaze.update(dt)         # and so on…
