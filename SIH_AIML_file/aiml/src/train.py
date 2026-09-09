from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import (
    GroupKFold,
    GroupShuffleSplit,
    KFold,
    train_test_split,
)

try:
    from .config import MODEL_SCHEMA_VERSION
    from .model import candidate_models, evaluate_regressor, save_model
except ImportError:
    from config import MODEL_SCHEMA_VERSION
    from model import candidate_models, evaluate_regressor, save_model



META_COLUMNS = {
    "image_id",
    "image_path",
    "dose_ppmh",

    "concentration_ppm",
    "exposure_hours",
    "temperature",
    "RH",

    
    "phone",
    "lighting",

    "batch",
    "capture_session",
    "badge_id",

    
    "notes",
}


MIN_RELIABLE_SAMPLES = 30


def prepare_xy(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepare ML input features X and target y.

    Target:
        dose_ppmh

    X:
        Numeric image/color/environment features only.
    """

    if "dose_ppmh" not in df.columns:
        raise ValueError(
            "features.csv must contain the target column 'dose_ppmh'."
        )

    # Select only columns that are not metadata
    feature_columns = [
        column
        for column in df.columns
        if column not in META_COLUMNS
    ]

    if not feature_columns:
        raise ValueError(
            "No ML feature columns found in features.csv."
        )

    # Convert all selected features to numeric
    x = df[feature_columns].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Replace missing feature values
    x = x.replace([float("inf"), float("-inf")], pd.NA)
    x = x.fillna(0.0)

    # Target
    y = pd.to_numeric(
        df["dose_ppmh"],
        errors="coerce"
    )

    # Keep only rows with valid target
    valid = y.notna()

    x = x.loc[valid]
    y = y.loc[valid]

    if len(x) < 5:
        raise ValueError(
            f"Only {len(x)} valid training rows found. "
            "You need more labelled samples before training."
        )

    print("\n========== DATASET INFORMATION ==========")
    print(f"Total valid samples : {len(x)}")
    print(f"Number of features  : {len(x.columns)}")

    if len(x) < MIN_RELIABLE_SAMPLES:
        print(
            f"\nWARNING: only {len(x)} labelled samples available "
            f"(recommend >= {MIN_RELIABLE_SAMPLES}). Model comparison "
            "results below may be noisy -- treat rankings as directional, "
            "not definitive, and collect more badge photos where possible."
        )

    if len(x.columns) > max(len(x) // 2, 1):
        print(
            f"\nWARNING: {len(x.columns)} features for only {len(x)} samples. "
            "This is a high feature-to-sample ratio and increases overfitting "
            "risk, especially for the polynomial and tree-based models."
        )

    print("\nML FEATURES:")
    for feature in x.columns:
        print(f"  - {feature}")

    print("\nTARGET:")
    print("  dose_ppmh")

    return x, y


def split_data(
    df: pd.DataFrame,
    x: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.20,
    random_state: int = 42,
):
    """
    Split data while trying to prevent data leakage.

    Priority:
        1. capture_session
        2. badge_id
        3. batch
        4. random split
    """

    group_column = None

    for column in (
        "capture_session",
        "badge_id",
        "batch",
    ):
        if (
            column in df.columns
            and df.loc[y.index, column].notna().any()
        ):
            group_column = column
            break

    if group_column is not None:

        groups = (
            df.loc[y.index, group_column]
            .fillna(df.loc[y.index, "image_id"])
            .astype(str)
        )

        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=test_size,
            random_state=random_state,
        )

        train_idx, test_idx = next(
            splitter.split(
                x,
                y,
                groups=groups,
            )
        )

        print("\n========== DATA SPLIT ==========")
        print(f"Split method : GroupShuffleSplit")
        print(f"Group column : {group_column}")
        print(f"Training     : {len(train_idx)}")
        print(f"Testing      : {len(test_idx)}")

        return (
            x.iloc[train_idx],
            x.iloc[test_idx],
            y.iloc[train_idx],
            y.iloc[test_idx],
            f"group:{group_column}",
            group_column,
        )

    # Fallback if grouping information is unavailable
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=random_state,
    )

    print("\n========== DATA SPLIT ==========")
    print("Split method : Random train-test split")
    print(f"Training     : {len(x_train)}")
    print(f"Testing      : {len(x_test)}")

    return (
        x_train,
        x_test,
        y_train,
        y_test,
        "random",
        None,
    )


def cross_validate_models(
    df: pd.DataFrame,
    x: pd.DataFrame,
    y: pd.Series,
    models: dict,
    group_column: str | None,
    n_splits: int = 5,
    random_state: int = 42,
) -> dict[str, dict[str, float]]:
    

    n_samples = len(x)

    if group_column is not None:
        groups = (
            df.loc[y.index, group_column]
            .fillna(df.loc[y.index, "image_id"])
            .astype(str)
        )
        n_groups = groups.nunique()
        effective_splits = min(n_splits, n_groups)

        if effective_splits < 2:
            print(
                "\nSkipping cross-validation: not enough distinct "
                f"'{group_column}' groups ({n_groups}) to form folds."
            )
            return {}

        splitter = GroupKFold(n_splits=effective_splits)
        folds = list(splitter.split(x, y, groups=groups))

    else:
        effective_splits = min(n_splits, n_samples)

        if effective_splits < 2:
            print("\nSkipping cross-validation: not enough samples to form folds.")
            return {}

        splitter = KFold(
            n_splits=effective_splits,
            shuffle=True,
            random_state=random_state,
        )
        folds = list(splitter.split(x, y))

    print("\n========== CROSS-VALIDATION ==========")
    print(f"Folds        : {effective_splits}")
    print(f"Group column : {group_column or 'none (random KFold)'}")

    results: dict[str, dict[str, float]] = {}

    for name, estimator in models.items():

        fold_mae = []
        fold_rmse = []

        for train_idx, val_idx in folds:
            try:
                model = clone(estimator)
                model.fit(x.iloc[train_idx], y.iloc[train_idx])
                pred = model.predict(x.iloc[val_idx])
                fold_mae.append(
                    mean_absolute_error(y.iloc[val_idx], pred)
                )
                fold_rmse.append(
                    float(np.sqrt(mean_squared_error(y.iloc[val_idx], pred)))
                )
            except Exception as exc:
                print(f"  {name}: fold failed ({type(exc).__name__}: {exc})")

        if not fold_mae:
            continue

        results[name] = {
            "cv_mae_mean": float(np.mean(fold_mae)),
            "cv_mae_std": float(np.std(fold_mae)),
            "cv_rmse_mean": float(np.mean(fold_rmse)),
            "cv_rmse_std": float(np.std(fold_rmse)),
        }

        print(
            f"  {name:<20s} "
            f"CV RMSE: {results[name]['cv_rmse_mean']:.4f} "
            f"(+/- {results[name]['cv_rmse_std']:.4f})  "
            f"CV MAE: {results[name]['cv_mae_mean']:.4f}"
        )

    return results


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Train and compare AIML regression models "
            "for cumulative H2S dose estimation."
        )
    )

    parser.add_argument(
        "--features",
        required=True,
        help="Path to processed features CSV.",
    )

    parser.add_argument(
        "--model-out",
        default="models/dose_model.joblib",
        help="Output path for best trained model.",
    )

    parser.add_argument(
        "--metrics-out",
        default="results/model_metrics.csv",
        help="Output path for model evaluation metrics.",
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # 1. Load feature dataset
    # --------------------------------------------------

    features_path = Path(args.features)

    if not features_path.exists():
        raise FileNotFoundError(
            f"Features file not found: {features_path}"
        )

    print("\n==========================================")
    print("       H2S DOSIMETER AIML TRAINING")
    print("==========================================")

    print(f"\nLoading dataset:")
    print(features_path)

    df = pd.read_csv(features_path)

    if df.empty:
        raise ValueError(
            "features.csv is empty. "
            "Run build_features.py first."
        )

    print(f"Dataset shape: {df.shape}")

    # --------------------------------------------------
    # 2. Prepare X and y
    # --------------------------------------------------

    x, y = prepare_xy(df)

    # --------------------------------------------------
    # 3. Train-test split
    # --------------------------------------------------

    (
        x_train,
        x_test,
        y_train,
        y_test,
        split_method,
        group_column,
    ) = split_data(
        df,
        x,
        y,
    )

    # --------------------------------------------------
    # 4. Create candidate models
    # --------------------------------------------------

    models = candidate_models()

    print("\n========== MODELS ==========")

    for name in models:
        print(f"  - {name}")

    # --------------------------------------------------
    # 4b. Cross-validate on the full dataset for a more
    #     reliable ranking than a single train/test split
    #     can give on a small sample size.
    # --------------------------------------------------

    cv_results = cross_validate_models(
        df,
        x,
        y,
        models,
        group_column,
    )

    # --------------------------------------------------
    # 5. Train and evaluate every model on the held-out
    #    split, for an honest, unbiased final report.
    # --------------------------------------------------

    reports = []
    fitted_models = {}

    for name, estimator in models.items():

        print("\n------------------------------------------")
        print(f"Training model: {name}")
        print("------------------------------------------")

        try:

            # Train
            estimator.fit(
                x_train,
                y_train,
            )

            # Save fitted estimator temporarily
            fitted_models[name] = estimator

            # Evaluate
            report = evaluate_regressor(
                estimator,
                x_test,
                y_test,
                name,
            )

            report_dict = report.to_dict()

            # Add split information
            report_dict["split"] = split_method

            # Attach cross-validation numbers (if available) so the
            # comparison table shows both the CV-based ranking signal
            # and the honest holdout numbers side by side.
            if name in cv_results:
                report_dict.update(cv_results[name])

            reports.append(report_dict)

            print(f"MAE : {report.mae:.4f}")
            print(f"RMSE: {report.rmse:.4f}")
            print(f"R²  : {report.r2:.4f}")

        except Exception as exc:

            print(
                f"WARNING: {name} failed: "
                f"{type(exc).__name__}: {exc}"
            )

    if not reports:
        raise RuntimeError(
            "All models failed during training."
        )

    # --------------------------------------------------
    # 6. Compare models
    # --------------------------------------------------

    metrics = pd.DataFrame(reports)

    # Prefer ranking by cross-validated RMSE when it's available --
    # it's a more reliable signal than a single holdout split,
    # especially with a small number of samples. Fall back to the
    # holdout RMSE/MAE if CV was skipped (e.g. too few groups).
    if "cv_rmse_mean" in metrics.columns and metrics["cv_rmse_mean"].notna().any():
        sort_columns = ["cv_rmse_mean", "cv_mae_mean"]
    else:
        sort_columns = ["RMSE", "MAE"]

    metrics = metrics.sort_values(
        by=sort_columns,
        ascending=True,
    )

    print("\n==========================================")
    print("          MODEL COMPARISON")
    print("==========================================")

    print(
        metrics.to_string(
            index=False
        )
    )

    # --------------------------------------------------
    # 7. Select best model
    # --------------------------------------------------

    best_name = str(
        metrics.iloc[0]["model"]
    )

    best_model = fitted_models[best_name]

    # Residual spread on the held-out test set, computed BEFORE we
    # touch the model again. inference.py's confidence field is
    # currently always None because nothing produces this number --
    # this is what lets predict_dose() report an actual confidence.
    test_predictions = best_model.predict(x_test)
    residual_std = float(
        np.std(np.asarray(y_test) - np.asarray(test_predictions))
    )

    print("\n==========================================")
    print("             BEST MODEL")
    print("==========================================")

    print(f"Selected model     : {best_name}")
    print(f"Test residual std  : {residual_std:.4f} ppm.h")

    if best_name == "baseline_mean":
        print(
            "\nWARNING: the mean-only baseline won. None of the trained "
            "models beat 'always predict the average dose' -- this "
            "usually means there isn't enough signal yet in the current "
            "features/dataset. More labelled images, or richer features, "
            "are likely needed before the estimator is meaningful."
        )

    # --------------------------------------------------
    # 7b. Refit the winning model on ALL labelled data
    #     (train + test) before saving. With a small,
    #     hard-won dataset, permanently discarding the test
    #     split after evaluation wastes real samples -- the
    #     holdout metrics above already give an honest sense
    #     of accuracy, so it's safe to fold the test rows
    #     back in for the model that actually ships.
    # --------------------------------------------------

    deployable_model = clone(best_model)
    deployable_model.fit(x, y)

    # --------------------------------------------------
    # 8. Save metrics
    # --------------------------------------------------

    metrics_path = Path(
        args.metrics_out
    )

    metrics_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics.to_csv(
        metrics_path,
        index=False,
    )

    print(
        f"\nMetrics saved to:"
        f"\n{metrics_path}"
    )

    # --------------------------------------------------
    # 9. Save best model
    # --------------------------------------------------

    model_path = Path(
        args.model_out
    )

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_model(
        deployable_model,
        model_path,
        list(x.columns),
        residual_std=residual_std,
        schema_version=MODEL_SCHEMA_VERSION,
    )

    print(
        f"Best model saved to:"
        f"\n{model_path}"
    )

    # --------------------------------------------------
    # 10. Final summary
    # --------------------------------------------------

    best_row = metrics.iloc[0]

    print("\n==========================================")
    print("             TRAINING COMPLETE")
    print("==========================================")

    print(f"Best model : {best_name}")
    print(f"MAE        : {best_row['MAE']:.4f}")
    print(f"RMSE       : {best_row['RMSE']:.4f}")
    print(f"R²         : {best_row['R2']:.4f}")

    print("\nOutput files:")
    print(f"  Model   : {model_path}")
    print(f"  Metrics : {metrics_path}")

    print("\nTarget:")
    print("  Estimated cumulative H2S dose (ppm·h)")


if __name__ == "__main__":
    main()
    