"""
Shipping Indices Module

Provides SCFI, CCFI, BDI shipping freight indices
"""

from .models import (
    SCFIIndex, CCFIIndex, BDIIndex,
    init_shipping_indices_database, get_shipping_indices_session
)

# Lazy import to avoid Flask dependency when running scripts
def get_shipping_bp():
    from .api import shipping_bp
    return shipping_bp

__all__ = [
    'SCFIIndex', 'CCFIIndex', 'BDIIndex',
    'init_shipping_indices_database', 'get_shipping_indices_session',
    'get_shipping_bp'
]

