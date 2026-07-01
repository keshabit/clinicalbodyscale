# Clinical Body Scale (`clinicalbodyscale`)

The **Clinical Body Scale** integration for Home Assistant transforms raw data from smart weight scales (such as Xiaomi, Sanitas, OpenScale-supported scales, etc.) into a comprehensive suite of clinical health and body composition metrics. By inputting basic biological attributes (height, gender, age, and activity level), this integration automatically computes advanced health indices directly within your Home Assistant ecosystem.

---

## 🚀 Key Benefits & Features

* **Advanced Body Composition Metrics**: Beyond basic weight tracking, it calculates BMI, Basal Metabolic Rate (BMR), Visceral Fat, Lean Body Mass, Body Fat Percentage, Protein Percentage, Water Percentage, Bone Mass, Muscle Mass, Metabolic Age, Body Score, and Body Type.
* **Dual-Frequency Impedance Support**: For high-end diagnostic scales, selecting the Dual Impedance mode enables advanced clinical parameters: Extracellular Water (ECW), Intracellular Water (ICW), ECW/TBW ratio, Body Cell Mass (BCM), and Skeletal Muscle Mass.
* **Cold-Start State Restoration**: Built with Home Assistant’s native `RestoreSensor` API. It automatically reloads your last known historical data upon Home Assistant restarts and seeds the internal cache. **No more cumbersome template helpers or `input_number` entities are required to maintain persistent data**.
* **Timezone-Aware Timestamps**: The `last_measurement_time` sensor automatically handles UTC-to-local timezone conversion, properly formatting the timestamp to reflect your local instance's configuration.
* **Sophisticated Multi-User Profile Routing**: Easily support multiple people in the same household using one physical scale through 5 optional profile matching filters.

---

## 🛠 Multi-User Profile Identification Methods

When multiple users share a scale, you can configure individual integration entries for each person. The component isolates measurements using one of the following strategies:

1. **No Filter (`none`)**: Accepts every incoming measurement unconditionally (best for single-user setups).
2. **Profile ID Filter (`profile_id`)**: Evaluates a numeric profile ID (1 through 5) broadcasted by your smart scale's sensor.
3. **Weight Range Filter (`weight_range`)**: Restricts entries to a strict half-open interval `[min, max[` in kilograms.
4. **Nearest Weight Filter (`nearest_weight`)**: Evaluates incoming weights against the user's last known weight within a specified tolerance boundary.
5. **Interactive Notification (`notification`)**: Sends an interactive push notification via the `mobile_app` integration when a weight change occurs. Tapping your name fires an action event that instantly routes the pending data to your profile.

---

## 📋 Pre-requisites & Requirements

* **Home Assistant Core**: version `2026.3.0` or higher.
* **Source Scale Sensors**: A pre-existing weight sensor entity (and optional impedance sensor entities) setup in Home Assistant via integrations like Bluetooth, Zigbee, MQTT, ESPHome, or OpenScale.

---

## 📦 Installation Instructions

### Method 1: Via HACS (Recommended)

1. Navigate to **HACS** (Home Assistant Community Store) in your sidebar.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the repository URL: `https://github.com/keshabit/clinicalbodyscale` and select **Integration** as the category.
4. Click **Add**, then find **Clinical Body Scale** in the listing and click **Download**.
5. **Restart Home Assistant** to load the custom component.

### Method 2: Manual Installation

1. Download the source code archive for version `1.4.0`.
2. Extract the archive and copy the `clinicalbodyscale` folder into your Home Assistant configuration's `custom_components/` directory (e.g., `/config/custom_components/clinicalbodyscale/`).
3. **Restart Home Assistant**.

---

## ⚙️ Step-by-Step UI Setup Guide

The integration is fully managed through a multi-step user-friendly configuration flow.

1. In Home Assistant, go to **Settings** ➡️ **Devices & Services**.
2. Click **+ Add Integration** in the bottom right corner.
3. Search for **Clinical Body Scale** and select it.
4. Follow the interactive setup prompts across four simple stages:

### Step 1: User Identity

* **Name**: Enter the name of the user profile (e.g., `John`).
* **Birthday**: Enter the date of birth (used for continuous age calculations).
* **Gender**: Select `Male` or `Female`.

