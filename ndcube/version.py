# This file is for compatibility with astropy_helpers
from pkg_resources import get_distribution, DistributionNotFound
try:
    version = get_distribution("ndcube").version
except DistributionNotFound:
    version = 'unknown.dev'
