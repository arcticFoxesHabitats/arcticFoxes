# Habitat selection of arctic foxes

In this project, we analyze the habitat selection of arctic foxes.

## Requirements:

- pyenv with Python: 3.9.4

### Setup

Use the requirements file in this repo to create a new environment.

```BASH
make setup

#or

pyenv local 3.9.8
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_dev.txt
```

## Data
All data is stored in the data folder.
The gps data of the foxes is stored in the r_files subfolder.
The rasters for the features of the landscape are stored in the Rasters_for_R subfolder.

The steps for data cleaning are described in the data_cleaning [Notebook](notebooks/Data_cleaning.ipynb).

The data cleaning can also be executed via the terminal with
```BASH
make data_clean
```
During this process, shapefiles containing the cleaned data are stored in the data/cleaned_shapefiles folder. This folder needs to be created beforehand.