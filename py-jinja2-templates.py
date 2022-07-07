from jinja2 import Template, StrictUndefined

print("####### Section 1 #######\n")

template = """hostname {{ hostname }}

{# DNS configuretion, leave domain lookup enabled for NTP pool resolution -#}
ip domain lookup
ip domain name local.lab
ip name-server {{ name_server_1 }}
ip name-server {{ name_server_2 }}

{# Time configuration, should use pools -#}
ntp server {{ ntp_server_1 }} prefer
ntp server {{ ntp_server_2 }} """

data = {
    "hostname": "PYTH-CORE-SW",
    "name_server_1": "10.30.10.250",
    "name_server_2": "8.8.8.8",
    "ntp_server_1": "0.pool.ntp.org",
    "ntp_server_2": "1.pool.ntp.org",
}

j2_template = Template(template, undefined=StrictUndefined)

print(j2_template.render(data),"\n")

#######################################################

print("\n####### Section 2 #######\n")

new_data = {}

for i in range(5):
    new_data["hostname"] = data["hostname"] + "0" + str(i)
    new_data["name_server_1"] = data["name_server_1"]
    new_data["name_server_2"] = data["name_server_2"]
    new_data["ntp_server_1"] = data["ntp_server_1"]
    new_data["ntp_server_2"] = data["ntp_server_2"]
    print(j2_template.render(new_data))

#######################################################

print("\n####### Section 3 #######\n")

interface_data = {
  "interface": {
    "name": "GigabitEthernet1/1",
    "ip_address": "10.0.0.1/31",
    "description": "Uplink to core",
    "speed": "1000",
    "duplex": "full",
    "mtu": "9124"
  }
}

interface_template = '''interface {{ interface.name }}
 description {{ interface.description }}
 ip address {{ interface.ip_address }}
 speed {{ interface.speed }}
 duplex {{ interface.duplex }}
 mtu {{ interface.mtu }}'''

j2_interface_template = Template(interface_template)
print(j2_interface_template.render(interface_data))

########################################################

print("\n####### Section 4 #######\n")

template_strict = "Device {{ name }} is a {{ type }} located in the {{ site }} datacenter."

data_strict = {
    "name": "waw-rtr-core-01",
    "site": "warsaw-01",
    "type": "Router"
}

j2_template_strict = Template(template_strict, undefined=StrictUndefined)

print(j2_template_strict.render(data_strict))

########################################################

print("\n####### Section 5 #######\n")

# Prefix-list template with loop

data_loop = { "prefix_list":
    [
    "permit 10.96.0.0/24",
    "permit 10.97.11.0/24",
    "permit 10.99.15.0/24",
    "permit 10.100.5.0/25",
    "permit 10.100.6.128/25"
    ]
}

prefix_list_template = """
ip prefix-list TEST_LIST_IN
{%- for item in prefix_list %}
 {{ item -}}
{% endfor %}
"""

j2_prefix_list_template = Template(prefix_list_template)
print(j2_prefix_list_template.render(data_loop))

########################################################

print("\n####### Section 6 #######\n")

data_dict = {
    "interfaces": {
        "Ethernet1":{
            "description": "Leaf 1",
            "ipv4_address": "10.0.0.1/24"
        },
        "Ethernet2":{
            "description": "Leaf 2",
            "ipv4_address": "10.0.0.2/24"
        }
    }
}

dictionary_template = """
{% for intf in interfaces -%}
interface {{ intf }}
 description {{ interfaces[intf].description }}
 ip address {{ interfaces[intf].ipv4_address }}
{% endfor %}
"""

dictionary_template_alt = """
{% for iname, idata in interfaces.items() -%}
interface {{ iname }}
 description {{ idata.description }}
 ip address {{ idata.ipv4_address }}
{% endfor %}
"""

j2_template = Template(dictionary_template)
print(j2_template.render(data_dict))

j2_template_alt = Template(dictionary_template_alt)
print(j2_template.render(data_dict))

########################################################

print("\n####### Section 7 #######\n")

data_dict_better = {
    "prefix_lists":{
        "PREF-LIST-1": [
            "permit 10.96.0.0/24",
            "permit 10.97.11.0/24",
            "permit 10.99.15.0/24",
            "permit 10.100.5.0/25",
            "permit 10.100.6.128/25"
        ],
        "PREF-LIST-2": [
            "permit 10.96.0.0/24",
            "permit 10.97.11.0/24",
            "permit 10.99.15.0/24",
            "permit 10.100.5.0/25",
            "permit 10.100.6.128/25"
        ]
    }
}

dictionary_template_better ="""
{% for pl_name, pl_lines in prefix_lists.items() %}
ip prefix-list {{ pl_name }}
{%- for line in pl_lines %}
 {{ line -}}
{%  endfor %}
{% endfor %}
"""

j2_template_better = Template(dictionary_template_better)
print(j2_template_better.render(data_dict_better))

########################################################

print("\n####### Section 8 #######\n")

routing_bgp = {
    "hostname": "router-w-bgp",
    "routing_protocol": "bgp",
    "interfaces":{
        "Loopback0":{ 
            "ip": "10.0.0.1",
            "mask": "32"
            }
        },
    "bgp": {
        "as": "65001"
    }
}

routing_ospf = {
    "hostname": "router-w-ospf",
    "routing_protocol": "ospf",
    "interfaces":{
        "Loopback0":{ 
            "ip": "10.0.0.2",
            "mask": "32"
            }
        },
    "bgp": {
        "pid": "1"
    }
}

routing_defgw = {
    "hostname": "router-w-bgp",
    "routing_protocol": "bgp",
    "interfaces":{
        "Loopback0":{ 
            "ip": "10.0.0.3",
            "mask": "32"
            }
        },
    "default_nh": "10.10.0.1"
    }
}


routing_template = """
hostname {{ hostname }}
ip routing

{% for intf, idata in interfaces.items() -%}
interface {{ intf }}
  ip address {{ idata.ip }}/{{ idata.mask }}
{%- endfor %}

{% if routing_protocol == 'bgp' -%}
router bgp {{ bgp.as }}
  router-id {{ interfaces.Loopback0.ip }}
  network {{ interfaces.Loopback0.ip }}/{{ interfaces.Loopback0.mask }}
{%- elif routing_protocol == 'ospf' -%}
router ospf {{ ospf.pid }}
  router-id {{ interfaces.Loopback0.ip }}
  network {{ interfaces.Loopback0.ip }}/{{ interfaces.Loopback0.mask }} area 0
{%- else -%}
  ip route 0.0.0.0/0 {{ default_nh }}
{%- endif %}
"""

