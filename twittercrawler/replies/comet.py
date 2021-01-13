from comet_ml import Experiment
import os, time
import numpy as np

def init_experiment(api_key, project, workspace):
    """Create comet.ml experiment based on provided or pipeline information."""
    # sleep for a few second to handle project creation cuncurrency
    s = np.random.random()*5
    time.sleep(s)
    # create experiment
    experiment = Experiment(
        api_key=api_key,
        project_name=project,
        workspace=workspace,
        log_code=False,
        log_graph=False,
        auto_param_logging=False,
        auto_metric_logging=False,
        auto_output_logging='default',
        log_env_details=False,
        log_git_metadata=True,
        log_git_patch=False,
        disabled=False,
        log_env_gpu=False,
        log_env_host=False,
        log_env_cpu=False,
        display_summary_level=0,  # silent on the console
        auto_weight_logging=False,
    )
    return experiment

def load_api_key(api_key_fp="../comet_key.txt"):
    """Load comet.ml api key from the provided file."""
    if os.path.exists(api_key_fp):
        with open(api_key_fp) as f:
            api_key = f.read().rstrip()
    else:
        print("Comet.ml api key file was not found: %s" % api_key_fp)
        api_key = None
    return api_key