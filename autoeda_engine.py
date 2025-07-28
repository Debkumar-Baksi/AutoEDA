import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
import pandas as pd
import numpy as np
from typing import List, Optional

# Set style for better looking plots
plt.style.use('default')
sns.set_palette("husl")

def preprocess_data(df: pd.DataFrame, plot_type: str, columns: List[str]) -> pd.DataFrame:
    """
    Preprocess data for plotting
    """
    df = df.copy()
    
    # Ensure columns exist
    available_columns = [col for col in columns if col in df.columns]
    if not available_columns:
        raise ValueError("None of the selected columns exist in the dataset")
    
    # Select only the columns we need
    df = df[available_columns].copy()
    
    # Drop rows with all NaN values in selected columns
    df.dropna(subset=available_columns, how='all', inplace=True)
    
    # For numeric plots, convert to numeric and handle categoricals
    if plot_type in ['histogram', 'boxplot', 'scatterplot', 'lineplot', 'heatmap', 'pairplot']:
        # Convert to numeric where possible
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    # If conversion fails, keep as object for categorical plots
                    pass
    
    # Handle missing values
    if plot_type in ['histogram', 'boxplot', 'scatterplot', 'lineplot']:
        # For numeric plots, fill NaN with median for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns and df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
    
    return df

def validate_plot_requirements(df: pd.DataFrame, plot_type: str, columns: List[str]) -> None:
    """
    Validate that the data meets the requirements for the selected plot type
    """
    if not columns:
        raise ValueError("No columns selected")
    
    available_columns = [col for col in columns if col in df.columns]
    if not available_columns:
        raise ValueError("None of the selected columns exist in the dataset")
    
    if plot_type == 'histogram':
        numeric_cols = df[available_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            raise ValueError("Histogram requires at least one numeric column")
    
    elif plot_type == 'boxplot':
        numeric_cols = df[available_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            raise ValueError("Boxplot requires at least one numeric column")
    
    elif plot_type == 'countplot':
        if len(available_columns) < 1:
            raise ValueError("Countplot requires at least one column")
    
    elif plot_type == 'barplot':
        if len(available_columns) < 2:
            raise ValueError("Barplot requires at least two columns")
    
    elif plot_type == 'lineplot':
        if len(available_columns) < 2:
            raise ValueError("Lineplot requires at least two columns")
        numeric_cols = df[available_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 1:
            raise ValueError("Lineplot requires at least one numeric column")
    
    elif plot_type == 'scatterplot':
        if len(available_columns) < 2:
            raise ValueError("Scatterplot requires at least two columns")
        numeric_cols = df[available_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Scatterplot requires at least two numeric columns")
    
    elif plot_type == 'heatmap':
        numeric_cols = df[available_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Heatmap requires at least two numeric columns")
    
    elif plot_type == 'pairplot':
        numeric_cols = df[available_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Pairplot requires at least two numeric columns")

def generate_selected_plot(df: pd.DataFrame, columns: List[str], plot_type: str, output_dir: str = "static/plots") -> List[str]:
    """
    Generate plots based on selected columns and plot type
    """
    try:
        # Preprocess data
        df = preprocess_data(df, plot_type, columns)
        
        # Validate requirements
        validate_plot_requirements(df, plot_type, columns)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Turn off interactive mode
        plt.ioff()
        
        def unique_file(name: str) -> str:
            """Generate unique filename"""
            return os.path.join(output_dir, f"{uuid.uuid4().hex[:6]}_{name}.png")
        
        def label_axes(ax, x_label: Optional[str], y_label: Optional[str], title: str):
            """Label axes and set title"""
            if x_label:
                ax.set_xlabel(x_label, fontsize=12)
            if y_label:
                ax.set_ylabel(y_label, fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Handle pairplot separately as it creates its own figure
        if plot_type == "pairplot":
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                # Limit to first 6 columns for performance
                plot_cols = numeric_cols[:6].tolist()
                g = sns.pairplot(df[plot_cols], diag_kind='hist', height=2.5)
                g.fig.suptitle('Pairplot', y=1.02, fontsize=16, fontweight='bold')
                g.fig.tight_layout()
                
                f = unique_file("pairplot")
                g.savefig(f, dpi=300, bbox_inches='tight')
                plt.close(g.fig)
                return [os.path.basename(f)]
            else:
                raise ValueError("Pairplot requires at least two numeric columns")
        
        # Create figure for other plot types
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Get column names for plotting
        x = columns[0] if len(columns) > 0 else None
        y = columns[1] if len(columns) > 1 else None
        
        try:
            if plot_type == "histogram":
                numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    ax.hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7, color='skyblue')
                    label_axes(ax, col, "Frequency", f"Histogram of {col}")
                else:
                    raise ValueError("No numeric columns available for histogram")
            
            elif plot_type == "boxplot":
                numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    ax.boxplot(df[col].dropna(), patch_artist=True, 
                             boxprops=dict(facecolor='lightblue', alpha=0.7))
                    label_axes(ax, col, "Value", f"Boxplot of {col}")
                else:
                    raise ValueError("No numeric columns available for boxplot")
            
            elif plot_type == "countplot":
                if x in df.columns:
                    sns.countplot(data=df, x=x, ax=ax, palette='viridis')
                    label_axes(ax, x, "Count", f"Countplot of {x}")
                else:
                    raise ValueError(f"Column {x} not found in dataset")
            
            elif plot_type == "barplot":
                if x in df.columns and y in df.columns:
                    # For barplot, we need categorical x and numeric y
                    if df[x].dtype == 'object' and df[y].dtype in ['int64', 'float64']:
                        sns.barplot(data=df, x=x, y=y, ax=ax, palette='viridis')
                        label_axes(ax, x, y, f"Barplot: {x} vs {y}")
                    else:
                        # Try to aggregate if both are numeric
                        if df[x].dtype in ['int64', 'float64'] and df[y].dtype in ['int64', 'float64']:
                            agg_data = df.groupby(x)[y].mean().reset_index()
                            sns.barplot(data=agg_data, x=x, y=y, ax=ax, palette='viridis')
                            label_axes(ax, x, f"Mean {y}", f"Barplot: {x} vs Mean {y}")
                        else:
                            raise ValueError("Barplot requires categorical x-axis and numeric y-axis")
                else:
                    raise ValueError("Both x and y columns are required for barplot")
            
            elif plot_type == "lineplot":
                if x in df.columns and y in df.columns:
                    numeric_cols = [col for col in [x, y] if df[col].dtype in ['int64', 'float64']]
                    if len(numeric_cols) >= 1:
                        # Sort by x if it's numeric
                        if df[x].dtype in ['int64', 'float64']:
                            plot_df = df.sort_values(x)
                        else:
                            plot_df = df
                        sns.lineplot(data=plot_df, x=x, y=y, ax=ax, marker='o')
                        label_axes(ax, x, y, f"Lineplot: {x} vs {y}")
                    else:
                        raise ValueError("At least one numeric column is required for lineplot")
                else:
                    raise ValueError("Both x and y columns are required for lineplot")
            
            elif plot_type == "scatterplot":
                if x in df.columns and y in df.columns:
                    numeric_cols = [col for col in [x, y] if df[col].dtype in ['int64', 'float64']]
                    if len(numeric_cols) >= 2:
                        ax.scatter(df[x], df[y], alpha=0.6, s=50)
                        label_axes(ax, x, y, f"Scatterplot: {x} vs {y}")
                    else:
                        raise ValueError("Both columns must be numeric for scatterplot")
                else:
                    raise ValueError("Both x and y columns are required for scatterplot")
            
            elif plot_type == "heatmap":
                numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
                if len(numeric_cols) >= 2:
                    # Calculate correlation matrix
                    corr_matrix = df[numeric_cols].corr()
                    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                              square=True, ax=ax, fmt='.2f')
                    label_axes(ax, None, None, "Correlation Heatmap")
                else:
                    raise ValueError("At least two numeric columns are required for heatmap")
            
            else:
                raise ValueError(f"Unknown plot type: {plot_type}")
        
        except Exception as e:
            plt.close(fig)
            raise e
        
        # Save the plot
        f = unique_file(plot_type)
        fig.tight_layout()
        fig.savefig(f, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return [os.path.basename(f)]
        
    except Exception as e:
        print(f"Error generating plot: {e}")
        return []
