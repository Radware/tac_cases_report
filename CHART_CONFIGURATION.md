# TAC Executive Report - Chart Configuration Guide

This guide explains how to customize chart types and styles in the TAC Executive Report Generator without modifying any code.

## Configuration Files

- **Chart Types & Styles**: `tac_config.py` - CHART_TYPES and CHART_STYLES sections
- **Colors**: `tac_config.py` - COLOR CONFIGURATION section  
- **Detailed Color Guide**: `COLOR_CONFIGURATION.md`

## Quick Chart Type Changes

To change chart types, simply edit the `CHART_TYPES` dictionary in `tac_config.py`:

```python
CHART_TYPES = {
    'monthly_trends': 'bar',              # 'line', 'bar', 'area'
    'severity_distribution': 'pie',       # 'pie', 'donut', 'bar', 'horizontal_bar'
    'product_hierarchy': 'horizontal_bar', # 'pie', 'donut', 'bar', 'horizontal_bar'
    'bug_analysis': 'pie',                # 'pie', 'donut', 'bar', 'horizontal_bar'
    'internal_external': 'donut',         # 'pie', 'donut', 'bar', 'horizontal_bar'
    'queue_distribution': 'bar',          # 'pie', 'donut', 'bar', 'horizontal_bar'
    'engineer_assignment': 'horizontal_bar', # 'bar', 'horizontal_bar'
}
```

## Chart Type Options

### Monthly Trends Chart
- **`'line'`**: Traditional line chart with trend line (best for time series analysis)
- **`'bar'`**: Bar chart showing discrete monthly values (easier to read exact values)
- **`'area'`**: Area chart with filled region under line (emphasizes volume)

### Distribution Charts
- **`'pie'`**: Traditional pie chart (good for showing proportions)
- **`'donut'`**: Pie chart with center hole (modern look, easier to read labels)
- **`'bar'`**: Vertical bar chart (easier to compare exact values)
- **`'horizontal_bar'`**: Horizontal bar chart (better for long category names)

**Note**: The bug analysis section shows two charts:
1. Bug vs Non-Bug Cases breakdown
2. Bug Types breakdown (when bug cases are present)
Both charts use the same chart type specified in `bug_analysis` configuration.

### Assignment Charts
- **`'bar'`**: Vertical bars (good for rankings)
- **`'horizontal_bar'`**: Horizontal bars (better for names/labels)

## Example Configurations

### Executive Dashboard Style (Clean, Professional)
```python
CHART_TYPES = {
    'monthly_trends': 'bar',
    'severity_distribution': 'horizontal_bar',
    'product_hierarchy': 'horizontal_bar', 
    'bug_analysis': 'donut',
    'internal_external': 'donut',
    'queue_distribution': 'horizontal_bar',
    'engineer_performance': 'horizontal_bar',
}
```

### Traditional Style (Classic Charts)
```python
CHART_TYPES = {
    'monthly_trends': 'line',
    'severity_distribution': 'pie',
    'product_hierarchy': 'pie', 
    'bug_analysis': 'pie',
    'internal_external': 'pie',
    'queue_distribution': 'pie',
    'engineer_performance': 'bar',
}
```

### Modern Dashboard Style (Mix of Chart Types)
```python
CHART_TYPES = {
    'monthly_trends': 'area',
    'severity_distribution': 'donut',
    'product_hierarchy': 'bar', 
    'bug_analysis': 'horizontal_bar',
    'internal_external': 'donut',
    'queue_distribution': 'donut',
    'engineer_performance': 'horizontal_bar',
}
```

## Advanced Styling

For advanced customization, you can modify the `CHART_STYLES` dictionary in `tac_config.py`:

### Example: Customize Pie Chart Appearance
```python
CHART_STYLES = {
    'distribution_charts': {
        'pie': {
            'hole': 0.0,  # 0 for full pie, 0.3+ for donut
            'textinfo': 'label+percent',  # Show labels and percentages
            'textposition': 'inside'  # Place text inside slices
        },
        'donut': {
            'hole': 0.6,  # Large center hole
            'textinfo': 'label+value',
            'textposition': 'outside'
        }
    }
}
```

### Example: Customize Bar Chart Appearance
```python
CHART_STYLES = {
    'distribution_charts': {
        'bar': {
            'show_values': False,  # Hide value labels on bars
        }
    }
}
```

## Tips for Chart Selection

1. **Monthly Trends**: 
   - Use `'bar'` for discrete monthly comparisons
   - Use `'line'` for trend analysis over time
   - Use `'area'` to emphasize volume/magnitude

2. **Distribution Charts**:
   - Use `'pie'` or `'donut'` for proportional data (percentages)
   - Use `'horizontal_bar'` for long category names
   - Use `'bar'` when exact values are more important than proportions

3. **Performance Charts**:
   - Use `'horizontal_bar'` for ranking with names/labels
   - Use `'bar'` for simple numerical rankings
   - Use `'scatter'` when you want to show relationships

## Testing Changes

After making changes to `tac_config.py`, run the analyzer to see your new chart types:

```bash
python tac_analyzer.py --format html
```

The new chart types will be applied to all generated reports automatically.

## Color Customization

The system includes comprehensive color customization options:

### Quick Color Palette Change
```python
# In tac_config.py, change the active palette:
ACTIVE_COLOR_PALETTE = 'professional_blue'  # Switch from default 'radware_corporate'
```

### Available Color Palettes
- `'radware_corporate'` - Default Radware branding (recommended)
- `'professional_blue'` - Blue-focused professional theme
- `'modern_minimal'` - Clean, minimal colors
- `'vibrant_corporate'` - Bright, energetic colors
- `'high_contrast'` - Maximum contrast for accessibility
- `'colorblind_friendly'` - Safe for color vision deficiency

### Custom Colors
You can override specific chart element colors in the `CHART_COLOR_ASSIGNMENTS` section:

```python
CHART_COLOR_ASSIGNMENTS = {
    'severity_colors': {
        'Critical': '#dc3545',    # Red
        'High': '#ff6b35',        # Orange
        'Medium': '#ffc107',      # Yellow
        'Low': '#28a745',         # Green
    },
    'bug_colors': {
        'Bug Cases': '#dc3545',      # Red for bugs
        'Non-Bug Cases': '#28a745'   # Green for non-bugs
    },
    # ... more color assignments
}
```

📖 **For detailed color customization instructions, see `COLOR_CONFIGURATION.md`**

This system gives you complete control over report visualizations while maintaining professional, consistent styling.