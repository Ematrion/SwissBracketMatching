import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from visualisation import fmt


class DashboardVisualizer:
    def __init__(self, samples: list, fig_path: str = "figures", swiss_systems: list | None = None):
        self.samples = samples
        self.fig_path = fig_path

        # Extract unique values across all samples
        all_df = pd.concat(samples, ignore_index=True)
        self.systems = sorted(all_df['system'].unique())
        self.solvers = sorted(all_df['generator'].unique())
        self.models = sorted(all_df['population'].unique())
        self.seed_classes = sorted(all_df['seeding_class'].unique())

        # Swiss bracket systems for matching-specific plots
        self.swiss_systems = set(swiss_systems) if swiss_systems else set(self.systems)

        # Define system colors (consistent across all plots)
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.systems)))
        self.system_colors = {sys: colors[i] for i, sys in enumerate(self.systems)}

    def _plot_mean_variance_impl(self, ax_level, ax_seed, filtered_samples, selected,
                                show_samples, metric_name, xlabel, ylabel=None,
                                ideal_hint=None):
        """
        Generic implementation for mean vs variance scatter plots.

        Parameters:
        -----------
        metric_name : str
            Base metric name (without 'level_' or 'seed_' prefix)
        xlabel : str
            Label for x-axis (mean)
        ylabel : str, optional
            Label for y-axis (variance), defaults to same as xlabel with 'Std Dev' prefix
        ideal_hint : str, optional
            Hint shown in the subplot title, e.g. "Bottom-Left" or "Bottom-Right".
            If None, no hint is displayed.
        """
        if ylabel is None:
            ylabel = f'Std Dev {xlabel}'
        
        for perspective, ax in [('level', ax_level), ('seed', ax_seed)]:
            metric = f'{perspective}_{metric_name}'
            
            if show_samples:
                # Plot each sample as individual dots
                for sample_df in filtered_samples:
                    stats = sample_df.groupby('system')[metric].agg(['mean', 'std'])
                    
                    for system in selected['systems']:
                        if system in stats.index:
                            ax.scatter(stats.loc[system, 'mean'],
                                    stats.loc[system, 'std'],
                                    s=50, alpha=0.3,
                                    color=self.system_colors[system])
            else:
                # Aggregate all samples
                all_filtered = pd.concat(filtered_samples)
                stats = all_filtered.groupby('system')[metric].agg(['mean', 'std'])
                
                for system in selected['systems']:
                    if system in stats.index:
                        ax.scatter(stats.loc[system, 'mean'],
                                stats.loc[system, 'std'],
                                s=200, alpha=0.7,
                                color=self.system_colors[system],
                                label=system)
                        ax.annotate(system,
                                (stats.loc[system, 'mean'],
                                stats.loc[system, 'std']),
                                xytext=(5, 5),
                                textcoords='offset points',
                                fontsize=9)
            
            # Add legend
            if show_samples:
                for system in selected['systems']:
                    ax.scatter([], [], s=100, alpha=0.7,
                            color=self.system_colors[system],
                            label=system)
            
            ax.set_xlabel(xlabel, fontsize=11)
            ax.set_ylabel(ylabel, fontsize=11)
            title = f'{perspective.upper()} Perspective'
            if ideal_hint:
                title += f'\n(Ideal: {ideal_hint})'
            ax.set_title(title, fontsize=12)
            ax.grid(alpha=0.3)
            ax.legend(fontsize=9)

    # --- UI --- #
    def _create_ui_for_plot(self):
        """Create NEW independent UI for each plot."""
        filters = {}
        
        system_checks = [widgets.Checkbox(value=True, description=str(s)) 
                         for s in self.systems]
        filters['system'] = widgets.VBox([widgets.Label('Systems:'), *system_checks])
        
        solver_checks = [widgets.Checkbox(value=True, description=str(s)) 
                         for s in self.solvers]
        filters['solver'] = widgets.VBox([widgets.Label('Solvers:'), *solver_checks])
        
        model_checks = [widgets.Checkbox(value=True, description=str(m)) 
                        for m in self.models]
        filters['model'] = widgets.VBox([widgets.Label('Models:'), *model_checks])
        
        seed_class_checks = [widgets.Checkbox(value=True, description=str(sc)) 
                             for sc in self.seed_classes]
        filters['seed_class'] = widgets.VBox([widgets.Label('Seed Classes:'), *seed_class_checks])
        
        controls = {
            'show_samples': widgets.Checkbox(value=False, description='Show individual samples')
        }
        controls_ui = widgets.VBox([widgets.Label('Display Options:'), controls['show_samples']])
        
        ui = widgets.HBox([
            filters['system'], filters['solver'], filters['model'], 
            filters['seed_class'], controls_ui
        ])
        
        return ui, filters, controls
    
    def _create_interactive_plot(self, plot_func, title):
        """
        Generic interactive plot framework with caption and save functionality.
        """
        # Create INDEPENDENT UI for this plot
        ui, filters, controls = self._create_ui_for_plot()
        
        # Add save controls
        save_button = widgets.Button(
            description='Save PNG',
            button_style='success',
            icon='save'
        )
        
        filename_input = widgets.Text(
            value=f'{title.lower().replace(" ", "_")}.png',
            placeholder='filename.png',
            description='Filename:',
            style={'description_width': 'initial'}
        )
        
        save_ui = widgets.HBox([filename_input, save_button])
        
        output = widgets.Output()
        caption_output = widgets.Output()
        
        # Store state
        state = {
            'fig': None,
            'filters': filters,
            'controls': controls,
            'output': output,
            'caption_output': caption_output,
            'filename_input': filename_input,
            'plot_func': plot_func,
            'title': title
        }
        
        # Connect callbacks
        save_button.on_click(lambda b: self._handle_save_click(state))
        
        for filter_group in filters.values():
            for cb in filter_group.children[1:]:
                cb.observe(lambda change: self._handle_plot_update(state), names='value')
        
        controls['show_samples'].observe(lambda change: self._handle_plot_update(state), names='value')
        
        # Initial plot
        self._handle_plot_update(state)
        
        # Display everything
        display(widgets.VBox([ui, save_ui, caption_output, output]))

    def _get_selected_from_filters(self, filters):
        """Extract selections from specific filter instances."""
        return {
            'systems': [self.systems[i] for i, cb in enumerate(filters['system'].children[1:]) if cb.value],
            'solvers': [self.solvers[i] for i, cb in enumerate(filters['solver'].children[1:]) if cb.value],
            'models': [self.models[i] for i, cb in enumerate(filters['model'].children[1:]) if cb.value],
            'seed_classes': [self.seed_classes[i] for i, cb in enumerate(filters['seed_class'].children[1:]) if cb.value]
        }    

    # --- Plots --- #
    def _generate_caption(self, selected, show_samples):
        """
        Generate caption text as two-line string for plot footer with bold labels.
        
        Parameters:
        -----------
        selected : dict
            Dictionary with keys: systems, solvers, models, seed_classes
        show_samples : bool
            Whether showing individual samples or aggregated
        
        Returns:
        --------
        str : Two-line caption text with LaTeX bold parameter names
        """
        # Escape values for LaTeX
        systems_str = fmt.escape_latex(', '.join(selected['systems']))
        solvers_str = fmt.escape_latex(', '.join(selected['solvers']))
        models_str = fmt.escape_latex(', '.join(selected['models']))
        seed_classes_str = fmt.escape_latex(', '.join(selected['seed_classes']))
        
        line1 = rf"$\mathbf{{Systems}}$: {systems_str}"
        line2 = (
            rf"$\mathbf{{Solvers}}$: {solvers_str} | "
            rf"$\mathbf{{Models}}$: {models_str} | "
            rf"$\mathbf{{Seed\ Classes}}$: {seed_classes_str}"
        )
        return f"{line1}\n{line2}"
    
    def _handle_plot_update(self, state):
        """Handle plot update when filters change."""
        with state['output']:
            state['output'].clear_output(wait=True)
            
            selected = self._get_selected_from_filters(state['filters'])
            if not all([selected['systems'], selected['solvers'], 
                    selected['models'], selected['seed_classes']]):
                print("Select at least one option from each category")
                return
            
            show_samples = state['controls']['show_samples'].value
            
            # Filter data
            filtered_samples = []
            for df in self.samples:
                filtered = df[
                    (df['system'].isin(selected['systems'])) &
                    (df['generator'].isin(selected['solvers'])) &
                    (df['population'].isin(selected['models'])) &
                    (df['seeding_class'].isin(selected['seed_classes']))
                ]
                filtered_samples.append(filtered)
            
            # Create plot
            fig, (ax_level, ax_seed) = plt.subplots(1, 2, figsize=(16, 7))
            state['plot_func'](ax_level, ax_seed, filtered_samples, selected, show_samples)
            
            mode = "Individual Samples" if show_samples else "Aggregated"
            fig.suptitle(f'{state["title"]} - {mode}\n'
                    f'Samples: {len(self.samples)} | '
                    f'Models: {len(selected["models"])} | '
                    f'Seed Classes: {len(selected["seed_classes"])}',
                    fontsize=13)
    
            # Add caption as footer using the dedicated method
            caption_text = self._generate_caption(selected, show_samples)
            fig.text(0.5, 0.01, caption_text, ha='center', fontsize=10, 
                    style='italic', weight='normal')

            # !!! hard coded 2 lines spaces for caption
            plt.tight_layout(rect=[0, 0.05, 1, 0.96]) #type: ignore
            
            # Store figure for saving
            state['fig'] = fig
            
            plt.show()

    # --- DashBoard Interface --- #
    # NOTE: Bunch or redundant code that can be refactor
    # NOTE: lambda usage is odd -> functool.partial ?
    # NOTE: global var with figure textual infos
    
    def plot_utility_loss_robustness(self):
        """Mean vs Variance: Utility Loss"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'utility_loss',
                'Mean Utility Loss',
                'Std Dev Utility Loss',
                ideal_hint='Bottom-Left'
            ),
            'Utility Loss Robustness'
        )

    def plot_top8_precision(self):
        """Mean vs Variance: Top-8 Precision"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'top8_precision',
                'Mean Top-8 Precision',
                'Std Dev Top-8 Precision',
                ideal_hint='Bottom-Right'
            ),
            'Top-8 Precision Robustness'
        )

    def plot_fairness(self):
        """Mean vs Variance: Fairness (Average Winner Rank)"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'fairness',
                'Mean Winner Rank',
                'Std Dev Winner Rank',
                ideal_hint='Bottom-Left'
            ),
            'Fairness Robustness'
        )

    def plot_balance(self):
        """Mean vs Variance: Balance (Average Rank Difference)"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'balance',
                'Mean Rank Difference',
                'Std Dev Rank Difference',
                ideal_hint='Bottom-Left'
            ),
            'Balance Robustness'
        )

    def plot_last_round_fairness(self):
        """Mean vs Variance: Last Round Fairness"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'last_round_fairness',
                'Mean Winner Rank (Last Round)',
                'Std Dev Winner Rank (Last Round)',
                ideal_hint='Bottom-Left'
            ),
            'Last Round Fairness Robustness'
        )

    def plot_last_round_balance(self):
        """Mean vs Variance: Last Round Balance"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'last_round_balance',
                'Mean Rank Difference (Last Round)',
                'Std Dev Rank Difference (Last Round)',
                ideal_hint='Bottom-Left'
            ),
            'Last Round Balance Robustness'
        )

    def plot_upset_rate(self):
        """Mean vs Variance: Upset Rate"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'upset_rate',
                'Mean Upset Rate',
                'Std Dev Upset Rate',
                ideal_hint='Bottom-Left'
            ),
            'Upset Rate Robustness'
        )

    def plot_frustration(self):
        """Mean vs Variance: Frustration Count"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss,
                'frustration',
                'Mean Frustration Count',
                'Std Dev Frustration Count',
                ideal_hint='Bottom-Left'
            ),
            'Frustration Robustness'
        )

    # --- Last Round Matching Plots (Swiss Bracket only) --- #
    def _filter_swiss_only(self, filtered_samples, selected):
        """Filter to Swiss bracket systems only."""
        swiss = [s for s in selected['systems'] if s in self.swiss_systems]
        if not swiss:
            return [], swiss
        return [df[df['system'].isin(swiss)] for df in filtered_samples], swiss

    def _plot_matching_histogram_impl(self, ax_level, ax_seed, filtered_samples, selected, show_samples):
        """Grouped histogram: matching index frequency per system."""
        filtered, swiss = self._filter_swiss_only(filtered_samples, selected)
        if not swiss:
            for ax in [ax_level, ax_seed]:
                ax.text(0.5, 0.5, 'No Swiss bracket systems selected',
                        ha='center', va='center', transform=ax.transAxes)
            return

        all_data = pd.concat(filtered, ignore_index=True)
        matching_indices = range(1, 16)  # 1-based index (1-15)
        bar_width = 0.8 / len(swiss)

        for perspective, ax in [('level', ax_level), ('seed', ax_seed)]:
            col = f'{perspective}_last_round_matching'
            if col not in all_data.columns:
                ax.text(0.5, 0.5, f'Column {col} not found',
                        ha='center', va='center', transform=ax.transAxes)
                continue

            for i, system in enumerate(swiss):
                sys_data = all_data[all_data['system'] == system][col].dropna()
                counts = sys_data.value_counts().reindex(matching_indices, fill_value=0)
                positions = np.array(list(matching_indices)) + i * bar_width
                ax.bar(positions, counts.values, width=bar_width, alpha=0.8,
                       color=self.system_colors[system], label=system)

            ax.set_xlabel('Matching Priority (1-15)', fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            ax.set_title(f'{perspective.upper()} Perspective', fontsize=12)
            ax.set_xticks(np.array(list(matching_indices)) + bar_width * (len(swiss) - 1) / 2)
            ax.set_xticklabels(list(matching_indices))
            ax.legend(fontsize=9)
            ax.grid(alpha=0.3, axis='y')

    def _plot_matching_heatmap_impl(self, ax_level, ax_seed, filtered_samples, selected, show_samples):
        """Heatmap: systems x matching indices, color = frequency %."""
        filtered, swiss = self._filter_swiss_only(filtered_samples, selected)
        if not swiss:
            for ax in [ax_level, ax_seed]:
                ax.text(0.5, 0.5, 'No Swiss bracket systems selected',
                        ha='center', va='center', transform=ax.transAxes)
            return

        all_data = pd.concat(filtered, ignore_index=True)
        matching_indices = list(range(1, 16))  # 1-based index (1-15)

        for perspective, ax in [('level', ax_level), ('seed', ax_seed)]:
            col = f'{perspective}_last_round_matching'
            if col not in all_data.columns:
                ax.text(0.5, 0.5, f'Column {col} not found',
                        ha='center', va='center', transform=ax.transAxes)
                continue

            matrix = []
            for system in swiss:
                sys_data = all_data[all_data['system'] == system][col].dropna()
                counts = sys_data.value_counts().reindex(matching_indices, fill_value=0)
                pct = counts / counts.sum() * 100 if counts.sum() > 0 else counts
                matrix.append(pct.values)

            im = ax.imshow(np.array(matrix), aspect='auto', cmap='YlOrRd')
            ax.set_xticks(range(len(matching_indices)))
            ax.set_xticklabels(matching_indices)
            ax.set_yticks(range(len(swiss)))
            ax.set_yticklabels(swiss)
            ax.set_xlabel('Matching Priority', fontsize=11)
            ax.set_ylabel('System', fontsize=11)
            ax.set_title(f'{perspective.upper()} Perspective', fontsize=12)
            plt.colorbar(im, ax=ax, label='Frequency %')

    def _plot_matching_stacked_impl(self, ax_level, ax_seed, filtered_samples, selected, show_samples):
        """Stacked bar: each bar = system, stacked by matching proportion."""
        filtered, swiss = self._filter_swiss_only(filtered_samples, selected)
        if not swiss:
            for ax in [ax_level, ax_seed]:
                ax.text(0.5, 0.5, 'No Swiss bracket systems selected',
                        ha='center', va='center', transform=ax.transAxes)
            return

        all_data = pd.concat(filtered, ignore_index=True)
        matching_indices = list(range(1, 16))  # 1-based index (1-15)
        cmap = plt.cm.viridis(np.linspace(0, 1, 15))

        for perspective, ax in [('level', ax_level), ('seed', ax_seed)]:
            col = f'{perspective}_last_round_matching'
            if col not in all_data.columns:
                ax.text(0.5, 0.5, f'Column {col} not found',
                        ha='center', va='center', transform=ax.transAxes)
                continue

            x = np.arange(len(swiss))
            bottom = np.zeros(len(swiss))

            for i, idx in enumerate(matching_indices):
                heights = []
                for system in swiss:
                    sys_data = all_data[all_data['system'] == system][col].dropna()
                    total = len(sys_data)
                    count = (sys_data == idx).sum()
                    heights.append(count / total * 100 if total > 0 else 0)
                ax.bar(x, heights, bottom=bottom, width=0.7, color=cmap[i], label=f'{idx}')
                bottom += heights

            ax.set_xticks(x)
            ax.set_xticklabels(swiss, rotation=30, ha='right')
            ax.set_xlabel('System', fontsize=11)
            ax.set_ylabel('Percentage', fontsize=11)
            ax.set_title(f'{perspective.upper()} Perspective', fontsize=12)
            ax.legend(title='Priority', bbox_to_anchor=(1.02, 1), loc='upper left',
                      fontsize=7, ncol=2)

    def plot_last_round_matching_histogram(self):
        """Histogram: matching index distribution per Swiss bracket system."""
        self._create_interactive_plot(
            self._plot_matching_histogram_impl,
            'Last Round Matching Distribution (Histogram)'
        )

    def plot_last_round_matching_heatmap(self):
        """Heatmap: matching index frequency by Swiss bracket system."""
        self._create_interactive_plot(
            self._plot_matching_heatmap_impl,
            'Last Round Matching Distribution (Heatmap)'
        )

    def plot_last_round_matching_stacked(self):
        """Stacked bar: matching proportion by Swiss bracket system."""
        self._create_interactive_plot(
            self._plot_matching_stacked_impl,
            'Last Round Matching Distribution (Stacked)'
        )

    def _plot_top6_preferred_impl(self, ax_level, ax_seed, filtered_samples, selected, show_samples):
        """Bar chart: percentage of top-6 preferred pairings (priority 1-6) per system."""
        filtered, swiss = self._filter_swiss_only(filtered_samples, selected)
        if not swiss:
            for ax in [ax_level, ax_seed]:
                ax.text(0.5, 0.5, 'No Swiss bracket systems selected',
                        ha='center', va='center', transform=ax.transAxes)
            return

        all_data = pd.concat(filtered, ignore_index=True)

        for perspective, ax in [('level', ax_level), ('seed', ax_seed)]:
            col = f'{perspective}_last_round_matching'
            if col not in all_data.columns:
                ax.text(0.5, 0.5, f'Column {col} not found',
                        ha='center', va='center', transform=ax.transAxes)
                continue

            percentages = []
            for system in swiss:
                sys_data = all_data[all_data['system'] == system][col].dropna()
                total = len(sys_data)
                # Top-6 preferred pairings are priorities 1-6 (1-based index)
                top6_count = ((sys_data >= 1) & (sys_data <= 6)).sum()
                pct = top6_count / total * 100 if total > 0 else 0
                percentages.append(pct)

            x = np.arange(len(swiss))
            bars = ax.bar(x, percentages, width=0.7, alpha=0.8,
                         color=[self.system_colors[s] for s in swiss])

            # Add percentage labels on bars
            for bar, pct in zip(bars, percentages):
                ax.annotate(f'{pct:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                           xytext=(0, 3), textcoords='offset points',
                           ha='center', va='bottom', fontsize=9)

            ax.set_xticks(x)
            ax.set_xticklabels(swiss, rotation=30, ha='right')
            ax.set_xlabel('System', fontsize=11)
            ax.set_ylabel('Percentage (%)', fontsize=11)
            ax.set_title(f'{perspective.upper()} Perspective\n(Top-6 Preferred Pairings)', fontsize=12)
            ax.set_ylim(0, 105)  # Leave room for labels
            ax.axhline(y=40, color='red', linestyle='--', alpha=0.5, label='Random baseline (6/15 ≈ 40%)')
            ax.legend(fontsize=9)
            ax.grid(alpha=0.3, axis='y')

    def plot_top6_preferred_pairings(self):
        """Bar chart: percentage of top-6 preferred pairings per Swiss bracket system."""
        self._create_interactive_plot(
            self._plot_top6_preferred_impl,
            'Top-6 Preferred Pairings Rate'
        )

    # --- Features --- #
    def _save_current_plot(self, fig, filename):
        """
        Save figure to PNG file.
        
        Parameters:
        -----------
        fig : matplotlib.figure.Figure
            Figure to save
        filename : str
            Output filename (will append .png if missing)
        
        Returns:
        --------
        tuple : (success: bool, message: str)
        """
        if fig is None:
            return False, "No plot to save. Generate a plot first."
        
        if not filename.endswith('.png'):
            filename += '.png'
        
        try:
            fig.savefig(self.fig_path + "/" +filename, dpi=300, bbox_inches='tight')
            return True, f"✓ Saved to: {filename}"
        except Exception as e:
            return False, f"✗ Error saving: {e}"
    
    def _handle_save_click(self, state):
        """Handle save button click."""
        success, message = self._save_current_plot(
            state['fig'], 
            state['filename_input'].value
        )
        print(message)