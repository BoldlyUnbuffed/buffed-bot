print('ERRORS.PY RAN')

class GameNotFoundError(RuntimeError):
    def __init__(self, game, suggestion=None):
        super().__init__()
        self.suggestion = suggestion
        self.game = game

    def __str__(self):
        s = f'"{self.game}" not found.'
        if self.suggestion is not None:
            s += f' Did you mean "{self.suggestion}"?'
        return s

class ElementNotFoundError(RuntimeError):
    pass

class AttributeNotFoundError(RuntimeError):
    pass
