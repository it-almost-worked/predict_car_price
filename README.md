# Used Car Price Prediction

[Русская версия](README.ru.md)

A tabular regression project comparing a median-price baseline, Ridge regression, and CatBoost to estimate used car listing prices. The project covers data quality checks, model evaluation, error analysis by price segment, and CSV predictions from a saved model.

**Main result:** CatBoost achieved a test MAE of **RUB 183,696**, approximately **20.5% lower than Ridge**.

## Dataset

Source: [Used Cars on Hugging Face](https://huggingface.co/datasets/imbalet/used_cars).

The dataset used in this experiment contains **432,227 rows and 21 columns** and covers the Russian car market. The target is `price`, measured in Russian rubles (RUB). Features include make, model, production year, mileage, region, ownership count, engine specifications, transmission, drive type, trim level, and generation information.

Download `dataset.csv` from the source and save it as **`cars.csv` in the project root**. The download is not performed automatically. Some categorical values, such as Russian region names, remain in their original language.

## Project Files

- `experiment.ipynb` — data inspection, training, evaluation, and model export.
- `predict.py` — command-line predictions using the saved CatBoost model.
- `README.md` — English documentation.
- `README.ru.md` — Russian documentation.

Running the notebook generates:

```text
models/
├── catboost.cbm       # Fitted CatBoost model
└── metadata.json      # Feature order and categorical feature names
cars_example.csv      # Ten sample vehicles without the target
```

The prediction command generates `predictions.csv`.

## Installation

Clone the repository and open its directory. Access to the repository is required if it is private.

```bash
git clone https://github.com/it-almost-worked/predict_car_price.git
cd predict_car_price
```

Install the dependencies into the Python environment you will also use for the notebook kernel:

```bash
python -m pip install -r requirements.txt
```

The saved notebook records Python **3.13.5**. The accompanying `requirements.txt` pins the library versions found in the local Python environment. Installation in a clean environment has not yet been verified.

## Train and Evaluate

1. Save the dataset as `cars.csv` in the project root.
2. Start JupyterLab from the same directory:

   ```bash
   python -m jupyterlab
   ```

3. Open `experiment.ipynb`, select the environment containing the dependencies, and run all cells from top to bottom. Alternatively, run the notebook in VS Code using that environment as the kernel.
4. The final cells save the CatBoost model, feature metadata, and sample input CSV.

Training is implemented in the notebook; a separate training script is not provided.

## Methodology

The data is randomly split into **60% training, 20% validation, and 20% test**, with `random_state=42`.

- **Median baseline:** predicts the training-set median price for every vehicle.
- **Ridge:** numerical median imputation and standardization; categorical imputation with `unknown` and one-hot encoding. Preprocessing and regression are combined in a pipeline fitted on the training set. Model parameters: `alpha=1.0`, `solver="lsqr"`.
- **CatBoost:** missing categorical values are replaced with `unknown` and categories are passed directly to the model. Numerical missing values are handled internally. Parameters: `iterations=1000`, `depth=6`, `learning_rate=0.5`, `loss_function="RMSE"`, and `random_seed=42`. The best iteration is selected using validation MAE, with `early_stopping_rounds=100`.

**MAE** is the mean absolute difference between predicted and observed prices, measured in RUB. Lower is better. The test set is reserved for final evaluation and is not used to select parameters.

No exact duplicate rows were found. Rows with missing feature values were retained; the target had no missing values. Hyperparameter search was not performed.

## Results

| Model | Validation MAE (RUB) | Test MAE (RUB) |
|---|---:|---:|
| Median baseline | 1,049,182 | 1,047,220 |
| Ridge | 228,880 | 230,988 |
| CatBoost | **182,790** | **183,696** |

CatBoost outperformed Ridge in this experiment and was selected for the prediction command. Its best validation result occurred at the final iteration; early stopping was not triggered.

### Validation Errors by Price Segment

Segments are defined using training-set price tertiles, with boundaries of **RUB 739,500** and **RUB 1,676,000**.

| Segment | Vehicles | Baseline MAE (RUB) | Ridge MAE (RUB) | CatBoost MAE (RUB) |
|---|---:|---:|---:|---:|
| Low-price: ≤ 739,500 | 28,837 | 708,497 | 139,269 | **82,843** |
| Mid-price: > 739,500 and ≤ 1,676,000 | 28,641 | 232,227 | 152,258 | **135,881** |
| High-price: > 1,676,000 | 28,967 | 2,196,098 | 393,848 | **328,669** |

CatBoost achieved lower MAE in every segment. Higher absolute errors for expensive vehicles do not, by themselves, establish higher relative errors.

## Predict from a CSV File

After running the notebook, execute from the project root:

```bash
python predict.py --input cars_example.csv --output predictions.csv
```

For your own data, replace the input path:

```bash
python predict.py --input new_cars.csv --output predictions.csv
```

A `models` directory containing `catboost.cbm` and `metadata.json` must be located next to the script. The model directory is resolved relative to `predict.py`; input and output paths are resolved relative to the terminal's current directory unless absolute paths are supplied.

### Input Schema

Each row represents a vehicle. The CSV must contain all 20 training features:

```text
owners, year, region, mileage, mark, model, complectation,
steering_wheel, gear_type, engine, transmission, power,
displacement, characteristics, color, body_type_type,
body_type_name, super_gen_name, super_gen_year_from, super_gen_year_to
```

Use the same units and categorical conventions as the source dataset. Numerical columns must contain numbers or missing values. The `price` column is optional and is not used for prediction. The script checks for missing columns, selects features in the saved order, and applies categorical preprocessing.

### Output

The output CSV retains the input columns and adds **`predicted_price`**, measured in RUB. An existing column with that name is replaced. An existing output file at the supplied path is overwritten.

The notebook includes an optional check comparing script predictions against in-memory predictions for the ten sample vehicles. Run it only after the prediction command has created the output CSV.

## Limitations

- Prices are listing prices, not verified final transaction prices.
- The collection date is insufficiently documented; this experiment does not establish accuracy for current market prices.
- Random splitting does not evaluate future-price performance. No temporal split was performed.
- Exact duplicate checks do not rule out repeated listings with modified attributes.
- These results compare specific configurations, without hyperparameter search; they do not prove universal superiority of one algorithm.
- Dependency versions are pinned, but clean-environment reproduction has not been verified.

This is an educational price-estimation project rather than a deployed valuation service.
