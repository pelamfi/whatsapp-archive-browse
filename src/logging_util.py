import logging

TRACE_LEVEL = 5  # Custom level below DEBUG


def setup_logging(verbose: int) -> None:
    """
    Set up logging configuration based on verbosity level.

    Args:
        verbosity: Verbosity level (0-3)
    """
    # Set up logging based on verbosity
    log_level: int

    log_levels: list[int] = [
        logging.ERROR,  # 0 (quiet)
        logging.INFO,  # 1 (default)
        logging.DEBUG,  # 2
        TRACE_LEVEL,  # 3 (trace level)
    ]
    level_index: int = min(verbose, len(log_levels) - 1)
    log_level = log_levels[level_index]

    # Register our custom level name
    if not hasattr(logging, "TRACE"):
        logging.addLevelName(TRACE_LEVEL, "TRACE")

    # Configure root logger
    logging.basicConfig(level=logging.NOTSET, format="%(levelname)s: %(message)s")  # Reset first
    logging.getLogger().setLevel(log_level)
    logging.getLogger().setLevel(log_level)
