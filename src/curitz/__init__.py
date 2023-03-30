try:
    from .version import version as __version__
except ImportError:
    # calculate version
    # we cannot use importlib_metadata because Ubuntu bionic
    package_name = "curitz"
    __version__ = 'master'  # fallback
    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:  # Python < 3.8
        try:
            import pkg_resources  # type: ignore
        except ImportError:
            pass
        else:
            try:
                __version__ = pkg_resources.get_distribution(package_name).version
            except pkg_resources.DistributionNotFound:
                pass
    else:  # Python 3.8+
        try:
            __version__ = version(package_name)
        except PackageNotFoundError:
            pass
