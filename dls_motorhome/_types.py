from ._snippets import P_VARIABLE_API


class Group:
    def __init__(self, *axes, plc_number=9):
        self.axes = axes
        self.plc_number = int(plc_number)
        self.code = P_VARIABLE_API

        if (
            self.plc_number < 8  # PLCs 1-8 are reserved
            or self.plc_number > 32  # highest PLC number possible
            or not isinstance(self.plc_number, int)
        ):
            raise ValueError("plc_number should be integer between 9 and 32")

    def __enter__(self):
        pass

    def __exit__(self):
        pass
