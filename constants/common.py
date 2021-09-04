from abc import ABC


TYPED_NONES = {
    str: "",
    dict: {},
    list: []
}

class TrimmableClass(ABC):
    FIELDS = []
    EMBED_TEMPLATE = {
        "title": {
            "type": str
        },
        "url": {
            "type": str
        }
    }

    def __init__(self, **kwargs):
        fields = type(self).FIELDS
        # set self attr in kwarg if also in FIELDS
        # for k, v in kwargs.items():
        for k, k_specs in fields.items():
            v = kwargs.get(k)
            if k in kwargs and isinstance(v, fields[k].get("type")):
                setattr(self, k, v)
    
    # unwrap all info; use each field's readable_name if raw=False
    def unwrap(self, raw=True):
        results = {}
        fields = type(self).FIELDS

        for k, k_specs in fields.items():
            k_type = k_specs.get("type")
            # get object value, or a None of an appropriate type if no value is found
            v = getattr(self, k, TYPED_NONES[k_type] if k_type in TYPED_NONES else None)
            # if object value is wrapped, unwrap
            v_type = type(v)
            if issubclass(v_type, TrimmableClass):
                v = v.unwrap()
        
            if not raw:
                readable_name = k_specs.get("readable_name")
                results[readable_name] = v
            else:
                results[k] = v
        return results

    def format_for_embed(self, embeds):
        embed_template = type(self).EMBED_TEMPLATE
        for k, v in embeds.items():
            assert( isinstance(v, embed_template.get(k) ) )
            
