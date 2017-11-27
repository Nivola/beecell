'''
Created on Nov 27, 2017

@author: darkbk
'''
from beecell.simple import compat
params = {u'ext_id': None, u'parent': 613, u'availability_zone': u'nova',
          u'attribute': {}, u'flavorRef': u'm1.medium',
          u'user_data': u'I2Nsb3VkLWNvbmZpZwpib290Y21kOgogIC0gWyBpcCwgcm91dGUsIGNoYW5nZSwgZGVmYXVsdCwgdmlhLCAxMC4xMDIuMTg0LjEgXQpjaHBhc3N3ZDoKICBsaXN0OiB8CiAgICByb290Om15cGFzcwogIGV4cGlyZTogRmFsc2UKc3NoX2F1dGhvcml6ZWRfa2V5czoKICAtIHNzaC1yc2EgQUFBQUIzTnphQzF5YzJFQUFBQURBUUFCQUFBQ0FRRHBOMzZSTWpCTnBROWxUdmJkTWpia1U2T3l5dFg3OFJYS2lWTk1CVTA3dkJ4NlJFd0dXZ3l0Zys4ckcxcHFGQXVvNlUzbFIxcTI1ZHBQRFF0SzhEYWQ2OE1QSEZ5ZGZ2MFdBWU9HNlkwMmovcFFLSkRHUGhiZVNZUzBYRjRGL3o0VXhZNmNYQjhVZHprVVNLdElnOTNZQ1RremJRWTYrQVBPWS9LOXExYjJaeFRFRUJEUWdXZW5adzRNY21TYmFTK0FZd21pZ1NKYjVzRk1leEpSS1pDZFhFU2dRY1NtVWtRRmlYUlFOSk1sZ1BaQm5JY2JHbHU1VUE5RzVvd0xNNkxUMTFiUFFQclJPcW1oY1NHb1F0WXE4M1JHTlg1S2d3ZTAwcHFlby9HK1NVdGNRUnA1SnRXSUU5YkxlYVhSSWhadUlucmJQMHJtSHlDUWhCZVpEQ1ByMW13MllEWlY5RmJiMDgvcXdicTFVWXVVelJYeFhyb1gxRjcvbXp0eVhRdDdvNEFqWFdwZXlCY2NSMG5rQXlaY2FuT3Z2Skp2b0l3TG9EcWJzWmFxQ2xkUUpDdnRiMVdOWDl1a2NlNVRvVzF5ODBSY2YxR1pyclhSVHMyY0FidWJVa3hZUWFMUVFBcFZuR0lKZWxSOUJsdlI3eHNtZlE1WTV3b2RlTGZFZ3F3MmhOekpFZUtLSHM1eG5wY2dHOWlYVnZXMVRyMEdmK1VzWTBVSW9nWjZCQ3N0ZlI1OWxQQXQxSVJhWVZDdmdIc0htNGhtcjB5TXZVd0dIcm96dHJqYTUwWEhwOWgwei9FV0F0NTZuaW9PSmNPVGxvQUlwQUkwNXo0Wjk4NWJZV2dGazhqLzFMa0VES0g5YnVxNW1ITHdONjlPN0pQTjhYYUR4QnE5eHFTUDl3PT0gc2VyZ2lvLnRvbmFuaUBjc2kuaXQ=', 
          u'user': u'admin@local', u'active': False, u'flavor': '3', 
          u'server': u'158.102.160.234', 
          'networks': [{'fixed_ip': {'gw': u'10.102.184.1'}, 'uuid': '68a34356-7395-4d63-95bc-4d2ff2b31d74'}], 
          'security_groups': [u'test-sg-01'], u'desc': u'test-server-01', 
          u'name': u'test-server-01', 'imageRef': u'centos7-heat', 
          'adminPass': u'mypass', 
          'block_device_mapping_v2': [{'source_type': u'volume', 'volume_size': 20, 'destination_type': u'volume'}], 
          u'cid': 2, u'uuid': '2e9ce2d9-68da-4492-8e8f-6a093c2b2e6f', 
          u'id': 734, u'tags': u'', 
          u'objid': u'07dbe93be27f1660f64b//534a381ec1d137def0e0//4ad2ef8a435973c46ad7//fb2c5cfff32f6e49111c', 
          u'identity': u'014a042d-dbc2-4b1a-a42c-aa4491b66b47', 
          'metadata': [], u'image': '1790e1fd-61fc-400e-9c0e-4e9584f16678', 
          'personality': []}

print(compat(params))
print(len(str(compat(params))))
