import re

from .advancedsearchresult import Option


def enumify(text):
    text = re.sub("[ -.]+", "_", text)
    text = re.sub(r"[^a-zA-Z0-9_]+", "", text)
    text = text.strip("_")
    if text.startswith("20th"):
        text = "twentieth" + text[4:]
    return text.lstrip("012345679").upper()


def generate_function_and_enums(tree):
    enums = {}
    all_fields = []
    for section in tree.xpath("//div[@class='clause']"):
        section_title = section.xpath(".//h3/text()")[0]
        if (
            section_title == "Instant Watch Options"
        ):  # bugged and not all that interesting
            continue
        if section_title == "Cast/Crew":  # Skipped for now
            continue
        if section_title == "Display Options":  # sorting option, not part of the form
            continue
        input_fields = section.xpath(".//input")
        input_field_names = section.xpath(".//input/@name")
        select_fields = section.xpath(".//select")
        select_field_names = section.xpath(".//select/@name")
        is_min_max = (
            any(f for f in input_field_names if f.endswith("-min"))
            and any(f for f in input_field_names if f.endswith("-max"))
            or any(f for f in select_field_names if f.endswith("-min"))
            and any(f for f in select_field_names if f.endswith("-max"))
        )
        if len(input_fields) == 1 and len(select_fields) == 0:
            all_fields.append((input_field_names[0], "normal", ""))
        elif len(set(input_field_names)) == 1 and len(select_fields) == 0:
            field_name = input_field_names[0]
            all_fields.append((field_name, "enum", []))
            for e in input_fields:
                label = section.xpath(f".//label[@for='{e.attrib['id']}']")[0]
                if label.text:
                    label = label.text
                else:
                    label = label.xpath(".//*/@title")[0]
                value = e.attrib["value"]
                enums.setdefault(enumify(field_name), {})[enumify(label)] = Option(
                    label, value
                )
        elif len(select_fields) == 1 and len(input_fields) == 0:
            field_name = select_field_names[0]
            all_fields.append((field_name, "enum", []))
            for field in select_fields[0].xpath(".//option"):
                label = field.text
                value = field.attrib["value"]
                enums.setdefault(enumify(field_name), {})[enumify(label)] = Option(
                    label, value
                )
        elif is_min_max:
            if select_field_names:
                field_name = select_field_names[0][:-4]
            else:
                field_name = input_field_names[0][:-4]
            all_fields.append((field_name, "minmax", ("", "")))
        else:
            print("Unknown", section_title, input_fields, select_fields)

    code = []
    code.append("class AS:")
    for k, v in enums.items():
        code.append(f"    class {k}:")
        for label, option in v.items():
            code.append(f"        {label} = {option!r}")
        code.append("")
    code.append("")

    func_args = ", ".join([f"{fn}={v!r}" for (fn, t, v) in all_fields])
    code.append("class AdvancedSearchResult(ParseBase):")
    code.append(f"    def __init__(self, imdb, {func_args}):")
    code.append("        self.imdb = imdb")
    code.append("")
    code.append("        self.query = {}")
    for fn, t, v in all_fields:
        if t == "normal":
            code.append(f"        self.query['{fn}'] = {fn}")
        elif t == "enum":
            code.append(
                f"        self.query['{fn}'] = ','.join([isinstance(v, str) and v or v.value for v in {fn}])"
            )
        elif t == "minmax":
            code.append(f"        self.query['{fn}-min'] = {fn}[0]")
            code.append(f"        self.query['{fn}-max'] = {fn}[1]")

    return "\n".join(code)
