from jinja2 import Template

# Template design section

TMP_AREA = """{
    "type": "area",
    "site": {
        "area": {
            "name": "{{ Area }}",
            "parentName": "Global"
        }
    }
}"""

TMP_BUILDING = """{
    "type": "building",
    "site": {
        "building": {
            "name": "{{ Building }}",
            "parentName": "Global/{{ Area }}",
            "address": "{{ Address|default("Manchester", true) }}"
        }
    }
}"""

TMP_FLOOR = """{
    "type": "floor",
    "site": {
        "floor": {
            "name": "{{ Floor }}",
            "parentName": "Global/{{ Area }}/{{ Building }}",
            "width": 1000,
            "length": 100,
            "height": 10,
            "rfModel": "Outdoor Open Space",
            "floorIndex": "0"
        }
    }
}"""

# Template creation section

J2_TMP_AREA = Template(TMP_AREA)
J2_TMP_BUILDING = Template(TMP_BUILDING)
J2_TMP_FLOOR = Template(TMP_FLOOR)