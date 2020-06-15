class Group:
    def __init__(self, *axes, plc_number=9):
        self.axes = axes
        self.plc_number = int(plc_number)

        if self.plc_number < 8 or self.plc_number > 32:
            raise ValueError("plc_number should be integer between 9 and 32")

    def __enter__(self):
        pass

    def __exit__(self):
        pass
