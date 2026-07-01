"""Metrics module — weight-based calculations (no impedance required)."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from homeassistant.helpers.typing import StateType

from ..const import (
    ALGO_OPENSCALE,
    ALGO_SANITAS,
    ALGO_SCIENCE,
    ALGO_XIAOMI,
    CONF_CALCULATION_MODE,
    CONF_GENDER,
    CONF_HEIGHT,
    CONF_IMPEDANCE_MODE,
    IMPEDANCE_MODE_DUAL,
)
from ..models import Gender, Metric
from ..util import check_value_constraints, get_bmr_schofield, to_float


def _is_dual(config: Mapping[str, Any]) -> bool:
    return config.get(CONF_IMPEDANCE_MODE) == IMPEDANCE_MODE_DUAL


def get_bmi(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate BMI — identical in all modes."""
    h = to_float(config.get(CONF_HEIGHT))
    w = to_float(metrics.get(Metric.WEIGHT))

    if h <= 0 or w <= 0:
        return 0.0

    bmi = w / (h / 100.0) ** 2
    return check_value_constraints(bmi, 10, 90)


def get_bmr(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Basal Metabolic Rate (BMR) / TDEE."""
    w = to_float(metrics.get(Metric.WEIGHT))
    h = to_float(config.get(CONF_HEIGHT))
    a = to_float(metrics.get(Metric.AGE))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if h <= 0 or w <= 0 or a <= 0 or gender is None:
        return 0.0

    if mode == ALGO_OPENSCALE:
        # Mifflin-St Jeor formula — BASAL metabolic rate only.
        #
        # BUG FIX: this used to multiply by the activity multiplier, which
        # turns BMR (basal/resting rate) into TDEE (total daily energy
        # expenditure including activity). openScale itself tracks these as
        # two separate metrics (BMR and TDEE) — it never folds activity
        # level into "BMR". That's why this sensor (labelled
        # "basal_metabolism") was reading far higher than expected: at
        # "sedentary" it was already +20% inflated, and up to +90% inflated
        # at "very_active". Removing the multiplier makes this consistent
        # with the Sanitas/Science/Xiaomi modes below, none of which apply
        # an activity multiplier to BMR either.
        if gender == Gender.MALE:
            bmr = (10.0 * w) + (6.25 * h) - (5.0 * a) + 5.0
        else:
            bmr = (10.0 * w) + (6.25 * h) - (5.0 * a) - 161.0

        return check_value_constraints(bmr, 500, 5000)

    # --- SANITAS LOGIC ---
    elif mode == ALGO_SANITAS:
        if gender == Gender.MALE:
            bmr = (10.0 * w) + (6.25 * h) - (5.0 * a) + 5.0
        else:
            bmr = (10.0 * w) + (6.25 * h) - (5.0 * a) - 161.0

    # 1. DUAL MODE (S400)
    elif _is_dual(config):
        lbm = to_float(metrics.get(Metric.LBM))
        bmr = 370 + 21.6 * lbm if lbm > 0 else get_bmr_schofield(w, a, gender)

    # 2. SCIENCE MODE : Schofield (WHO Standard)
    elif mode == ALGO_SCIENCE:
        bmr = get_bmr_schofield(w, a, gender)

    # 3. XIAOMI MODE : Exact Zepp Life formula
    else:
        if gender == Gender.MALE:
            bmr = 877.8 + w * 14.916 - h * 0.726 - a * 8.976
        else:
            bmr = 864.6 + w * 10.2036 - h * 0.39336 - a * 6.204

    return check_value_constraints(bmr, 500, 5000)


def get_visceral_fat(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Visceral Fat Rating."""
    h = to_float(config.get(CONF_HEIGHT))
    w = to_float(metrics.get(Metric.WEIGHT))
    a = to_float(metrics.get(Metric.AGE))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if h <= 0 or w <= 0 or a <= 0 or gender is None:
        return 1.0

    # --- OPENSCALE / SANITAS LOGIC ---
    if mode in (ALGO_OPENSCALE, ALGO_SANITAS):
        bmi = get_bmi(config, metrics)
        if gender == Gender.MALE:
            vfal = (bmi - 20) * 0.7 + (a * 0.1)
        else:
            vfal = (bmi - 20) * 0.6 + (a * 0.1)

        return max(1.0, vfal) # OpenScale floors this to 1.0 minimum

    # Common Zepp Life / Xiaomi standard formula fallback (Xiaomi & Science modes)
    elif gender == Gender.MALE:
        if h < w * 1.6 + 63.0:
            vfal = a * 0.15 + ((w * 305.0) / ((h * 0.0826 * h - h * 0.4) + 48.0) - 2.9)
        else:
            vfal = a * 0.15 + (w * (h * -0.0015 + 0.765) - h * 0.143) - 5.0
    else:
        if w <= h * 0.5 - 13.0:
            vfal = a * 0.07 + (w * (h * -0.0024 + 0.691) - h * 0.027) - 10.5
        else:
            vfal = a * 0.07 + (
                (w * 500.0) / ((h * 1.45 + h * 0.1158 * h) - 120.0) - 6.0
            )

    return check_value_constraints(vfal, 1, 50)