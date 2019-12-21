from mediama import PreProcess


class Metadata(PreProcess):
    """
    Allows the user to set metadata
    """
    def main(self, **kwargs):
        for key, value in kwargs:
            self.metadata[key] = value
