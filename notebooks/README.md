# Data Exploration Notebook

This notebook provides initial exploration of Bangkok traffic data.

## Quick Setup
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
```

## Load Sample Data
```python
# Load a sample PROBE file
probe_file = "data/raw/PROBE-202401/20240101.csv.out"
df = pd.read_csv(probe_file)

print(f"Data shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
```

## Basic Analysis
```python
# Speed distribution
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.hist(df['speed'], bins=50, alpha=0.7)
plt.title('Speed Distribution')
plt.xlabel('Speed (km/h)')

plt.subplot(1, 3, 2)
plt.scatter(df['lon'], df['lat'], c=df['speed'], alpha=0.5)
plt.title('Geographic Speed Distribution')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

plt.subplot(1, 3, 3)
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
hourly_speed = df.groupby('hour')['speed'].mean()
plt.plot(hourly_speed.index, hourly_speed.values)
plt.title('Average Speed by Hour')
plt.xlabel('Hour of Day')

plt.tight_layout()
plt.show()
```

## Next Steps
1. Explore multiple days/months
2. Analyze traffic patterns
3. Examine road network data
4. Identify data quality issues

For detailed analysis, see other notebooks in this directory.