### Step 2: Biological & Operational Modes

* **Height**: Provide height in centimeters (cm).
* **Activity Level**: Choose your corresponding physical multiplier: `Sedentary` (Default), `Light`, `Moderate`, `Active`, or `Very Active` (used to evaluate metabolic adjustments).
* **Calculation Mode**: Select your preferred algorithm formula base:
* `Xiaomi` (Default)
* `OpenScale`
* `Sanitas`
* `Science`


* **Impedance Mode**: Select based on your physical scale hardware capabilities:
* `None` (Only generates weight-based sensors like BMI, BMR, and Visceral Fat)
* `Standard` (Requires a single overall raw impedance sensor)
* `Dual Frequency` (Requires separate low-frequency and high-frequency impedance sensors)


* **Profile Method**: Choose your preferred Multi-User identification method (`none`, `profile_id`, `weight_range`, `nearest_weight`, or `notification`).

### Step 3: Target Sensor Links

* Select your source **Weight Sensor** entity (supports `sensor`, `number`, or `input_number` domains).
* *(Conditional)* Select the corresponding **Impedance Sensor** or **Impedance Low / High Sensors** based on Step 2.
* *(Conditional)* Select the **Scale Profile ID Sensor** if using the `profile_id` routing method.

### Step 4: Profile Filter Configuration

*(This step dynamically adapts to the routing method chosen in Step 2)*

* **Weight Range**: Specify the minimum and maximum weight intervals.
* **Nearest Weight**: Provide an initial baseline weight and a tolerance threshold (e.g., `5 kg`).
* **Notification**: Select your targeted smartphone or tablet device linked through the Home Assistant Companion App (`mobile_app`).

Click **Submit**, and the user profile will be created! Repeat the process to create independent tracking entities for additional family members.

---

## 🗃 Generated Sensors Reference

Depending on your configuration, the following sensors will be exposed under your profile prefix:

| Sensor Translation Key | Domain / Device Class | Unit | Required Mode |
| --- | --- | --- | --- |
| **Weight** | `sensor.weight` | `kg` | Always Active |
| **Height** | `sensor.distance` | `cm` | Always Active |
| **BMI** | Measurement | Index | Always Active |
| **Ideal Weight** | `sensor.weight` | `kg` | Always Active |
| **Basal Metabolism** | Measurement | `kcal` | Always Active |
| **Visceral Fat** | Measurement | Rating | Always Active |
| **Last Measurement Time** | Timestamp String | `HH:MM DD/MM/YY` | Always Active |
| **Lean Body Mass** | `sensor.weight` | `kg` | Standard / Dual |
| **Body Fat** | Measurement | `%` | Standard / Dual |
| **Protein** | Measurement | `%` | Standard / Dual |
| **Water** | Measurement | `%` | Standard / Dual |
| **Bone Mass** | `sensor.weight` | `kg` | Standard / Dual |
| **Muscle Mass** | `sensor.weight` | `kg` | Standard / Dual |
| **Metabolic Age** | Measurement | Years | Standard / Dual |
| **Body Score** | Measurement | Points | Standard / Dual |
| **Body Type** | Text Status | String | Standard / Dual |
| **Impedance** | Measurement | `Ω` | Standard Only |
| **Extracellular Water** | Measurement | `L` | Dual Only |
| **Intracellular Water** | Measurement | `L` | Dual Only |
| **ECW/TBW Ratio** | Measurement | `%` | Dual Only |
| **Body Cell Mass** | `sensor.weight` | `kg` | Dual Only |
| **Skeletal Muscle Mass** | `sensor.weight` | `kg` | Dual Only |
| **Impedance High** | Measurement | `Ω` | Dual Only |
| **Impedance Low** | Measurement | `Ω` | Dual Only |

---

## 🔍 Troubleshooting & Issues

If you encounter unexpected metric variations or debugging errors:

1. Ensure your source sensors are correctly delivering numerical floats or integers.
2. Verify that your calculation mode aligns with your scale's factory app settings.
3. Open a detailed technical issue tracker via the [Official Issues Repository](https://github.com/keshabit/clinicalbodyscale/issues).
