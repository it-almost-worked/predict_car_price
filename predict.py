import argparse
import json
from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor

def main():
    parser = argparse.ArgumentParser(
        description='car price prediction from csv'
    )
    parser.add_argument('--input', required=True, help='inputed csv')
    parser.add_argument("--output", required=True, help="CSV with predictions")
    args = parser.parse_args()

    model_dir = Path(__file__).resolve().parent / 'models'

    with open(model_dir / 'metadata.json', encoding='utf-8') as file:
        metadata = json.load(file)

    model = CatBoostRegressor()
    model.load_model(str(model_dir / 'catboost.cbm'))

    df = pd.read_csv(args.input)

    missing_columns = [
        col for col in metadata['features'] if col not in df.columns
    ]
    if missing_columns:
        parser.error(f'there are no such colimns in CSV: {missing_columns}')

    X = df[metadata['features']].copy()
    for col in metadata['categorical_features']:
        X[col] = X[col].fillna('unknown').astype(str)

    df['predicted_price'] = model.predict(X)
    df.to_csv(args.output, index=False)

    print(f"Сохранено {len(df)} предсказаний в {args.output}")

if __name__ == '__main__':
    main()