# TAC Executive Report - Color Configuration Guide

This guide explains how to customize chart colors in the TAC Executive Report Generator.

## Quick Color Palette Changes

To change color palettes, edit the `ACTIVE_COLOR_PALETTE` setting in `tac_config.py`:

```python
# Set the active color palette (change this to switch color schemes)
ACTIVE_COLOR_PALETTE = 'radware_corporate'  # Choose from available palettes
```

## Available Color Palettes

### 1. `'radware_corporate'` (Default)
Professional corporate colors with Radware branding:
- Primary blues, orange accents, and colorblind-friendly selections
- Best for: Executive presentations, client-facing reports

### 2. `'professional_blue'`
Blue-focused professional theme:
- Various shades of blue with orange highlights
- Best for: Technical documentation, conservative presentations

### 3. `'modern_minimal'`
Clean, minimal color scheme:
- Grays and muted colors with selective bright accents
- Best for: Modern dashboards, minimalist designs

### 4. `'vibrant_corporate'`
Bright, energetic corporate colors:
- High-contrast, attention-grabbing colors
- Best for: Marketing materials, dynamic presentations

### 5. `'high_contrast'`
Maximum contrast for accessibility:
- Black, white, and primary colors only
- Best for: Accessibility compliance, high-contrast displays

### 6. `'colorblind_friendly'`
Scientifically designed for color vision deficiency:
- Safe for deuteranopia and protanopia
- Best for: Inclusive design, scientific publications

## Custom Color Palettes

Create your own color palette by adding to `COLOR_PALETTES`:

```python
COLOR_PALETTES = {
    # ... existing palettes ...
    
    'my_custom_theme': [
        '#FF5733',  # Red-orange
        '#33FF57',  # Green
        '#3357FF',  # Blue
        '#FF33F5',  # Magenta
        '#33FFF5',  # Cyan
        # Add more colors as needed
    ]
}

# Then activate it
ACTIVE_COLOR_PALETTE = 'my_custom_theme'
```

## Specific Color Assignments

Override specific chart elements by modifying `CHART_COLOR_ASSIGNMENTS`:

### Severity Colors
```python
'severity_colors': {
    'Critical': '#dc3545',    # Red
    'High': '#ff6b35',        # Orange  
    'Medium': '#ffc107',      # Yellow
    'Low': '#28a745',         # Green
    'Info': '#17a2b8'         # Blue
}
```

### Bug Analysis Colors
```python
'bug_colors': {
    'Bug Cases': '#dc3545',      # Red for bugs
    'Non-Bug Cases': '#28a745'   # Green for non-bugs
}
```

### Internal/External Colors
```python
'internal_external_colors': {
    'Internal': '#003f7f',       # Radware blue for internal
    'External': '#6cb2eb'        # Light blue for external
}
```

### Monthly Trends Colors
```python
'trends_colors': {
    'primary': '#003f7f',        # Main trend line color
    'area_fill': 'rgba(0, 63, 127, 0.3)'  # Semi-transparent fill for area charts
}
```

## Color Format Options

Colors can be specified in multiple formats:

### Hex Colors (Recommended)
```python
'#FF5733'  # Red-orange
'#003f7f'  # Radware blue
```

### RGB Colors
```python
'rgb(255, 87, 51)'     # Same red-orange
'rgba(0, 63, 127, 0.5)' # Semi-transparent blue
```

### Named Colors
```python
'red'
'blue' 
'green'
'orange'
```

## Example Custom Configurations

### Corporate Red Theme
```python
ACTIVE_COLOR_PALETTE = 'vibrant_corporate'

CHART_COLOR_ASSIGNMENTS = {
    'severity_colors': {
        'Critical': '#8B0000',    # Dark red
        'High': '#DC143C',        # Crimson
        'Medium': '#FF6347',      # Tomato
        'Low': '#32CD32',         # Lime green
        'Info': '#4682B4'         # Steel blue
    },
    'trends_colors': {
        'primary': '#8B0000',     # Dark red primary
        'area_fill': 'rgba(139, 0, 0, 0.2)'
    }
}
```

### Accessibility-First Theme
```python
ACTIVE_COLOR_PALETTE = 'high_contrast'

CHART_COLOR_ASSIGNMENTS = {
    'severity_colors': {
        'Critical': '#000000',    # Black
        'High': '#FF0000',        # Pure red  
        'Medium': '#0000FF',      # Pure blue
        'Low': '#00FF00',         # Pure green
        'Info': '#FFFF00'         # Yellow
    }
}
```

### Scientific Publication Theme
```python
ACTIVE_COLOR_PALETTE = 'colorblind_friendly'

# Use default color assignments - they're already optimized for colorblind users
```

## Testing Color Changes

After modifying colors:

1. Save `tac_config.py`
2. Run the analyzer: `python tac_analyzer.py --format html`
3. Open generated HTML reports to preview colors
4. Adjust as needed

## Color Accessibility Tips

1. **Ensure sufficient contrast**: Use online contrast checkers
2. **Test with colorblind simulators**: Verify accessibility
3. **Don't rely on color alone**: Use patterns, shapes, or labels
4. **Consider your audience**: Corporate vs. technical vs. public
5. **Test on different displays**: Colors may appear different on various screens

## Troubleshooting

### Colors Not Changing
- Check `ACTIVE_COLOR_PALETTE` spelling
- Ensure color format is correct (hex codes with #)
- Verify palette exists in `COLOR_PALETTES`

### Charts Look Wrong
- Regenerate reports after color changes
- Clear browser cache if viewing HTML files
- Check console for error messages

### Want to Reset
Set `ACTIVE_COLOR_PALETTE = 'radware_corporate'` to return to defaults.