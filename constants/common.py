from abc import ABC


TYPED_NONES = {
    str: "",
    dict: {},
    list: []
}

class TrimmableClass(ABC):
    FIELDS = []
    def __init__(self, **kwargs):
        FIELDS = type(self).FIELDS
        # set self attr in kwarg if also in FIELDS
        for k, v in kwargs.items():
            if k in FIELDS and isinstance(v, FIELDS[k]):
                setattr(self, k, v)
    
    # unwrap all info
    def raw(self):
        results = {}
        FIELDS = type(self).FIELDS

        for k, k_type in FIELDS.items():
            # get object value, or a None of an appropriate type if no value is found
            v = getattr(self, k, TYPED_NONES[k_type] if k_type in TYPED_NONES else None)
            # if object value is wrapped, unwrap
            v_type = type(v)
            if issubclass(v_type, TrimmableClass):
                v = v.raw()
        
            results[k] = v
        return results