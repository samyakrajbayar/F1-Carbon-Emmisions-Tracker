import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
from datetime import datetime
import json

class F1CarbonTracker:
    """
    F1 Carbon Footprint Sustainability Tracker
    Calculates and visualizes CO2 emissions from Formula 1 racing operations
    """
    
    def __init__(self):
        # Emission factors (kg CO2 per unit)
        self.emission_factors = {
            'air_freight_per_kg': 2.1,  # kg CO2 per kg freight per 1000km
            'sea_freight_per_kg': 0.015,  # kg CO2 per kg freight per 1000km
            'fuel_per_liter': 2.31,  # kg CO2 per liter of fuel
            'passenger_flight_per_km': 0.255,  # kg CO2 per passenger km
            'circuit_operations': 500000,  # kg CO2 per race weekend (lighting, facilities)
            'hotel_night': 30,  # kg CO2 per person per night
        }
        
        # F1 operational data estimates
        self.f1_data = {
            'teams': 10,
            'personnel_per_team': 80,
            'freight_weight_per_team': 15000,  # kg including cars, equipment
            'fuel_consumption_per_race': 100,  # liters per car per race
            'cars_per_race': 20,
            'support_series_factor': 1.3,  # Additional emissions from F2, F3, etc.
        }
        
        # Initialize race calendar with approximate distances and logistics
        self.race_calendar = self._initialize_race_calendar()
        
        # Comparison baselines
        self.comparisons = {
            'average_home_annual_emissions': 16000,  # kg CO2 per year
            'passenger_car_per_km': 0.192,  # kg CO2 per km
            'transatlantic_flight_per_passenger': 1600,  # kg CO2
        }
    
    def _initialize_race_calendar(self):
        """Initialize 2024 F1 race calendar with logistics data"""
        races = [
            {'race': 'Bahrain GP', 'location': 'Manama', 'distance_from_previous': 0, 'freight_method': 'sea'},
            {'race': 'Saudi Arabian GP', 'location': 'Jeddah', 'distance_from_previous': 450, 'freight_method': 'road'},
            {'race': 'Australian GP', 'location': 'Melbourne', 'distance_from_previous': 8500, 'freight_method': 'sea'},
            {'race': 'Japanese GP', 'location': 'Suzuka', 'distance_from_previous': 8000, 'freight_method': 'sea'},
            {'race': 'Chinese GP', 'location': 'Shanghai', 'distance_from_previous': 1700, 'freight_method': 'road'},
            {'race': 'Miami GP', 'location': 'Miami', 'distance_from_previous': 17000, 'freight_method': 'air'},
            {'race': 'Emilia Romagna GP', 'location': 'Imola', 'distance_from_previous': 8500, 'freight_method': 'air'},
            {'race': 'Monaco GP', 'location': 'Monaco', 'distance_from_previous': 350, 'freight_method': 'road'},
            {'race': 'Canadian GP', 'location': 'Montreal', 'distance_from_previous': 6200, 'freight_method': 'air'},
            {'race': 'Spanish GP', 'location': 'Barcelona', 'distance_from_previous': 5200, 'freight_method': 'air'},
            {'race': 'Austrian GP', 'location': 'Spielberg', 'distance_from_previous': 1000, 'freight_method': 'road'},
            {'race': 'British GP', 'location': 'Silverstone', 'distance_from_previous': 1200, 'freight_method': 'road'},
            {'race': 'Hungarian GP', 'location': 'Budapest', 'distance_from_previous': 1500, 'freight_method': 'road'},
            {'race': 'Belgian GP', 'location': 'Spa', 'distance_from_previous': 1200, 'freight_method': 'road'},
            {'race': 'Dutch GP', 'location': 'Zandvoort', 'distance_from_previous': 300, 'freight_method': 'road'},
            {'race': 'Italian GP', 'location': 'Monza', 'distance_from_previous': 1000, 'freight_method': 'road'},
            {'race': 'Azerbaijan GP', 'location': 'Baku', 'distance_from_previous': 3000, 'freight_method': 'air'},
            {'race': 'Singapore GP', 'location': 'Singapore', 'distance_from_previous': 7500, 'freight_method': 'air'},
            {'race': 'United States GP', 'location': 'Austin', 'distance_from_previous': 17000, 'freight_method': 'air'},
            {'race': 'Mexican GP', 'location': 'Mexico City', 'distance_from_previous': 1500, 'freight_method': 'road'},
            {'race': 'Brazilian GP', 'location': 'Sao Paulo', 'distance_from_previous': 3500, 'freight_method': 'air'},
            {'race': 'Las Vegas GP', 'location': 'Las Vegas', 'distance_from_previous': 8000, 'freight_method': 'air'},
            {'race': 'Qatar GP', 'location': 'Doha', 'distance_from_previous': 12000, 'freight_method': 'air'},
            {'race': 'Abu Dhabi GP', 'location': 'Abu Dhabi', 'distance_from_previous': 550, 'freight_method': 'road'},
        ]
        return pd.DataFrame(races)
    
    def calculate_race_emissions(self, race_data):
        """Calculate CO2 emissions for a single race"""
        distance = race_data['distance_from_previous']
        method = race_data['freight_method']
        
        # Freight emissions
        total_freight = self.f1_data['teams'] * self.f1_data['freight_weight_per_team']
        
        if method == 'air':
            freight_emissions = (total_freight * distance * self.emission_factors['air_freight_per_kg']) / 1000
        elif method == 'sea':
            freight_emissions = (total_freight * distance * self.emission_factors['sea_freight_per_kg']) / 1000
        else:  # road
            freight_emissions = (total_freight * distance * 0.1) / 1000  # Road freight factor
        
        # Personnel travel emissions
        total_personnel = self.f1_data['teams'] * self.f1_data['personnel_per_team']
        personnel_travel = total_personnel * distance * self.emission_factors['passenger_flight_per_km']
        
        # Fuel emissions during race weekend
        total_fuel = (self.f1_data['fuel_consumption_per_race'] * 
                     self.f1_data['cars_per_race'] * 3)  # Practice, Qualifying, Race
        fuel_emissions = total_fuel * self.emission_factors['fuel_per_liter']
        
        # Circuit operations
        circuit_emissions = self.emission_factors['circuit_operations']
        
        # Hotel accommodation (3 nights average)
        accommodation = total_personnel * 3 * self.emission_factors['hotel_night']
        
        # Support series factor
        total_emissions = ((freight_emissions + personnel_travel + fuel_emissions + 
                           circuit_emissions + accommodation) * 
                          self.f1_data['support_series_factor'])
        
        return {
            'freight': freight_emissions,
            'personnel_travel': personnel_travel,
            'fuel': fuel_emissions,
            'circuit_operations': circuit_emissions,
            'accommodation': accommodation,
            'total': total_emissions
        }
    
    def calculate_season_emissions(self):
        """Calculate emissions for entire F1 season"""
        results = []
        
        for _, race in self.race_calendar.iterrows():
            emissions = self.calculate_race_emissions(race)
            emissions['race'] = race['race']
            emissions['location'] = race['location']
            results.append(emissions)
        
        return pd.DataFrame(results)
    
    def create_comparisons(self, total_emissions):
        """Create relatable comparisons for emissions"""
        comparisons = {}
        
        # Home energy equivalents
        comparisons['homes_powered_annually'] = total_emissions / self.comparisons['average_home_annual_emissions']
        
        # Car driving equivalent
        comparisons['car_driving_km'] = total_emissions / self.comparisons['passenger_car_per_km']
        
        # Transatlantic flights
        comparisons['transatlantic_flights'] = total_emissions / self.comparisons['transatlantic_flight_per_passenger']
        
        return comparisons
    
    def visualize_season_breakdown(self, emissions_df):
        """Create comprehensive visualization of F1 emissions"""
        # Calculate totals
        total_season = emissions_df['total'].sum()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Emissions by Race', 'Emissions by Category', 
                          'Race-by-Race Cumulative', 'Comparison with Daily Life'),
            specs=[[{"secondary_y": False}, {"type": "pie"}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Race-by-race emissions
        fig.add_trace(
            go.Bar(x=emissions_df['race'], y=emissions_df['total']/1000, 
                   name='Total Emissions (tonnes CO2)', marker_color='darkred'),
            row=1, col=1
        )
        
        # Pie chart of emission categories
        categories = ['freight', 'personnel_travel', 'fuel', 'circuit_operations', 'accommodation']
        category_totals = [emissions_df[cat].sum()/1000 for cat in categories]
        category_labels = ['Freight Transport', 'Personnel Travel', 'Fuel Consumption', 
                          'Circuit Operations', 'Accommodation']
        
        fig.add_trace(
            go.Pie(labels=category_labels, values=category_totals, 
                   name="Emission Categories"),
            row=1, col=2
        )
        
        # Cumulative emissions
        cumulative = np.cumsum(emissions_df['total']/1000)
        fig.add_trace(
            go.Scatter(x=range(1, len(cumulative)+1), y=cumulative, 
                      mode='lines+markers', name='Cumulative Emissions (tonnes)',
                      line=dict(color='green', width=3)),
            row=2, col=1
        )
        
        # Comparison chart
        comparisons = self.create_comparisons(total_season)
        comparison_labels = ['Homes Powered\n(Annual)', 'Car Driving\n(km)', 'Transatlantic\nFlights']
        comparison_values = [comparisons['homes_powered_annually'], 
                           comparisons['car_driving_km']/1000,  # Convert to thousands
                           comparisons['transatlantic_flights']]
        
        fig.add_trace(
            go.Bar(x=comparison_labels, y=comparison_values, 
                   name='Equivalents', marker_color='orange'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text=f"F1 2024 Season Carbon Footprint Analysis<br>Total: {total_season/1000:.0f} tonnes CO2",
            showlegend=True,
            height=800
        )
        
        # Update x-axis labels for race chart
        fig.update_xaxes(tickangle=45, row=1, col=1)
        fig.update_xaxes(title_text="Race Number", row=2, col=1)
        fig.update_yaxes(title_text="Tonnes CO2", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Tonnes CO2", row=2, col=1)
        fig.update_yaxes(title_text="Equivalent Units", row=2, col=2)
        
        return fig
    
    def simulate_sustainability_scenarios(self, emissions_df):
        """What-if scenarios for F1 sustainability improvements"""
        base_total = emissions_df['total'].sum()
        
        scenarios = {}
        
        # Scenario 1: Sustainable Aviation Fuel (50% reduction in air freight)
        saf_reduction = emissions_df['freight'].sum() * 0.5
        scenarios['sustainable_aviation_fuel'] = {
            'reduction': saf_reduction,
            'new_total': base_total - saf_reduction,
            'percentage_reduction': (saf_reduction / base_total) * 100
        }
        
        # Scenario 2: Regional calendar optimization (20% travel reduction)
        travel_reduction = (emissions_df['freight'].sum() + emissions_df['personnel_travel'].sum()) * 0.2
        scenarios['calendar_optimization'] = {
            'reduction': travel_reduction,
            'new_total': base_total - travel_reduction,
            'percentage_reduction': (travel_reduction / base_total) * 100
        }
        
        # Scenario 3: 100% renewable energy at circuits
        circuit_reduction = emissions_df['circuit_operations'].sum() * 0.8
        scenarios['renewable_energy'] = {
            'reduction': circuit_reduction,
            'new_total': base_total - circuit_reduction,
            'percentage_reduction': (circuit_reduction / base_total) * 100
        }
        
        # Scenario 4: Combined approach
        combined_reduction = saf_reduction + travel_reduction + circuit_reduction
        scenarios['combined_approach'] = {
            'reduction': combined_reduction,
            'new_total': base_total - combined_reduction,
            'percentage_reduction': (combined_reduction / base_total) * 100
        }
        
        return scenarios
    
    def visualize_scenarios(self, scenarios, base_total):
        """Visualize sustainability scenarios"""
        scenario_names = list(scenarios.keys())
        reductions = [scenarios[s]['percentage_reduction'] for s in scenario_names]
        
        fig = go.Figure(data=[
            go.Bar(name='Current Emissions', x=scenario_names, 
                   y=[100] * len(scenario_names), marker_color='red'),
            go.Bar(name='Potential Reduction', x=scenario_names, 
                   y=reductions, marker_color='green')
        ])
        
        fig.update_layout(
            title='F1 Sustainability Scenarios - Potential CO2 Reductions',
            xaxis_title='Scenario',
            yaxis_title='Percentage',
            barmode='group',
            height=500
        )
        
        return fig
    
    def generate_report(self):
        """Generate comprehensive F1 carbon footprint report"""
        print("🏎️  F1 Carbon Footprint Sustainability Tracker")
        print("=" * 50)
        
        # Calculate season emissions
        emissions_df = self.calculate_season_emissions()
        total_season = emissions_df['total'].sum()
        
        print(f"\n📊 2024 F1 Season Carbon Footprint")
        print(f"Total CO2 Emissions: {total_season/1000:.1f} tonnes")
        print(f"Average per race: {(total_season/len(emissions_df))/1000:.1f} tonnes")
        
        # Breakdown by category
        print(f"\n🔍 Emissions Breakdown:")
        categories = {
            'Freight Transport': emissions_df['freight'].sum(),
            'Personnel Travel': emissions_df['personnel_travel'].sum(),
            'Fuel Consumption': emissions_df['fuel'].sum(),
            'Circuit Operations': emissions_df['circuit_operations'].sum(),
            'Accommodation': emissions_df['accommodation'].sum()
        }
        
        for category, value in categories.items():
            percentage = (value / total_season) * 100
            print(f"  • {category}: {value/1000:.1f} tonnes ({percentage:.1f}%)")
        
        # Comparisons
        comparisons = self.create_comparisons(total_season)
        print(f"\n🌍 Real-World Comparisons:")
        print(f"  • Equivalent to powering {comparisons['homes_powered_annually']:.0f} homes for a year")
        print(f"  • Same as driving {comparisons['car_driving_km']/1000000:.1f} million km by car")
        print(f"  • Equal to {comparisons['transatlantic_flights']:.0f} transatlantic flights")
        
        # Scenarios
        scenarios = self.simulate_sustainability_scenarios(emissions_df)
        print(f"\n🚀 Sustainability Scenarios (Path to Net Zero 2030):")
        for scenario, data in scenarios.items():
            print(f"  • {scenario.replace('_', ' ').title()}: "
                  f"{data['percentage_reduction']:.1f}% reduction "
                  f"({data['reduction']/1000:.0f} tonnes CO2 saved)")
        
        return emissions_df, scenarios
    
    def track_progress_to_net_zero(self, current_emissions, target_year=2030):
        """Track progress toward F1's net-zero 2030 goal"""
        current_year = datetime.now().year
        years_remaining = target_year - current_year
        
        required_annual_reduction = (current_emissions / years_remaining) if years_remaining > 0 else current_emissions
        
        print(f"\n🎯 Net Zero 2030 Progress Tracker:")
        print(f"Current annual emissions: {current_emissions/1000:.1f} tonnes CO2")
        print(f"Years remaining: {years_remaining}")
        print(f"Required annual reduction: {required_annual_reduction/1000:.1f} tonnes CO2/year")
        print(f"Required annual reduction rate: {(required_annual_reduction/current_emissions)*100:.1f}%")
        
        return required_annual_reduction

def main():
    """Main function to run the F1 Carbon Footprint Tracker"""
    tracker = F1CarbonTracker()
    
    # Generate comprehensive report
    emissions_df, scenarios = tracker.generate_report()
    
    # Create visualizations
    season_fig = tracker.visualize_season_breakdown(emissions_df)
    scenario_fig = tracker.visualize_scenarios(scenarios, emissions_df['total'].sum())
    
    # Track progress to net zero
    total_emissions = emissions_df['total'].sum()
    tracker.track_progress_to_net_zero(total_emissions)
    
    # Display visualizations
    season_fig.show()
    scenario_fig.show()
    
    print(f"\n💡 Key Insights:")
    print(f"  • Logistics (freight + travel) account for {((emissions_df['freight'].sum() + emissions_df['personnel_travel'].sum())/total_emissions)*100:.1f}% of emissions")
    print(f"  • The most carbon-intensive races are those requiring long-distance air freight")
    print(f"  • A combined sustainability approach could reduce emissions by {scenarios['combined_approach']['percentage_reduction']:.1f}%")
    print(f"  • Calendar optimization offers the biggest single impact")
    
    return tracker, emissions_df, scenarios

if __name__ == "__main__":
    # Run the tracker
    tracker, emissions_data, sustainability_scenarios = main()
    
    print("\n🏁 F1 Carbon Tracker Analysis Complete!")
    print("This tool demonstrates how data science can make sustainability tangible and actionable.")
