#!/usr/bin/env python3
"""
Yearly Activity Graph Generator for Plone GitHub Statistics

Generates visual graphs from yearly activity data to show development trends
and patterns in the Plone ecosystem over time.
"""

import pandas as pd
from pathlib import Path
import sys

# Try to import optional dependencies for graph generation
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime
    import seaborn as sns
    import numpy as np
    GRAPHING_AVAILABLE = True
except ImportError as e:
    GRAPHING_AVAILABLE = False
    missing_modules = []
    for module in ['matplotlib', 'seaborn', 'numpy']:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)


def setup_plot_style():
    """Set up consistent plot styling."""
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Set up matplotlib parameters
    plt.rcParams.update({
        'figure.figsize': (12, 8),
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.dpi': 100
    })


def load_yearly_data():
    """Load yearly activity statistics."""
    csv_file = "yearly-activity-statistics.csv"
    
    if not Path(csv_file).exists():
        print(f"❌ {csv_file} not found. Please run 'make yearly-activity' first.")
        return None
    
    df = pd.read_csv(csv_file)
    df['year_date'] = pd.to_datetime(df['year'], format='%Y')
    
    return df


def create_commits_trend_graph(df, output_dir="graphs"):
    """Create commits trend graph."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Commits trend
    ax.plot(df['year'], df['total_commits'], marker='o', linewidth=3, markersize=8, 
             color='#1f77b4', label='Total Commits')
    ax.fill_between(df['year'], df['total_commits'], alpha=0.3, color='#1f77b4')
    ax.set_ylabel('Total Commits', fontsize=14)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_title('Plone Ecosystem - Commits Over Time (2015-2024)', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12)
    
    # Format y-axis for commits
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    
    # Set x-axis to show all years
    years = df['year'].tolist()
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    
    # Add Plone milestone annotations
    milestones = [
        (2015, 'Plone 5'),
        (2018, 'Volto & REST API'),
        (2022, 'Plone 6')
    ]
    milestone_color = '#000000'  # Black color for all milestones
    
    for year, label in milestones:
        if year in df['year'].values:
            commits_value = df[df['year'] == year]['total_commits'].iloc[0]
            y_min, y_max = ax.get_ylim()
            
            # Add white dashed vertical line within graph area
            ax.axvline(x=year, color='white', linestyle='--', alpha=0.8, linewidth=1, 
                      ymin=(y_min/y_max), ymax=(commits_value/y_max))
            
            # Add text annotation to the right of vertical line with bottom spacing
            ax.annotate(label, 
                       xy=(year, y_min + (y_max - y_min) * 0.08), 
                       xytext=(5, 0), textcoords='offset points',
                       fontsize=10, ha='left', fontweight='bold',
                       color=milestone_color)
    
    # Add annotations for key points
    max_commits_idx = df['total_commits'].idxmax()
    max_year = df.loc[max_commits_idx, 'year']
    max_commits = df.loc[max_commits_idx, 'total_commits']
    
    ax.annotate(f'{max_commits:,.0f}', 
                xy=(max_year, max_commits), 
                xytext=(max_year, max_commits + max_commits * 0.05),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=12, ha='center', fontweight='bold')
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/commits_trend.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_prs_trend_graph(df, output_dir="graphs"):
    """Create pull requests trend graph."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # PRs trend
    ax.plot(df['year'], df['total_pull_requests'], marker='s', linewidth=3, markersize=8, 
             color='#ff7f0e', label='Total Pull Requests')
    ax.fill_between(df['year'], df['total_pull_requests'], alpha=0.3, color='#ff7f0e')
    ax.set_ylabel('Total Pull Requests', fontsize=14)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_title('Plone Ecosystem - Pull Requests Over Time (2015-2024)', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12)
    
    # Format y-axis for PRs
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    # Add trend line
    z = np.polyfit(df['year'], df['total_pull_requests'], 1)
    p = np.poly1d(z)
    ax.plot(df['year'], p(df['year']), "--", color='red', alpha=0.8, linewidth=2, 
            label=f'Trend Line (slope: {z[0]:,.0f} PRs/year)')
    ax.legend(fontsize=12)
    
    # Set x-axis to show all years
    years = df['year'].tolist()
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    
    # Add Plone milestone annotations
    milestones = [
        (2015, 'Plone 5'),
        (2018, 'Volto & REST API'),
        (2022, 'Plone 6')
    ]
    milestone_color = '#000000'  # Black color for all milestones
    
    for year, label in milestones:
        if year in df['year'].values:
            prs_value = df[df['year'] == year]['total_pull_requests'].iloc[0]
            y_min, y_max = ax.get_ylim()
            
            # Add white dashed vertical line within graph area
            ax.axvline(x=year, color='white', linestyle='--', alpha=0.8, linewidth=1, 
                      ymin=(y_min/y_max), ymax=(prs_value/y_max))
            
            # Add text annotation to the right of vertical line with bottom spacing
            ax.annotate(label, 
                       xy=(year, y_min + (y_max - y_min) * 0.08), 
                       xytext=(5, 0), textcoords='offset points',
                       fontsize=10, ha='left', fontweight='bold',
                       color=milestone_color)
    
    # Add annotations for key points
    max_prs_idx = df['total_pull_requests'].idxmax()
    max_year = df.loc[max_prs_idx, 'year']
    max_prs = df.loc[max_prs_idx, 'total_pull_requests']
    
    ax.annotate(f'{max_prs:,.0f}', 
                xy=(max_year, max_prs), 
                xytext=(max_year, max_prs + max_prs * 0.05),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=12, ha='center', fontweight='bold')
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/pull_requests_trend.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_commits_prs_trend_graph(df, output_dir="graphs"):
    """Create combined commits and PRs trend graph."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Commits trend
    ax1.plot(df['year'], df['total_commits'], marker='o', linewidth=2, markersize=6, 
             color='#1f77b4', label='Commits')
    ax1.fill_between(df['year'], df['total_commits'], alpha=0.3, color='#1f77b4')
    ax1.set_ylabel('Total Commits')
    ax1.set_title('Plone Ecosystem Development Activity (2015-2024)', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Format y-axis for commits
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    # PRs trend
    ax2.plot(df['year'], df['total_pull_requests'], marker='s', linewidth=2, markersize=6, 
             color='#ff7f0e', label='Pull Requests')
    ax2.fill_between(df['year'], df['total_pull_requests'], alpha=0.3, color='#ff7f0e')
    ax2.set_ylabel('Total Pull Requests')
    ax2.set_xlabel('Year')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Format y-axis for PRs
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    
    # Add Plone milestone annotations
    milestones = [
        (2015, 'Plone 5'),
        (2018, 'Volto & REST API'),
        (2022, 'Plone 6')
    ]
    milestone_color = '#000000'  # Black color for all milestones
    
    for year, label in milestones:
        if year in df['year'].values:
            commits_value = df[df['year'] == year]['total_commits'].iloc[0]
            prs_value = df[df['year'] == year]['total_pull_requests'].iloc[0]
            
            # Get y-axis limits for both subplots
            y_min1, y_max1 = ax1.get_ylim()
            y_min2, y_max2 = ax2.get_ylim()
            
            # Add white dashed vertical lines within graph areas
            ax1.axvline(x=year, color='white', linestyle='--', alpha=0.8, linewidth=1, 
                       ymin=(y_min1/y_max1), ymax=(commits_value/y_max1))
            ax2.axvline(x=year, color='white', linestyle='--', alpha=0.8, linewidth=1, 
                       ymin=(y_min2/y_max2), ymax=(prs_value/y_max2))
            
            # Add text annotations to the right of vertical lines with bottom spacing
            ax1.annotate(label, 
                        xy=(year, y_min1 + (y_max1 - y_min1) * 0.08), 
                        xytext=(5, 0), textcoords='offset points',
                        fontsize=9, ha='left', fontweight='bold',
                        color=milestone_color)
    
    # Set x-axis to show all years
    years = df['year'].tolist()
    ax2.set_xticks(years)
    ax2.set_xticklabels(years, rotation=45)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/commits_prs_combined_trend.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_pr_adoption_graph(df, output_dir="graphs"):
    """Create PR adoption trend graph."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot PR to commit ratio
    ax.plot(df['year'], df['pr_to_commit_ratio'], marker='o', linewidth=3, markersize=8, 
            color='#2ca02c', label='PR/Commit Ratio (%)')
    ax.fill_between(df['year'], df['pr_to_commit_ratio'], alpha=0.3, color='#2ca02c')
    
    ax.set_ylabel('PR/Commit Ratio (%)')
    ax.set_xlabel('Year')
    ax.set_title('Pull Request Adoption in Plone Development (2015-2024)', 
                fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add trend line
    z = np.polyfit(df['year'], df['pr_to_commit_ratio'], 1)
    p = np.poly1d(z)
    ax.plot(df['year'], p(df['year']), "--", color='red', alpha=0.8, linewidth=2, 
            label=f'Trend Line (slope: {z[0]:.1f}%/year)')
    ax.legend()
    
    # Set x-axis to show all years
    years = df['year'].tolist()
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45)
    
    # Add annotations for key points
    max_ratio_idx = df['pr_to_commit_ratio'].idxmax()
    max_year = df.loc[max_ratio_idx, 'year']
    max_ratio = df.loc[max_ratio_idx, 'pr_to_commit_ratio']
    
    ax.annotate(f'{max_ratio:.1f}%', 
                xy=(max_year, max_ratio), 
                xytext=(max_year, max_ratio + 3),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, ha='center')
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/pr_adoption_trend.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_ecosystem_growth_graph(df, output_dir="graphs"):
    """Create ecosystem growth graph (contributors, orgs, repos)."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    
    # Contributors
    ax1.plot(df['year'], df['total_contributors'], marker='o', linewidth=2, markersize=6, 
             color='#d62728', label='Contributors')
    ax1.fill_between(df['year'], df['total_contributors'], alpha=0.3, color='#d62728')
    ax1.set_ylabel('Total Contributors')
    ax1.set_title('Plone Ecosystem Growth Metrics (2015-2024)', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Organizations
    ax2.plot(df['year'], df['total_organisations'], marker='s', linewidth=2, markersize=6, 
             color='#9467bd', label='Organizations')
    ax2.fill_between(df['year'], df['total_organisations'], alpha=0.3, color='#9467bd')
    ax2.set_ylabel('Total Organizations')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Repositories
    ax3.plot(df['year'], df['unique_repositories'], marker='^', linewidth=2, markersize=6, 
             color='#8c564b', label='Active Repositories')
    ax3.fill_between(df['year'], df['unique_repositories'], alpha=0.3, color='#8c564b')
    ax3.set_ylabel('Active Repositories')
    ax3.set_xlabel('Year')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Set x-axis to show all years
    years = df['year'].tolist()
    ax3.set_xticks(years)
    ax3.set_xticklabels(years, rotation=45)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/ecosystem_growth.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_growth_rates_heatmap(df, output_dir="graphs"):
    """Create growth rates heatmap."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Prepare data for heatmap
    growth_data = df[['year', 'commits_growth', 'prs_growth', 'contributors_growth', 'orgs_growth']].copy()
    growth_data = growth_data.dropna()  # Remove first year with no growth data
    
    # Rename columns for better display
    growth_data.columns = ['Year', 'Commits Growth', 'PRs Growth', 'Contributors Growth', 'Orgs Growth']
    
    # Set year as index and transpose for better heatmap layout
    growth_data = growth_data.set_index('Year').T
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create heatmap
    sns.heatmap(growth_data, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
                ax=ax, cbar_kws={'label': 'Growth Rate (%)'})
    
    ax.set_title('Year-over-Year Growth Rates in Plone Development (2016-2024)', 
                fontsize=16, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Metric')
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/growth_rates_heatmap.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_productivity_metrics_graph(df, output_dir="graphs"):
    """Create productivity metrics graph."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Commits per contributor
    ax1.plot(df['year'], df['commits_per_contributor'], marker='o', linewidth=2, markersize=6, 
             color='#17becf', label='Commits per Contributor')
    ax1.fill_between(df['year'], df['commits_per_contributor'], alpha=0.3, color='#17becf')
    ax1.set_ylabel('Commits per Contributor')
    ax1.set_title('Developer Productivity Metrics (2015-2024)', fontsize=16, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # PRs per contributor
    ax2.plot(df['year'], df['prs_per_contributor'], marker='s', linewidth=2, markersize=6, 
             color='#e377c2', label='PRs per Contributor')
    ax2.fill_between(df['year'], df['prs_per_contributor'], alpha=0.3, color='#e377c2')
    ax2.set_ylabel('PRs per Contributor')
    ax2.set_xlabel('Year')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Set x-axis to show all years
    years = df['year'].tolist()
    ax2.set_xticks(years)
    ax2.set_xticklabels(years, rotation=45)
    
    plt.tight_layout()
    
    output_file = f"{output_dir}/productivity_metrics.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def create_combined_overview_graph(df, output_dir="graphs"):
    """Create a combined overview graph with key metrics."""
    Path(output_dir).mkdir(exist_ok=True)
    
    fig = plt.figure(figsize=(16, 12))
    
    # Create a 2x3 grid
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Commits and PRs (spans top row)
    ax1 = fig.add_subplot(gs[0, :])
    line1 = ax1.plot(df['year'], df['total_commits'], marker='o', linewidth=2, 
                     color='#1f77b4', label='Commits')
    ax1.set_ylabel('Total Commits', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    
    ax1_twin = ax1.twinx()
    line2 = ax1_twin.plot(df['year'], df['total_pull_requests'], marker='s', linewidth=2, 
                          color='#ff7f0e', label='Pull Requests')
    ax1_twin.set_ylabel('Total Pull Requests', color='#ff7f0e')
    ax1_twin.tick_params(axis='y', labelcolor='#ff7f0e')
    
    ax1.set_title('Commits vs Pull Requests Over Time', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    # 2. PR Adoption Rate
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(df['year'], df['pr_to_commit_ratio'], marker='o', linewidth=2, 
             color='#2ca02c', label='PR/Commit Ratio')
    ax2.set_ylabel('PR/Commit Ratio (%)')
    ax2.set_title('PR Adoption Trend', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Contributors
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(df['year'], df['total_contributors'], marker='o', linewidth=2, 
             color='#d62728', label='Contributors')
    ax3.set_ylabel('Total Contributors')
    ax3.set_title('Contributor Growth', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Organizations
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.plot(df['year'], df['total_organisations'], marker='s', linewidth=2, 
             color='#9467bd', label='Organizations')
    ax4.set_ylabel('Total Organizations')
    ax4.set_xlabel('Year')
    ax4.set_title('Organizational Growth', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Productivity
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.plot(df['year'], df['commits_per_contributor'], marker='^', linewidth=2, 
             color='#17becf', label='Commits/Contributor')
    ax5.set_ylabel('Commits per Contributor')
    ax5.set_xlabel('Year')
    ax5.set_title('Developer Productivity', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # Set x-axis formatting for all subplots
    for ax in [ax1, ax2, ax3, ax4, ax5]:
        years = df['year'].tolist()
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=45)
    
    # Main title
    fig.suptitle('Plone Ecosystem Development Overview (2015-2024)', 
                fontsize=18, fontweight='bold', y=0.98)
    
    output_file = f"{output_dir}/yearly_activity_overview.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file


def main():
    """Main execution function."""
    print("Plone Yearly Activity Graph Generator")
    print("=" * 40)
    
    # Setup
    setup_plot_style()
    
    # Load data
    print("Loading yearly activity data...")
    df = load_yearly_data()
    
    if df is None:
        return 1
    
    print(f"✅ Loaded data for {len(df)} years: {df['year'].min()}-{df['year'].max()}")
    
    # Create output directory
    output_dir = "graphs"
    Path(output_dir).mkdir(exist_ok=True)
    
    # Generate graphs
    print("\nGenerating graphs...")
    
    graphs = []
    
    print("  📊 Creating commits trend graph...")
    graphs.append(create_commits_trend_graph(df, output_dir))
    
    print("  📊 Creating pull requests trend graph...")
    graphs.append(create_prs_trend_graph(df, output_dir))
    
    print("  📊 Creating combined commits and PRs trend graph...")
    graphs.append(create_commits_prs_trend_graph(df, output_dir))
    
    print("  📈 Creating PR adoption graph...")
    graphs.append(create_pr_adoption_graph(df, output_dir))
    
    print("  🌱 Creating ecosystem growth graph...")
    graphs.append(create_ecosystem_growth_graph(df, output_dir))
    
    print("  🔥 Creating growth rates heatmap...")
    graphs.append(create_growth_rates_heatmap(df, output_dir))
    
    print("  ⚡ Creating productivity metrics graph...")
    graphs.append(create_productivity_metrics_graph(df, output_dir))
    
    print("  🎯 Creating combined overview graph...")
    graphs.append(create_combined_overview_graph(df, output_dir))
    
    # Summary
    print(f"\n✅ Generated {len(graphs)} graphs in '{output_dir}/' directory:")
    for graph in graphs:
        print(f"  - {graph}")
    
    print(f"\n🎉 Graph generation completed!")
    print(f"   View graphs: open {output_dir}/")
    
    return 0


if __name__ == "__main__":
    exit(main())