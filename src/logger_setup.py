import logging


def setup_logging(log_file, log_level=logging.INFO) -> None:

    # To generate a log file name that includes the date

    # Set up logging format and level
    level_list = [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
        logging.NOTSET
    ]

    if log_level not in level_list:
        raise ValueError(f"Invalid log level: {log_level}. Valid levels are as follows: {level_list}")


    logging.basicConfig(
        # Set the logging level
        level=log_level,
        # Log format
        # format='%(asctime)s - %(levelname)s - %(message)s',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line: %(lineno)d',
        # format='%(levelname)s - %(message)s',
        handlers=[
            # NOTE: Create a file handler to log to console only
            # logging.StreamHandler(),  
            # NOTE: Create a file handler to log to a file and console
            logging.FileHandler(log_file, encoding='utf-8')  # Log to file
        ]
    )
