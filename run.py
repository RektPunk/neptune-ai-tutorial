from module import (
    NeptuneProjectManager,
    NeptuneExperimentManager,
    NeptuneModelStorageManager,
)

## project init
project_manager = NeptuneProjectManager(
    workspace_name="rektpunk",
    project_name="project-name",
    key="PROJ",
)

## project create
project_manager.create()

## project delete
# project_manager.delete()

## experiment manager
experiment_manager = NeptuneExperimentManager(
    project_manager=project_manager,
)

## log experiment tags
experiment_manager.tags(["experiment1", "tag1"])

## log experiment value
params = {"learning_rate": 0.001, "optimizer": "Adam"}
experiment_manager.log_value("parameters", params)

## log experiment series
for epoch in range(100):
    experiment_manager.log_series(
        name="train",
        metric_name="loss",
        metric_value=0.1**epoch,
    )

## upload experiment files
experiment_manager.upload(
    name="files",
    path=[
        "requirements.txt",
        "README.md",
    ],
)

## stop experiment
experiment_manager.stop()


## init model storage
model_storage = NeptuneModelStorageManager(
    project_manager=project_manager,
    experiment_manager=experiment_manager,
    key="MDL",
)

## log models tags
model_storage.models_tags(["models-tag1", "models-tag2"])

## log model tags
model_storage.model_tags(["model-tag1", "model-tag2"])

## log models info
model_storage.log_models_info(
    name="env",
    params={
        "model": "lightgbm",
    },
)

## log model info
model_storage.log_model_info(
    name="params",
    params={
        "n_trees": 12,
        "frac": 0.5,
    },
)

## log experiment info to model storage
model_storage.log_run_info()

## change stage
model_storage.change_stage("Production")

## stop model storage
model_storage.stop()
