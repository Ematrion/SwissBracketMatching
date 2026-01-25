import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from visualisation import fmt


class DashboardVisualizer:
    def __init__(self, samples: list, fig_path: str = "figures"):
        self.samples = samples
        self.fig_path = fig_path
        
        # Extract unique values across all samples
        all_df = pd.concat(samples, ignore_index=True)
        self.systems = sorted(all_df['system'].unique())
        self.solvers = sorted(all_df['generator'].unique())
        self.models = sorted(all_df['population'].unique())
        self.seed_classes = sorted(all_df['seeding_class'].unique())
        
        # Define system colors (consistent across all plots)
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.systems)))
        self.system_colors = {sys: colors[i] for i, sys in enumerate(self.systems)}

    def _plot_mean_variance_impl(self, ax_level, ax_seed, filtered_samples, selected, 
                                show_samples, metric_name, xlabel, ylabel=None):
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
            ax.set_title(f'{perspective.upper()} Perspective\n(Ideal: Bottom-Left)',
                    fontsize=12)
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
            plt.tight_layout(rect=[0, 0.05, 1, 0.96])
            
            # Store figure for saving
            state['fig'] = fig
            
            plt.show()

    # --- DashBoard Interface --- #
    def plot_utility_loss_robustness(self):
        """Mean vs Variance: Utility Loss"""
        self._create_interactive_plot(
            lambda ax_l, ax_s, fs, sel, ss: self._plot_mean_variance_impl(
                ax_l, ax_s, fs, sel, ss, 
                'utility_loss', 
                'Mean Utility Loss', 
                'Std Dev Utility Loss'
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
                'Std Dev Top-8 Precision'
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
                'Std Dev Winner Rank'
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
                'Std Dev Rank Difference'
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
                'Std Dev Winner Rank (Last Round)'
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
                'Std Dev Rank Difference (Last Round)'
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
                'Std Dev Upset Rate'
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
                'Std Dev Frustration Count'
            ),
            'Frustration Robustness'
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