# KubraGen: programmatic Kubernetes YAML generator

[![PyPI version](https://img.shields.io/pypi/v/kubragen.svg)](https://pypi.python.org/pypi/kubragen/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/kubragen.svg)](https://pypi.python.org/pypi/kubragen/)

## Overview

KubraGen is a Kubernetes YAML generator library that makes it possible to generate
configurations using the full power of the Python programming language.

Using plugins (called Builders), it is possible to include libraries that know how to configure
specific services, like Prometheus, RabbitMQ, Traefik, etc.

The *jsonpatchext* library (an extension of *jsonpatch*) is used to make it possible to check and modify the output
objects in any way without accessing the returned dicts directly, including merging dicts with the *deepmerge* 
library.

See source code for examples

* Website: https://github.com/RangelReale/kubragen
* Repository: https://github.com/RangelReale/kubragen.git
* Documentation: https://kubragen.readthedocs.org/
* PyPI: https://pypi.python.org/pypi/kubragen

### Builders

* RabbitMQ: [kg_rabbitmq](https://github.com/RangelReale/kg_rabbitmq)
* Traefik 2: [kg_traefik2](https://github.com/RangelReale/kg_traefik2)
* Keycloak: [kg_keycloak](https://github.com/RangelReale/kg_keycloak)
* Ingress NGINX: [kg_ingressnginx](https://github.com/RangelReale/kg_ingressnginx)
* Prometheus: [kg_prometheus](https://github.com/RangelReale/kg_prometheus)
* Grafana: [kg_grafana](https://github.com/RangelReale/kg_grafana)
* Node Exporter: [kg_nodeexporter](https://github.com/RangelReale/kg_nodeexporter)
* Kube State Metrics: [kg_kubestatemetrics](https://github.com/RangelReale/kg_kubestatemetrics)
* RabbitMQ (Online YAML download): [kg_rabbitmqonline](https://github.com/RangelReale/kg_rabbitmqonline)
* Prometheus Stack (Prometheus, Grafana, Node Exporter, Kube State Metrics): [kg_prometheusstack](https://github.com/RangelReale/kg_prometheusstack)


## Example

This example is purposeful convoluted to illustrate the many features of the library.

```python
from kubragen import KubraGen
from kubragen.consts import PROVIDER_GOOGLE, PROVIDERSVC_GOOGLE_GKE
from kubragen.data import ValueData
from kubragen.helper import QuotedStr
from kubragen.jsonpatch import FilterJSONPatches_Apply, FilterJSONPatch, ObjectFilter
from kubragen.kdata import KData_Secret
from kubragen.object import Object
from kubragen.option import OptionRoot
from kubragen.options import Options
from kubragen.output import OutputProject, OD_FileTemplate
from kubragen.outputimpl import OutputFile_ShellScript, OutputFile_Kubernetes, OutputDriver_Print
from kubragen.provider import Provider

from kg_rabbitmq import RabbitMQBuilder, RabbitMQOptions

kg = KubraGen(provider=Provider(PROVIDER_GOOGLE, PROVIDERSVC_GOOGLE_GKE), options=Options({
    'namespaces': {
        'default': 'app-default',
        'monitoring': 'app-monitoring',
    },
}))

out = OutputProject(kg)

shell_script = OutputFile_ShellScript('create_gke.sh')
out.append(shell_script)

shell_script.append('set -e')

#
# OUTPUTFILE: app-namespace.yaml
#
file = OutputFile_Kubernetes('app-namespace.yaml')
out.append(file)

file.append(FilterJSONPatches_Apply([
    Object({
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': 'app-default',
            'annotations': {
                'will-not-output': ValueData(value='anything', enabled=False),
            }
        },
    }, name='ns-default', source='app'), Object({
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': 'app-monitoring',
        },
    }, name='ns-monitoring', source='app'),
], jsonpatches=[
    FilterJSONPatch(filters=ObjectFilter(names=['ns-monitoring']), patches=[
        {'op': 'add', 'path': '/metadata/annotations', 'value': {
                'kubragen.github.io/patches': QuotedStr('true'),
        }},
    ])
]))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

shell_script.append(f'kubectl config set-context --current --namespace=app-default')

#
# SETUP: rabbitmq
#
rabbitmq_config = RabbitMQBuilder(kubragen=kg, options=RabbitMQOptions({
    'namespace': OptionRoot('namespaces.monitoring'),
    'basename': 'myrabbit',
    'config': {
        'erlang_cookie': KData_Secret(secretName='app-global-secrets', secretData='erlang_cookie'),
        'enable_prometheus': True,
        'prometheus_annotation': True,
        'authorization': {
            'serviceaccount_create': True,
            'roles_create': True,
            'roles_bind': True,
        },
    },
    'kubernetes': {
        'volumes': {
            'data': {
                'persistentVolumeClaim': {
                    'claimName': 'rabbitmq-storage-claim'
                }
            }
        },
        'resources': {
            'statefulset': {
                'requests': {
                    'cpu': '150m',
                    'memory': '300Mi'
                },
                'limits': {
                    'cpu': '300m',
                    'memory': '450Mi'
                },
            },
        },
    }
})).jsonpatches([
    FilterJSONPatch(filters={'names': [RabbitMQBuilder.BUILDITEM_SERVICE]}, patches=[
        {'op': 'check', 'path': '/spec/ports/0/name', 'cmp': 'equals', 'value': 'http'},
        {'op': 'replace', 'path': '/spec/type', 'value': 'LoadBalancer'},
    ]),
])

rabbitmq_config.ensure_build_names(rabbitmq_config.BUILD_ACCESSCONTROL, rabbitmq_config.BUILD_CONFIG,
                                   rabbitmq_config.BUILD_SERVICE)

#
# OUTPUTFILE: rabbitmq-config.yaml
#
file = OutputFile_Kubernetes('rabbitmq-config.yaml')
out.append(file)

file.append(rabbitmq_config.build(rabbitmq_config.BUILD_ACCESSCONTROL, rabbitmq_config.BUILD_CONFIG))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

#
# OUTPUTFILE: rabbitmq.yaml
#
file = OutputFile_Kubernetes('rabbitmq.yaml')
out.append(file)

file.append(rabbitmq_config.build(rabbitmq_config.BUILD_SERVICE))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

#
# OUTPUT
#
out.output(OutputDriver_Print())
# out.output(OutputDriver_Directory('/tmp/app-gke'))
```

Output:

```text
****** BEGIN FILE: 001-app-namespace.yaml ********
apiVersion: v1
kind: Namespace
metadata:
  name: app-default
  annotations: {}
---
apiVersion: v1
kind: Namespace
metadata:
  name: app-monitoring
  annotations:
    kubragen.github.io/patches: 'true'

****** END FILE: 001-app-namespace.yaml ********
****** BEGIN FILE: 002-rabbitmq-config.yaml ********
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myrabbit
  namespace: app-monitoring
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1beta1
<...more...>
****** END FILE: 002-rabbitmq-config.yaml ********
****** BEGIN FILE: 003-rabbitmq.yaml ********
apiVersion: v1
kind: Service
metadata:
  name: myrabbit-headless
  namespace: app-monitoring
spec:
  clusterIP: None
<...more...>
****** END FILE: 003-rabbitmq.yaml ********
****** BEGIN FILE: create_gke.sh ********
#!/bin/bash

set -e
kubectl apply -f 001-app-namespace.yaml
kubectl config set-context --current --namespace=app-default
kubectl apply -f 002-rabbitmq-config.yaml
kubectl apply -f 003-rabbitmq.yaml

****** END FILE: create_gke.sh ********
```

## Design Philosophy

* As the generated Kubernetes files can have critical consequences, the library is designed to fail on the minimal
possibility of error, and also gives tools to users of the library to check any generated value for critical
options, using the *jsonpatchext* library to check the data output by the builders.

* To minimize the use of dict concatenation, a special type *kubragen.data.Data* can be used anywhere in the object,
and it has a *is_enabled()* method that removes the value (and its key if it is contained in a dict/list)
if it returns False.

* Only YAML is supported by the library, it is not possible to generate JSON directly at the moment.

## Author

Rangel Reale (rangelspam@gmail.com)
