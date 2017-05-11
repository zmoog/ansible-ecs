#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ecs_task_info
short_description: Get information about a task in ecs
description:
    - Get information about a task in ecs.
author: Maurizio Branca(@zmoog)
requirements: [ json, boto, botocore, boto3 ]
options:
    cluster:
        description:
            - The name of the cluster to run the task on
        required: True
    family:
        description:
            - The task definition to start or run
        required: False
extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Simple example of task info
- name: Get task info for the given cluster and family
  ecs_task_info:
    cluster: console-sample-app-static-cluster
    family: task-family
  register: task_output
  
# The family is optional, so you can list all the tasks in a give cluster
- name: Get task info for the given cluster and family
  ecs_task_info:
    cluster: console-sample-app-static-cluster
  register: task_output  
'''

RETURN = '''
taskArns:
    description: a list of ARNs for the Tasks that matches the cluster and family 
    returned: success
    type: list
    sample: [
        "arn:aws:ecs:eu-west-1:731459125315:task/b6a1e01e-e81b-4a7a-937d-7b6939991393"
    ]
'''

try:
    import boto
    import botocore
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import boto3_conn, ec2_argument_spec, get_aws_connection_info


class EcsExecManager:
    """Handles ECS Tasks"""

    def __init__(self, module):
        self.module = module

        try:
            region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
            if not region:
                module.fail_json(msg="Region must be specified as a parameter, in EC2_REGION or AWS_REGION environment variables or in boto configuration file")
            self.ecs = boto3_conn(module, conn_type='client', resource='ecs', region=region, endpoint=ec2_url, **aws_connect_kwargs)
        except boto.exception.NoAuthHandlerFound as e:
            module.fail_json(msg="Can't authorize connection - %s " % str(e))

    def list_tasks(self, cluster_name, service_name):
        filters = dict(cluster=cluster_name)
        if service_name:
            filters['family'] = service_name
        response = self.ecs.list_tasks(**filters)
        return response['taskArns']


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        cluster=dict(required=True, type='str' ), # R S P
        family=dict(required=False, type='str' ) # R* S*
    ))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    # Validate Requirements
    if not HAS_BOTO:
        module.fail_json(msg='boto is required.')

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 is required.')

    service_mgr = EcsExecManager(module)
    existing = service_mgr.list_tasks(module.params['cluster'], module.params['family'])

    results = dict(changed=False)
    results['taskArns'] = existing

    module.exit_json(**results)

if __name__ == '__main__':
    main()
