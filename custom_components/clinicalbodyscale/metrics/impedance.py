"""Metrics module — impedance-based calculations."""

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
    CONF_CLINICAL_BODY_SCALE,
    IMPEDANCE_MODE_DUAL,
)
from ..models import Gender, Metric
from ..util import (
    check_value_constraints,
    clamp_water_percentage,
    get_metabolic_age_clamped,
    to_float,
)

# ─────────────────────────────────────────────────────────────────────────────
# HARDWARE IMPEDANCE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _is_dual(config: Mapping[str, Any]) -> bool:
    return config.get(CONF_IMPEDANCE_MODE) == IMPEDANCE_MODE_DUAL


def _get_z_lf(metrics: Mapping[Metric, StateType | datetime]) -> float:
    z1 = to_float(metrics.get(Metric.IMPEDANCE_LOW))
    z2 = to_float(metrics.get(Metric.IMPEDANCE_HIGH))
    return max(z1, z2) if z1 > 0 and z2 > 0 else z1


def _get_z_hf(metrics: Mapping[Metric, StateType | datetime]) -> float:
    z1 = to_float(metrics.get(Metric.IMPEDANCE_LOW))
    z2 = to_float(metrics.get(Metric.IMPEDANCE_HIGH))
    return min(z1, z2) if z1 > 0 and z2 > 0 else z2


def _get_z_std(metrics: Mapping[Metric, StateType | datetime]) -> float:
    return to_float(metrics.get(Metric.IMPEDANCE))


# ─────────────────────────────────────────────────────────────────────────────
# LEAN BODY MASS (LBM)
# ─────────────────────────────────────────────────────────────────────────────

