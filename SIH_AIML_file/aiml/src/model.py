from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import joblib
import numpy as np
import pandas as pd
from sklearn.base import RegressorMixin
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.svm import SVR
@dataclass
class ModelReport:
    name: str
    mae: float
    rmse: float
    r2: float
    def to_dict(self) -> dict:
        return {"model": self.name, "MAE": self.mae, "RMSE": self.rmse, "R2": self.r2}
def candidate_models(random_state: int = 42) -> dict[str, RegressorMixin]:
    return {
        # Sanity floor: if nothing beats "always predict the mean
        # dose", the other models aren't actually learning signal yet.
        "baseline_mean": DummyRegressor(strategy="mean"),

        "linear": LinearRegression(),

        # Ridge instead of plain LinearRegression for the polynomial
        # expansion: degree-2 features on ~30 sensor/color features
        # produces hundreds of columns, and with a small sample count
        # unregularized LinearRegression will overfit that badly.
        "ridge": Ridge(alpha=1.0, random_state=random_state),
        "polynomial_2_ridge": make_pipeline(
            PolynomialFeatures(degree=2, include_bias=False),
            StandardScaler(),
            Ridge(alpha=5.0, random_state=random_state),
        ),

        # Depth/leaf-constrained versions of the tree ensembles --
        # unconstrained trees memorize a small training set instead
        # of generalizing.
        "random_forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=6,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05,
            random_state=random_state,
        ),

        "svr": make_pipeline(StandardScaler(), SVR(C=10.0, epsilon=0.1, gamma="scale")),
    }
def evaluate_regressor(model: RegressorMixin, x_test: pd.DataFrame, y_test: Sequence[float], name: str) -> ModelReport:
    prediction = model.predict(x_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, prediction)))
    return ModelReport(name=name, mae=float(mean_absolute_error(y_test, prediction)), rmse=rmse, r2=float(r2_score(y_test, prediction)))
def save_model(
    model: RegressorMixin,
    path: str | Path,
    feature_names: list[str],
    residual_std: float | None = None,
    schema_version: str = "1",
) -> None:
    payload = {
        "model": model,
        "feature_names": feature_names,
        # Test-set residual spread, used by inference.py to turn a
        # raw prediction into a rough, non-calibrated confidence score.
        "residual_std": residual_std,
        "schema_version": schema_version,
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, path)
def load_model(path: str | Path) -> tuple[RegressorMixin, list[str], float | None]:
    payload = joblib.load(path)
    return (
        payload["model"],
        payload["feature_names"],
        payload.get("residual_std"),
    )