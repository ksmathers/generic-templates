class Backend:
    def __init__(self, ctx):
        self.name = "Generic Backend"
        self.ctx = ctx
        self.ctx.with_backend(self)

    def __repr__(self):
        print(f"Backend:{self.name}")