class EntryHandler:
    def __init__(self):
        self.entry = {}
        self.plugin_id = ""

    def replace_format(self, line, data_ids):
        for k, v in data_ids.items():
            line = line.replace(f"$[{k}]", "{$" + v + "$}")
        return line

    def process_action(self, action):
        entry = {}
        data_ids = {}

        old_aid = action.get("id")
        action_id = self.plugin_id + "." + action.get("id")
        action["id"] = action_id

        if "data" in action and len(action["data"]) > 0:
            for aid in action["data"]:
                data_ids[aid["id"]] = action_id + "." + aid["id"]
                aid["id"] = data_ids[aid["id"]]
            
            for line_type in action.get("lines", []):
                for lines in action["lines"].get(line_type, []):
                    for line in lines.get("data", []):
                        line["lineFormat"] = self.replace_format(line["lineFormat"], data_ids)
                # onHold as well? not sure

        entry[old_aid] = action
        return entry

    def generate(self, class_instance):
        if not "__plugin_info__" in dir(class_instance):
            raise Exception("No plugin info found")
        
        self.entry["TP_PLUGIN_INFO"] = class_instance.__plugin_info__
        self.plugin_id = self.entry["TP_PLUGIN_INFO"].get("id", "")
        self.entry["TP_PLUGIN_CATEGORIES"] = class_instance.__plugin_categories__

        for func in dir(class_instance):
            func = getattr(class_instance, func)
            if callable(func):
                if "__actions__" in dir(func):
                    data = self.process_action(func.__actions__)
                    if "TP_PLUGIN_ACTIONS" not in self.entry:
                        self.entry["TP_PLUGIN_ACTIONS"] = {}
                    self.entry["TP_PLUGIN_ACTIONS"].update(data)

                elif "__setting__" in dir(func):
                    if "TP_PLUGIN_SETTINGS" not in self.entry:
                        self.entry["TP_PLUGIN_SETTINGS"] = {}
                    self.entry["TP_PLUGIN_SETTINGS"].update({func.__setting__["name"]: func.__setting__})

            elif isinstance(func, dict):
                if "__state__" in func.keys():
                    if "TP_PLUGIN_STATES" not in self.entry:
                        self.entry["TP_PLUGIN_STATES"] = {}
                    del func["__state__"]
                    
                    old_id = func["id"]
                    func["id"] = self.plugin_id + "." + func["id"]
                    self.entry["TP_PLUGIN_STATES"][old_id] = func
        
        return self.entry