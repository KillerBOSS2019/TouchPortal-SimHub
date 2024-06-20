from .plugin_categories import PluginCategories
from .EntryHandler import EntryHandler
from re import compile as re_compile


class EntryGenerator:
    def __init__(self):
        self.plugin_id = ""
        self.entry = {}

    # just helper method that adds the key if it doesn't exist, otherwise update the data.
    def update_info(self, func, k, data):
        if hasattr(func, k):
            getattr(func, k).update(data)
        else:
            setattr(func, k, data)  # don't exist, create one

    def return_decorator(self, k, entry):  # actual decorator
        def decorator(func):
            # in here, now I have access to the orginal function and I can modify it however I want.
            self.update_info(func, k, entry)
            return func  # again always return the function back.

        return decorator

    # plugin_info is just a function that allows me to pass argument. decorator is the actual decorator.
    def plugin_info(self, api: int, version: str, name: str, id: str):
        entry = {
            "api": api,
            "version": version,
            "name": name,
            "id": id
        }
        self.plugin_id = id

        # return_decorator is a function that easily allows me to add data without repeating the same code.
        return self.return_decorator("__plugin_info__", entry)

    def create_category(self, id: str, name: str, imagepath: str):
        entry = {
            "id": id,
            "name": name,
            "imagepath": imagepath
        }
        return self.return_decorator("__plugin_categories__", {id: entry})

    def add_start_cmd(self, cmd: str, system: str = ""):
        if system in ["windows", "linux", "mac"]:
            entry = {"plugin_start_cmd_" + system: cmd}
        elif system == "":
            entry = {"plugin_start_cmd": cmd}

        return self.return_decorator("__plugin_info__", entry)

    def add_configuration(self, colorDark: str, colorLight: str, parentCategory: str):
        entry = {
            "configuration": {
                "colorDark": colorDark,
                "colorLight": colorLight,
                "parentCategory": parentCategory
            }
        }

        return self.return_decorator("__plugin_info__", entry)

    def add_action(self, category: str, id: str, name: str, type: str = "communicate", executionType: str = "", execution_cmd: str = ""):
        action = {
            'id': id,
            'name': name,
            'type': type
        }

        if isinstance(category, str) and category != "":
            action['category'] = category

        if isinstance(executionType, str) and executionType != "":
            action['executionType'] = executionType

        if isinstance(execution_cmd, str) and execution_cmd != "":
            action['execution_cmd'] = execution_cmd

        return self.return_decorator("__actions__", action)

    # add_format is just a function that allows me to pass argument. decorator is the actual decorator.
    def add_format(self, language: str, format: str):
        # with the decorator I have the function that I can modify aka adding "__actions__" attribute.
        def decorator(func):
            # if the function doesn't have "__actions__" attribute, add it.
            if "__actions__" not in dir(func):
                # add "__actions__" attribute to the function.
                setattr(func, "__actions__", {})
            # if "lines" is not in the "__actions__" attribute, add it.
            if "lines" not in getattr(func, "__actions__"):
                # add "lines" attribute to the "__actions__" attribute.
                getattr(func, "__actions__").update({"lines": {"action": []}})

            getattr(func, "__actions__")["lines"]["action"].append({  # it gets previous data and append new data.
                "language": language,
                "data": [
                    {
                        "lineFormat": format
                    }
                ]
            })

            # always need to return the func back. This is a modified of the original function with new attribute.
            return func

        return decorator  # returns the decorator

    def add_data(self, id: str, type: str, default: str, valueChoices: list = None, extensions: list = None, allowDecimals: bool = None, minValue: int = None, maxValue: int = None):
        def decorator(func):
            if "__actions__" not in dir(func):
                setattr(func, "__actions__", {})

            if "data" not in getattr(func, "__actions__"):
                getattr(func, "__actions__").update({"data": []})
            # print(func.__actions__)
            if any([id, type, default]) is None:
                raise Exception("id, type, default is required")
            if not (type.lower() in ["text", "number", "switch", "choice"]):
                raise Exception("type must be text, number, switch, choice")

            data_entry = {
                'id': id,
                'type': type.lower(),
                'default': default
            }

            if isinstance(default, str) and default != "":
                data_entry['default'] = default

            if isinstance(valueChoices, list) and type == "choice":
                data_entry['valueChoices'] = valueChoices

            if isinstance(extensions, list):
                data_entry['extensions'] = extensions

            if type == "number":
                if isinstance(allowDecimals, bool):
                    data_entry['allowDecimals'] = allowDecimals

                if isinstance(minValue, int):
                    data_entry['minValue'] = minValue

                if isinstance(maxValue, int):
                    data_entry['maxValue'] = maxValue
            else:
                if (allowDecimals or minValue or maxValue) is not None:
                    raise Exception(
                        "allowDecimals, minValue, maxValue is only for number type")

            getattr(func, "__actions__")["data"].append(data_entry)
            return func

        return decorator

    def add_setting(self, name: str, type: str, maxLength: int = None,
                    isPassword: bool = None, minValue: int = None,
                    maxValue: int = None, readOnly: bool = None, default: str = ""):
        entry = {
            'name': name,
            'type': type
        }

        if isinstance(maxLength, int):
            entry['maxLength'] = maxLength
        
        if isinstance(isPassword, bool):
            entry['isPassword'] = isPassword

        if (maxValue or minValue) and type == "number":
            entry['minValue'] = minValue
            entry['maxValue'] = maxValue
        else:
            if (maxValue or minValue) is not None:
                raise Exception("minValue and maxValue is only for number type")
        
        if isinstance(readOnly, bool):
            entry['readOnly'] = readOnly
        
        if isinstance(default, str):
            entry['default'] = default

        return self.return_decorator("__setting__", entry)
    
    def add_tooltip(self, body:str, title:str = None, docUrl: str = None):
        entry = {
            'body': body
        }

        if isinstance(title, str):
            entry['title'] = title
        if isinstance(docUrl, str):
            entry['docUrl'] = docUrl

        return self.return_decorator("__setting__", {"tooltip": entry})
    
    def create_state(self, id: str, type: str, desc: str, default: str, category: str = None):
        entry = {
            'id': id,
            'type': type,
            'desc': desc,
            'default': default,
            "__state__": True
        }

        if isinstance(category, str):
            entry['parentGroup'] = category

        return entry
            
