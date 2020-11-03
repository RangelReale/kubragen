from .types import TProvider, TProviderSvc

DEFAULT_KUBERNETES_VERSION = '1.19.0'
"""Default Kubernetes version"""

PROVIDER_GENERIC: TProvider = 'generic'
"""Generic provider"""

PROVIDER_GOOGLE: TProvider = 'google'
"""Google provider"""

PROVIDER_AMAZON: TProvider = 'amazon'
"""Amazon provider"""

PROVIDER_DIGITALOCEAN: TProvider = 'digitalocean'
"""DigitalOcean provider"""

PROVIDER_KIND: TProvider = 'kind'
"""KinD provider"""

PROVIDER_K3D: TProvider = 'k3d'
"""K3D provider"""

PROVIDERSVC_GENERIC: TProviderSvc = 'generic'
"""Generic provider service"""

PROVIDERSVC_GOOGLE_GKE: TProviderSvc = 'google-gke'
"""Google GKE provider service"""

PROVIDERSVC_AMAZON_EKS: TProviderSvc = 'amazon-eks'
"""Amazon EKS provider service"""

PROVIDERSVC_DIGITALOCEAN_KUBERNETES: TProviderSvc = 'digitalocean-kubernetes'
"""DigitalOcean Kubernetes provider service"""
