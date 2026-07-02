<p align="center">
  <img src="./images/icon.png" alt="ClinicalBodyScale Logo" width="180">
</p>

<h1 align="center">ClinicalBodyScale</h1>

<p align="center">
  <strong>Clinical-grade Body Composition Analysis for Home Assistant</strong>
</p>

<p align="center">
Transform your smart body scale into a comprehensive health assessment platform with scientifically based body composition calculations, intelligent multi-user identification, and fully local processing.
</p>

<p align="center">

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.3%2B-41BDF5?style=for-the-badge\&logo=homeassistant)  ![HACS](https://img.shields.io/badge/HACS-Custom%20Repository-41BDF5?style=for-the-badge)  ![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge\&logo=python)  ![License](https://img.shields.io/github/license/keshabit/clinicalbodyscale?style=for-the-badge)

</p>

---

## Why ClinicalBodyScale?

Most smart scales provide only basic measurements such as weight or vendor-specific body fat estimates. ClinicalBodyScale brings advanced body composition analysis directly into Home Assistant by applying scientifically validated calculation models to your scale data.

Whether your scale connects through Bluetooth, ESPHome, MQTT, Zigbee, OpenScale, Xiaomi integrations, or other Home Assistant integrations, ClinicalBodyScale converts raw measurements into meaningful health metrics while keeping all processing completely local.

Unlike vendor mobile applications, ClinicalBodyScale is designed to integrate naturally into Home Assistant dashboards, automations, long-term statistics, and notifications.

---

# ✨ Features

### 🩺 Clinical Body Composition

Generate more than **25 health metrics**, including:

* Body Mass Index (BMI)
* Body Fat Percentage
* Lean Body Mass
* Muscle Mass
* Skeletal Muscle Mass
* Bone Mass
* Body Water
* Protein Percentage
* Basal Metabolic Rate (BMR)
* Visceral Fat
* Metabolic Age
* Body Score
* Body Type
* Ideal Body Weight
* Last Measurement Timestamp

---

### ⚡ Dual-Frequency Bioelectrical Impedance

Supports advanced body composition scales capable of dual-frequency impedance measurements.

Additional clinical metrics include:

* Extracellular Water (ECW)
* Intracellular Water (ICW)
* ECW / TBW Ratio
* Body Cell Mass (BCM)
* Skeletal Muscle Mass
* High Frequency Impedance
* Low Frequency Impedance

---

### 👨‍👩‍👧 Intelligent Multi-User Support

One smart scale.

Multiple family members.

No cloud services required.

ClinicalBodyScale automatically routes measurements using five configurable identification methods:

* No Filtering
* Scale Profile ID
* Weight Range
* Nearest Previous Weight
* Interactive Mobile Notifications

Perfect for households sharing a single scale.

---

### 🔄 Persistent Measurements

Built using Home Assistant's native **RestoreSensor** API.

After a Home Assistant restart:

* Previous measurements are restored automatically.
* Internal history cache is rebuilt.
* No helper entities are required.
* No template sensors are necessary.

Everything continues exactly where it left off.

---

### 🧠 Multiple Calculation Models

Choose the algorithm that best matches your scale.

Supported calculation models include:

| Model     | Best For                          |
| --------- | --------------------------------- |
| Xiaomi    | Xiaomi Mi Body Composition Scales |
| OpenScale | OpenScale compatible devices      |
| Sanitas   | Sanitas diagnostic scales         |
| Science   | General scientific formulas       |

---

## What Makes ClinicalBodyScale Different?

Many integrations simply expose values reported by the manufacturer's application.

ClinicalBodyScale takes a different approach.

Instead of trusting vendor-provided estimates, it computes body composition locally using established formulas and configurable calculation models. This makes it suitable for users who want consistent measurements regardless of scale brand while benefiting from Home Assistant's automation and visualization capabilities.

The integration is designed to be extensible, allowing future support for additional algorithms, new diagnostic metrics, and more advanced body composition analysis as compatible hardware becomes available.

---

# 📦 Installation

ClinicalBodyScale can be installed using **HACS (recommended)** or by manually copying the integration into your Home Assistant configuration.

## Installation Methods

| Method | Difficulty      | Recommended |
| ------ | --------------- | ----------- |
| HACS   | ⭐ Easy          | ✅ Yes       |
| Manual | ⭐⭐ Intermediate | ✔ Supported |

---

# 🚀 Install with HACS (Recommended)

Using HACS provides automatic update notifications and makes future upgrades effortless.

### Step 1 — Open HACS

In Home Assistant, navigate to:

```
HACS → Integrations
```

Click the **⋮** menu in the upper-right corner and select:

```
Custom repositories
```

---

### Step 2 — Add Repository

Repository URL

```
https://github.com/keshabit/clinicalbodyscale
```

Category

```
Integration
```

Click **Add**.

---

### Step 3 — Install

Search for

```
ClinicalBodyScale
```

Select the integration and click

```
Download
```

---

### Step 4 — Restart Home Assistant

Restart Home Assistant to load the custom component.

After restarting:

```
Settings
→ Devices & Services
→ Add Integration
```

Search for

```
ClinicalBodyScale
```

and begin the configuration wizard.

---

# 📁 Manual Installation

If you prefer manual installation:

Download the latest release from GitHub.

Copy

```
custom_components/
    clinicalbodyscale/
```

into

```
config/
└── custom_components/
    └── clinicalbodyscale/
```

Your directory should look similar to:

```
config/

├── automations.yaml
├── configuration.yaml
├── custom_components
│
└── clinicalbodyscale
    ├── __init__.py
    ├── manifest.json
    ├── config_flow.py
    ├── sensor.py
    ├── coordinator.py
    ├── calculations.py
    ├── profile.py
    ├── translations
    └── icons.json
```

Restart Home Assistant.

---

# ⚙️ Configuration

ClinicalBodyScale uses Home Assistant's modern **Config Flow**.

No YAML configuration is required.

Navigate to

```
Settings
→ Devices & Services
→ Add Integration
```

Search for

```
ClinicalBodyScale
```

The setup wizard guides you through every step.

---

# Step 1 — User Information

Enter your personal information.

| Field    | Description                          |
| -------- | ------------------------------------ |
| Name     | Friendly profile name                |
| Birthday | Used for continuous age calculations |
| Gender   | Male or Female                       |

The birthday is stored so age automatically updates over time.

No yearly adjustments are necessary.

---

# Step 2 — Body Parameters

Provide your biological information.

| Setting           | Description                           |
| ----------------- | ------------------------------------- |
| Height            | Height in centimeters                 |
| Activity Level    | Daily activity multiplier             |
| Calculation Model | Xiaomi, OpenScale, Sanitas or Science |
| Impedance Mode    | None, Standard or Dual Frequency      |
| Profile Method    | Multi-user identification method      |

---

## Activity Levels

Choose the option that best matches your lifestyle.

| Level       | Description                                |
| ----------- | ------------------------------------------ |
| Sedentary   | Little or no exercise                      |
| Light       | Exercise 1–3 days/week                     |
| Moderate    | Exercise 3–5 days/week                     |
| Active      | Daily exercise                             |
| Very Active | Athlete or physically demanding occupation |

---

## Calculation Models

ClinicalBodyScale supports multiple body composition algorithms.

| Algorithm | Recommended For                 |
| --------- | ------------------------------- |
| Xiaomi    | Xiaomi Body Composition scales  |
| OpenScale | OpenScale users                 |
| Sanitas   | Sanitas diagnostic scales       |
| Science   | Generic scientific calculations |

This allows users to match calculations with the scale they own.

---

## Impedance Modes

### None

Uses only weight.

Generates:

* BMI
* BMR
* Ideal Weight
* Visceral Fat

No impedance sensor required.

---

### Standard

Uses a single impedance sensor.

Adds:

* Body Fat
* Water
* Protein
* Muscle
* Bone
* Body Score
* Body Type
* Metabolic Age

---

### Dual Frequency

Supports professional diagnostic scales.

Adds advanced metrics:

* ECW
* ICW
* BCM
* Skeletal Muscle
* ECW/TBW Ratio
* High Frequency Impedance
* Low Frequency Impedance

---

# Step 3 — Link Sensors

Select your existing Home Assistant entities.

Depending on your configuration, you may be asked to select:

| Entity                    | Required          |
| ------------------------- | ----------------- |
| Weight Sensor             | ✅ Always          |
| Standard Impedance Sensor | Standard Mode     |
| Low Frequency Sensor      | Dual Mode         |
| High Frequency Sensor     | Dual Mode         |
| Scale Profile Sensor      | Profile ID Method |

Supported entity domains include:

* sensor
* number
* input_number

---

# Step 4 — Multi-User Identification

ClinicalBodyScale can distinguish multiple users sharing a single scale.

Choose one of the following identification methods.

| Method         | Description                                           |
| -------------- | ----------------------------------------------------- |
| None           | Accept every measurement                              |
| Profile ID     | Uses scale profile number                             |
| Weight Range   | Uses configured weight interval                       |
| Nearest Weight | Matches nearest historical weight                     |
| Notification   | Ask the user through the Home Assistant Companion App |

Each user simply creates their own integration entry.

ClinicalBodyScale automatically routes incoming measurements to the correct profile.

---

# 🎯 Configuration Complete

Once setup is finished the integration immediately begins monitoring incoming measurements.

Every new reading automatically updates all calculated body composition metrics.

No templates.

No helper entities.

No YAML.

Everything is managed directly through the Home Assistant user interface.

---

# 👨‍👩‍👧 Intelligent Multi-User Identification

Sharing a single smart scale across multiple people is one of the biggest challenges in home health monitoring.

ClinicalBodyScale provides **five independent profile identification methods**, allowing every member of the household to maintain their own body composition history while using the same physical scale.

Each Home Assistant profile is configured independently and processes only the measurements that belong to that user.

---

## Available Identification Methods

| Method                       | Best For                       | Description                                                                             |
| ---------------------------- | ------------------------------ | --------------------------------------------------------------------------------------- |
| **None**                     | Single-user households         | Accept every measurement without filtering.                                             |
| **Profile ID**               | Xiaomi and supported scales    | Matches the profile number reported by the scale.                                       |
| **Weight Range**             | Families with distinct weights | Accepts measurements only within a configured weight range.                             |
| **Nearest Weight**           | Similar-weight households      | Compares new measurements to the user's previous weight using a configurable tolerance. |
| **Interactive Notification** | Maximum accuracy               | Sends a notification asking who is currently on the scale.                              |

---

## Profile ID

Some smart scales broadcast an internal profile identifier.

Example:

| Scale Output | Assigned User |
| ------------ | ------------- |
| Profile 1    | Alice         |
| Profile 2    | Bob           |
| Profile 3    | Charlie       |

ClinicalBodyScale automatically routes measurements to the correct user without additional interaction.

---

## Weight Range

Useful when household members have clearly different body weights.

Example:

| User    | Weight Range |
| ------- | ------------ |
| Alice   | 48–58 kg     |
| Bob     | 70–82 kg     |
| Charlie | 92–108 kg    |

Incoming measurements outside the configured range are ignored.

---

## Nearest Weight

Ideal when users have similar body weights.

ClinicalBodyScale compares each new measurement with the user's most recent recorded weight.

Example:

| Previous Weight | New Reading | Result   |
| --------------- | ----------- | -------- |
| 74.3 kg         | 74.8 kg     | Accepted |
| 74.3 kg         | 88.5 kg     | Ignored  |

The acceptable tolerance can be configured during setup.

---

# 🧮 Clinical Calculations

ClinicalBodyScale performs all calculations locally using configurable body composition models.

Supported calculation engines include:

| Algorithm | Typical Use                    |
| --------- | ------------------------------ |
| Xiaomi    | Xiaomi Body Composition Scales |
| OpenScale | OpenScale-compatible devices   |
| Sanitas   | Sanitas diagnostic scales      |
| Science   | General scientific equations   |

Unlike vendor applications, calculations remain consistent regardless of cloud connectivity or mobile applications.


