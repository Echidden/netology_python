import json


def json2xml(json_obj, line_padding=""):
    result_list = list()

    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json2xml(sub_elem, line_padding))

        return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append("%s<%s>" % (line_padding, tag_name))
            result_list.append(json2xml(sub_obj, "\t" + line_padding))
            result_list.append("%s</%s>" % (line_padding, tag_name))

        content = "\n".join(result_list)
        return content
    content = "%s%s" % (line_padding, json_obj)
    return content

if __name__ == '__main__':
    with open('test.json', 'r') as file:
        file_content = file.read()
    print(json2xml(json.loads(file_content)))