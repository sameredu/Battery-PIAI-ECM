import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for plotting
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, linregress, f_oneway, kruskal
from sklearn.preprocessing import MinMaxScaler

from src.config import FIGURES_DIR, TABLES_DIR, STAT_TESTS_CSV, REGRESSION_RESULTS_CSV, COMBINED_CLEANED_CSV

def correlation_analysis(x, y):
    """
    Computes Pearson correlation coefficient and p-value.
    Matches the requested statistics_analysis template.
    """
    r, p = pearsonr(x, y)
    return r, p

def generate_pipeline_flowchart():
    """
    Generates a flow diagram of the pipeline and saves it as fig1_pipeline.png.
    """
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.axis('off')
    
    box_props = dict(boxstyle="round,pad=0.6", fc="#ecf3fe", ec="#1a73e8", lw=2.0)
    
    ax.text(0.13, 0.5, "Raw NASA Data\n(B0005, B0006,\nB0007, B0018)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#174ea6', bbox=box_props)
            
    ax.text(0.38, 0.5, "2-RC Circuit Model\nIdentification\n(Trust-Region LSQ)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#174ea6', bbox=box_props)
            
    ax.text(0.63, 0.5, "Feature Engineering\n& Statistics\n(tau = R * C)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#174ea6', bbox=box_props)
            
    ax.text(0.87, 0.5, "RUL Prediction\n(Random Forest\nLOBO Validation)", 
            ha='center', va='center', fontsize=9, fontweight='bold', color='#174ea6', bbox=box_props)
            
    arrow_props = dict(arrowstyle="->", color='#1a73e8', lw=2.5, mutation_scale=15)
    ax.annotate('', xy=(0.25, 0.5), xytext=(0.20, 0.5), arrowprops=arrow_props)
    ax.annotate('', xy=(0.50, 0.5), xytext=(0.47, 0.5), arrowprops=arrow_props)
    ax.annotate('', xy=(0.75, 0.5), xytext=(0.72, 0.5), arrowprops=arrow_props)
    
    plt.title("Cycle-Resolved Physics-Informed AI Battery Degradation Pipeline", fontsize=12, fontweight='bold', pad=10, color='#202124')
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "fig1_pipeline.png"), dpi=300)
    plt.close()

def run_statistical_pipeline(df):
    """
    Runs full statistical analysis:
    - Linear regression of params vs CycleIndex
    - ANOVA and Kruskal-Wallis across cells
    - Generates 300dpi plots (trends, boxplots, heatmap, pairplot, radar)
    """
    print("Running statistical analysis pipeline...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)
    
    # Generate flowchart
    generate_pipeline_flowchart()
    
    # Save a cleaned copy of the combined params
    df.to_csv(COMBINED_CLEANED_CSV, index=False)
    
    # Identify numerical parameters for analysis
    params = ['R0', 'R1', 'C1', 'R2', 'C2', 'Voc_slope', 'Voc_intercept', 'Capacity_Ah']
    
    # Ensure columns exist in DataFrame
    params = [p for p in params if p in df.columns]
    
    # ----------------- 1. Trend analysis & Linear Regression -----------------
    print("Fitting linear regressions...")
    reg_rows = []
    sns.set(style="whitegrid", context="talk", font_scale=1.0)
    
    for p in params:
        plt.figure(figsize=(10, 5.5))
        ax = plt.gca()
        unique_bats = df['Battery'].unique()
        palette = sns.color_palette("tab10", n_colors=len(unique_bats))
        
        for i, bat in enumerate(unique_bats):
            sub = df[df['Battery'] == bat].dropna(subset=['CycleIndex', p])
            if len(sub) < 2:
                continue
                
            ax.scatter(sub['CycleIndex'], sub[p], label=bat, alpha=0.7, s=36, color=palette[i])
            
            slope, intercept, r_val, p_val, stderr = linregress(sub['CycleIndex'], sub[p])
            reg_rows.append({
                'Parameter': p,
                'Battery': bat,
                'slope': slope,
                'intercept': intercept,
                'R2': r_val**2,
                'pval': p_val,
                'n': len(sub)
            })
            
            x_line = np.linspace(sub['CycleIndex'].min(), sub['CycleIndex'].max(), 100)
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, color=palette[i], linewidth=1.8)
            
            txt = f"{bat}: y={slope:.3e}x+{intercept:.3e}, R²={r_val**2:.3f}"
            ax.text(x_line[-1] * 1.01, y_line[-1], txt, color=palette[i], fontsize=8, va='center')
            
        ax.set_xlabel("Cycle Index")
        ax.set_ylabel("Capacity (Ah)" if p == 'Capacity_Ah' else p)
        ax.set_title(f"{p} vs Cycle Index (scatter + linear fit)")
        ax.set_xlim(right=ax.get_xlim()[1] * 1.35)  # Make room for text labels
        ax.legend(title="Battery", loc='upper left', bbox_to_anchor=(1.02, 1.0), fontsize=9)
        plt.tight_layout()
        
        # Save standard names
        plt.savefig(os.path.join(FIGURES_DIR, f"trend_{p}_regression.png"), dpi=300)
        
        # Keep copy with user structure names
        if p == 'R0':
            plt.savefig(os.path.join(FIGURES_DIR, "fig2_r0_trend.png"), dpi=300)
        elif p == 'Capacity_Ah':
            plt.savefig(os.path.join(FIGURES_DIR, "fig3_capacity.png"), dpi=300)
            
        plt.close()
        
    df_reg = pd.DataFrame(reg_rows)
    df_reg.to_csv(REGRESSION_RESULTS_CSV, index=False)
    # Save a copy as table2_feature_importance placeholder or table summary
    df_reg.to_csv(os.path.join(TABLES_DIR, "regression_results.csv"), index=False)
    
    # ----------------- 2. Boxplots -----------------
    print("Generating boxplots...")
    for p in params:
        plt.figure(figsize=(7, 4.5))
        sns.boxplot(data=df, x='Battery', y=p, palette="Set2", hue='Battery', legend=False)
        sns.stripplot(data=df, x='Battery', y=p, color='k', size=3, jitter=True, alpha=0.6)
        plt.title(f"Distribution of {p} by Battery")
        plt.ylabel("Capacity (Ah)" if p == 'Capacity_Ah' else p)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, f"box_{p}.png"), dpi=300)
        plt.close()
        
    # ----------------- 3. Heatmap -----------------
    print("Generating correlation heatmap...")
    corr = df[params].corr()
    plt.figure(figsize=(8.5, 7.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True, linewidths=0.5)
    plt.title("Correlation Matrix: ECM Parameters & Capacity")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "correlation_heatmap.png"), dpi=300)
    plt.savefig(os.path.join(FIGURES_DIR, "fig4_heatmap.png"), dpi=300)
    plt.close()
    
    # ----------------- 4. Pairplot -----------------
    print("Generating pairplot...")
    sample_df = df.sample(n=min(200, len(df)), random_state=42)
    pp = sns.pairplot(sample_df, vars=params, hue='Battery', diag_kind='kde', plot_kws={'s': 20, 'alpha': 0.7})
    pp.savefig(os.path.join(FIGURES_DIR, "pairplot.png"), dpi=300)
    plt.close()
    
    # ----------------- 5. Radar Chart (Normalized) -----------------
    print("Generating radar chart...")
    avg = df.groupby('Battery')[params].mean()
    num_vars = len(params)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    plt.figure(figsize=(7, 7))
    ax_polar = plt.subplot(111, polar=True)
    
    # Normalize averages between 0 and 1 for visual clarity
    scaler = MinMaxScaler()
    avg_scaled = pd.DataFrame(scaler.fit_transform(avg), columns=params, index=avg.index)
    
    for bat, row in avg_scaled.iterrows():
        vals = row.tolist()
        vals += vals[:1]
        ax_polar.plot(angles, vals, linewidth=2, linestyle='solid', label=bat)
        ax_polar.fill(angles, vals, alpha=0.08)
        
    plt.xticks(angles[:-1], params, size=9)
    plt.title("Average ECM Signature per Battery (Normalized)", y=1.05)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "radar_signature.png"), dpi=300)
    plt.savefig(os.path.join(FIGURES_DIR, "fig5_radar.png"), dpi=300)
    plt.close()
    
    # ----------------- 6. Statistical tests (ANOVA & Kruskal-Wallis) -----------------
    print("Performing ANOVA and Kruskal-Wallis tests...")
    stats_rows = []
    for p in params:
        groups = [g[p].dropna().values for _, g in df.groupby('Battery') if not g[p].dropna().empty]
        if len(groups) > 1:
            try:
                F, p_anova = f_oneway(*groups)
            except Exception:
                F, p_anova = np.nan, np.nan
            try:
                H, p_kruskal = kruskal(*groups)
            except Exception:
                H, p_kruskal = np.nan, np.nan
            stats_rows.append({
                'parameter': p,
                'ANOVA_F': F,
                'ANOVA_p': p_anova,
                'Kruskal_H': H,
                'Kruskal_p': p_kruskal
            })
        else:
            stats_rows.append({
                'parameter': p,
                'ANOVA_F': np.nan,
                'ANOVA_p': np.nan,
                'Kruskal_H': np.nan,
                'Kruskal_p': np.nan
            })
            
    df_stats = pd.DataFrame(stats_rows)
    df_stats.to_csv(STAT_TESTS_CSV, index=False)
    # Also save as table1_anova.csv for user consistency
    df_stats.to_csv(os.path.join(TABLES_DIR, "table1_anova.csv"), index=False)
    
    print("Statistical analysis completed successfully.")
