import sys

this = sys.modules[__name__]

this.provider_name = None


def init_provider(provider):
    if this.provider_name is None:
        this.provider_name = provider
    else:
        msg = "Provider sudah diset {0}"
        raise RuntimeError(msg.format(this.provider_name))
