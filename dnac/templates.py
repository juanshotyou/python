# This file import the 'jinja2' module and defines all the templates used by the other scripts

import jinja2

site_area_template = """{
    "type": "area",
    "site": {
        "area": {
            "name": "{{site_name}}",
            "parentName": "Global"
        }
    }
}"""

template2 = jinja2.Template(site_area_template)
site_area = template2.render(site_name="test")

{
    "type": "area",
    "site": {
        "area": {
            "name": "TESTURU",
            "parentName": "Global"
        }
    }
}
{
    "type": "building",
    "site": {
        "building": {
            "name": "yololo",
            "parentName": "Global/TESTURU",
            "address": "Manchester"
        }
    }
}

{
    "type": "floor",
    "site": {
        "floor": {
            "name": "Ground-floor",
            "parentName": "Global/TESTURU/yololo",
            "width": 1000,
            "length": 100,
            "height": 10,
            "rfModel": "Outdoor Open Space",
            "floorIndex": "0"
        }
    }
}