def get_lbm(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Lean Body Mass (Fat-Free Mass)."""
    h = to_float(config.get(CONF_HEIGHT))
    w = to_float(metrics.get(Metric.WEIGHT))
    a = to_float(metrics.get(Metric.AGE))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    z = _get_z_lf(metrics) if _is_dual(config) else _get_z_std(metrics)

    if h <= 0 or w <= 0 or z <= 0 or gender is None:
        return 0.0

    # Sanitas / Beurer openScale Formula
    if mode == ALGO_SANITAS:
        if gender == Gender.MALE:
            lbm = 0.485 * ((h * h) / z) + 0.338 * w + 5.32
        else:
            lbm = 0.485 * ((h * h) / z) + 0.298 * w + 4.34
        return check_value_constraints(lbm, 10.0, 150.0)

    # Standard openScale Formula
    elif mode == ALGO_OPENSCALE:
        if gender == Gender.MALE:
            lbm = 0.503 * ((h * h) / z) + 0.165 * w - 0.158 * a + 17.8
        else:
            lbm = 0.490 * ((h * h) / z) + 0.150 * w - 0.130 * a + 11.5
        return float(min(lbm, w * 0.98))

    # Xiaomi / Science / Dual (S400) baseline Formula
    else:
        lbm = (
            (h * 9.058 / 100.0) * (h / 100.0) + w * 0.32 + 12.226 - z * 0.0068 - a * 0.0542
        )
        return float(min(lbm, w * 0.98))


# ─────────────────────────────────────────────────────────────────────────────
# BODY FAT PERCENTAGE
# ─────────────────────────────────────────────────────────────────────────────

def get_fat_percentage(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Body Fat Percentage."""
    w = to_float(metrics.get(Metric.WEIGHT))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if w <= 0 or gender is None:
        return 0.0

    if mode == ALGO_SANITAS:
        lbm = get_lbm(config, metrics)
        fat_pct = ((w - lbm) / w) * 100.0
        return check_value_constraints(fat_pct, 3.0, 75.0)

    elif mode == ALGO_OPENSCALE:
        lbm = get_lbm(config, metrics)
        fat_pct = ((w - lbm) / w) * 100.0
        return check_value_constraints(fat_pct, 5.0, 75.0)

    elif _is_dual(config) or mode == ALGO_SCIENCE:
        lbm = get_lbm(config, metrics)
        fat_pct = ((w - lbm) / w) * 100.0
        return check_value_constraints(fat_pct, 5.0, 75.0)

    else:
        # XIAOMI Default
        lbm = get_lbm(config, metrics)
        offset = 0.8 if gender == Gender.FEMALE else 1.2
        fat_pct = (1.0 - ((lbm - offset) / w)) * 100.0
        return check_value_constraints(fat_pct, 5.0, 75.0)


# ─────────────────────────────────────────────────────────────────────────────
# WATER PERCENTAGE
# ─────────────────────────────────────────────────────────────────────────────

def get_water_percentage(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Total Body Water Percentage."""
    w = to_float(metrics.get(Metric.WEIGHT))
    fat_pct = to_float(metrics.get(Metric.FAT_PERCENTAGE))
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if w <= 0:
        return 0.0

    if mode == ALGO_SANITAS:
        lbm = get_lbm(config, metrics)
        water_pct = (lbm * 0.732 / w) * 100.0
        return check_value_constraints(water_pct, 35.0, 75.0)

    elif mode == ALGO_OPENSCALE:
        lbm = get_lbm(config, metrics)
        water_pct = (lbm * 0.73 / w) * 100.0
        return check_value_constraints(water_pct, 35.0, 75.0)

    elif _is_dual(config) or mode == ALGO_SCIENCE:
        water_pct = (100.0 - fat_pct) * 0.73
        return clamp_water_percentage(water_pct)

    else:
        # XIAOMI
        water_pct = (100.0 - fat_pct) * 0.7
        water_pct *= 1.02 if water_pct <= 50.0 else 0.98
        return check_value_constraints(water_pct, 35.0, 75.0)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FOR DUAL-FREQUENCY MULTI-COMPARTMENT CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def _get_tbw_for_compartments(
    metrics: Mapping[Metric, StateType | datetime],
) -> float:
    w = to_float(metrics.get(Metric.WEIGHT))
    fat_pct = to_float(metrics.get(Metric.FAT_PERCENTAGE))
    if w <= 0:
        return 0.0
    return (1.0 - fat_pct / 100.0) * 0.73 * w


# ─────────────────────────────────────────────────────────────────────────────
# ECW — EXTRA CELLULAR WATER (Dual mode fallback indicators)
# ─────────────────────────────────────────────────────────────────────────────

def get_ecw(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    _ = config
    z_lf = _get_z_lf(metrics)
    z_hf = _get_z_hf(metrics)

    if z_lf <= 0 or z_hf <= 0:
        return 0.0

    tbw = _get_tbw_for_compartments(metrics)
    if tbw <= 0:
        return 0.0

    z_ratio = z_hf / z_lf
    return float(tbw * (0.32 + 0.08 * z_ratio))


# ─────────────────────────────────────────────────────────────────────────────
# ICW — INTRA CELLULAR WATER
# ─────────────────────────────────────────────────────────────────────────────

def get_icw(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    tbw = _get_tbw_for_compartments(metrics)
    ecw = get_ecw(config, metrics)
    return max(0.0, tbw - ecw)


# ─────────────────────────────────────────────────────────────────────────────
# ECW/TBW RATIO
# ─────────────────────────────────────────────────────────────────────────────

def get_ecw_tbw_ratio(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    tbw = _get_tbw_for_compartments(metrics)
    ecw = get_ecw(config, metrics)

    if tbw <= 0:
        return 0.0

    return (ecw / tbw) * 100.0


# ─────────────────────────────────────────────────────────────────────────────
# BCM — BODY CELL MASS
# ─────────────────────────────────────────────────────────────────────────────

def get_bcm(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    icw = get_icw(config, metrics)
    if icw <= 0:
        return 0.0
    return icw / 0.73


# ─────────────────────────────────────────────────────────────────────────────
# SKELETAL MUSCLE MASS (S400 Dual mode exclusive)
# ─────────────────────────────────────────────────────────────────────────────

def get_skeletal_muscle_mass(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    h = to_float(config.get(CONF_HEIGHT))
    a = to_float(metrics.get(Metric.AGE))
    z_lf = _get_z_lf(metrics)
    gender = config.get(CONF_GENDER)

    if h <= 0 or a <= 0 or z_lf <= 0 or gender is None:
        return 0.0

    ri_lf = (h * h) / z_lf
    sex = 1.0 if gender == Gender.MALE else 0.0
    smm = (ri_lf * 0.401) + (sex * 3.825) + (a * -0.071) + 5.102
    return max(0.0, smm)


# ─────────────────────────────────────────────────────────────────────────────
# BONE MASS
# ─────────────────────────────────────────────────────────────────────────────

def get_bone_mass(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Bone Mass."""
    w = to_float(metrics.get(Metric.WEIGHT))
    lbm = to_float(metrics.get(Metric.LBM))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if gender is None:
        return 0.0

    if mode == ALGO_SANITAS:
        lbm_recalc = get_lbm(config, metrics)
        bone_mass = lbm_recalc * 0.05
        return check_value_constraints(bone_mass, 0.5, 10.0)

    elif mode == ALGO_OPENSCALE:
        if gender == Gender.MALE:
            bone_mass = (w * 0.04) + 0.5
        else:
            bone_mass = (w * 0.035) + 0.5
        return check_value_constraints(bone_mass, 0.5, 8.0)

    else:
        base = 0.245691014 if gender == Gender.FEMALE else 0.18016894
        bone_mass = (base - (lbm * 0.05158)) * -1

        if bone_mass > 2.2:
            bone_mass += 0.1
        else:
            bone_mass -= 0.1

        if (gender == Gender.FEMALE and bone_mass > 5.1) or (
            gender == Gender.MALE and bone_mass > 5.2
        ):
            bone_mass = 8.0

        return check_value_constraints(bone_mass, 0.5, 8.0)


# ─────────────────────────────────────────────────────────────────────────────
# MUSCLE MASS
# ─────────────────────────────────────────────────────────────────────────────

def get_muscle_mass(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Muscle Mass."""
    w = to_float(metrics.get(Metric.WEIGHT))
    fat_pct = to_float(metrics.get(Metric.FAT_PERCENTAGE))
    bone_mass = to_float(metrics.get(Metric.BONE_MASS))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if gender is None:
        return 0.0

    if mode == ALGO_SANITAS:
        lbm = get_lbm(config, metrics)
        muscle_mass = lbm * 0.75
        return check_value_constraints(muscle_mass, 10.0, 120.0)

    elif mode == ALGO_OPENSCALE:
        lbm = get_lbm(config, metrics)
        estimated_bone = (w * 0.04) + 0.5 if gender == Gender.MALE else (w * 0.035) + 0.5
        muscle_mass = lbm - estimated_bone
        return check_value_constraints(muscle_mass, 10.0, 120.0)

    else:
        muscle_mass = w - (fat_pct * 0.01 * w) - bone_mass

        if (gender == Gender.FEMALE and muscle_mass >= 84.0) or (
            gender == Gender.MALE and muscle_mass >= 93.5
        ):
            muscle_mass = 120.0

        return check_value_constraints(muscle_mass, 10.0, 120.0)


# ─────────────────────────────────────────────────────────────────────────────
# METABOLIC AGE
# ─────────────────────────────────────────────────────────────────────────────

def get_metabolic_age(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Metabolic Age."""
    h = to_float(config.get(CONF_HEIGHT))
    w = to_float(metrics.get(Metric.WEIGHT))
    a = to_float(metrics.get(Metric.AGE))
    gender = config.get(CONF_GENDER)
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)

    if h <= 0 or w <= 0 or a <= 0 or gender is None:
        return a

    if mode == ALGO_SANITAS:
        return float(int(a))

    elif mode == ALGO_OPENSCALE:
        bmi = w / ((h / 100.0) ** 2) if h > 0 else 0.0
        if bmi > 25.0:
            metab_age = a + ((bmi - 25.0) * 1.2)
        elif 0.0 < bmi < 18.5:
            metab_age = a + ((18.5 - bmi) * 0.5)
        else:
            metab_age = a - 2.0

    elif _is_dual(config):
        lbm = to_float(metrics.get(Metric.LBM))
        bmr_actual = 370.0 + 21.6 * lbm if lbm > 0 else 0.0
        if gender == Gender.MALE:
            bmr_exp = 88.362 + 13.397 * w + 4.799 * h - 5.677 * a
        else:
            bmr_exp = 447.593 + 9.247 * w + 3.098 * h - 4.330 * a
        metab_age = a * (bmr_exp / bmr_actual) if bmr_actual > 0 else a

    else:
        z = _get_z_std(metrics)
        if z <= 0:
            return a
        if gender == Gender.MALE:
            metab_age = (
                (h * -0.7471) + (w * 0.9161) + (a * 0.4184) + (z * 0.0517) + 54.2267
            )
        else:
            metab_age = (
                (h * -1.1165) + (w * 1.5784) + (a * 0.4615) + (z * 0.0415) + 83.2548
            )
        return check_value_constraints(metab_age, 15.0, 80.0)

    return float(get_metabolic_age_clamped(int(metab_age), int(a)))


# ─────────────────────────────────────────────────────────────────────────────
# PROTEIN PERCENTAGE
# ─────────────────────────────────────────────────────────────────────────────

def get_protein_percentage(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    """Calculate Protein Percentage."""
    w = to_float(metrics.get(Metric.WEIGHT))
    lbm = to_float(metrics.get(Metric.LBM))
    mode = config.get(CONF_CALCULATION_MODE, ALGO_XIAOMI)
    gender = config.get(CONF_GENDER)

    if w <= 0:
        return 0.0

    if mode == ALGO_SANITAS:
        lbm_recalc = get_lbm(config, metrics)
        bone = lbm_recalc * 0.05
        water_mass = lbm_recalc * 0.732
        protein_pct = ((lbm_recalc - water_mass - bone) / w) * 100.0
        return check_value_constraints(protein_pct, 5.0, 30.0)

    elif mode == ALGO_OPENSCALE:
        lbm_recalc = get_lbm(config, metrics)
        water = lbm_recalc * 0.73
        bone = (w * 0.04) + 0.5 if gender == Gender.MALE else (w * 0.035) + 0.5
        protein_kg = lbm_recalc - water - bone
        protein_pct = (protein_kg / w) * 100.0
        return check_value_constraints(protein_pct, 5.0, 32.0)

    elif _is_dual(config) or mode == ALGO_SCIENCE:
        if lbm <= 0:
            return 0.0
        protein_pct = (lbm * 0.195 / w) * 100.0
        return check_value_constraints(protein_pct, 5.0, 32.0)

    else:
        # XIAOMI
        muscle = to_float(metrics.get(Metric.MUSCLE_MASS))
        water = to_float(metrics.get(Metric.WATER_PERCENTAGE))
        protein_pct = (muscle / w) * 100.0 - water
        return check_value_constraints(protein_pct, 5.0, 32.0)


# ─────────────────────────────────────────────────────────────────────────────
# FAT MASS TO IDEAL WEIGHT
# ─────────────────────────────────────────────────────────────────────────────

def get_fat_mass_to_ideal_weight(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> float:
    w = to_float(metrics.get(Metric.WEIGHT))
    a = to_float(metrics.get(Metric.AGE))
    fat_pct = to_float(metrics.get(Metric.FAT_PERCENTAGE))

    target = config[CONF_CLINICAL_BODY_SCALE].get_fat_percentage(int(a))[2]
    return float(w * (target / 100.0) - w * (fat_pct / 100.0))


# ─────────────────────────────────────────────────────────────────────────────
# BODY TYPE
# ─────────────────────────────────────────────────────────────────────────────

def get_body_type(
    config: Mapping[str, Any], metrics: Mapping[Metric, StateType | datetime]
) -> str:
    fat = to_float(metrics.get(Metric.FAT_PERCENTAGE))
    muscle = to_float(metrics.get(Metric.MUSCLE_MASS))
    a = to_float(metrics.get(Metric.AGE))
    clinical_scale = config[CONF_CLINICAL_BODY_SCALE]

    f_scale = clinical_scale.get_fat_percentage(int(a))
    factor = 0 if fat > f_scale[2] else (2 if fat < f_scale[1] else 1)
    m_factor = (
        2
        if muscle > clinical_scale.muscle_mass[1]
        else (0 if muscle < clinical_scale.muscle_mass[0] else 1)
    )
    body_type = m_factor + (factor * 3)

    return [
        "obese",
        "overweight",
        "thick_set",
        "lack_exercise",
        "balanced",
        "balanced_muscular",
        "skinny",
        "balanced_skinny",
        "skinny_muscular",
    ][body_type]