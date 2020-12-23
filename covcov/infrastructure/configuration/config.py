# __all__ = ["config"]
#
# import os
# import yaml
# import logging
#
# ENVIRONMENT = os.getenv("COVCOV_CONFIG_PATH")
# print("CONFIG - **ENVIRONMENT**")
#
#
# # 1 - Locate 'config_file_path'
# if ENVIRONMENT:
#     config_file_path = ENVIRONMENT
# else:
#     this_dir = os.path.dirname(os.path.realpath(__file__))
#     config_file_path = os.path.join(this_dir, "config.yml")
#
# # 2 - Load config values
# with open(config_file_path, 'r') as file_in:
#     config = yaml.safe_load(file_in)
#
# # 3 - Set logging parameters
# logging.basicConfig(level=config['logging']['level'], format=config['logging']['format'])