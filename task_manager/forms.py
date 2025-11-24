class NoLabelSuffixMixin:
    """Mixin to disable the default colon after form labels."""

    label_suffix = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Django overwrites label_suffix in __init__, so set it back to empty.
        self.label_suffix = ""
