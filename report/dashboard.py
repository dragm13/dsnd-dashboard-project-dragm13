from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# Import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
)

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/Dropdown called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    # Overwrite the build_component method ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, model=None, **kwargs):
        # Set the `label` attribute so it is set to the `name` attribute for the model
        self.label = model.name
        # Return the output from the parent class's build_component method
        return super().build_component(model=model, **kwargs)

    # Overwrite the `component_data` method
    def component_data(self, model=None, **kwargs):
        # Using the model argument, call the employee_events method that returns the user-type's names and ids
        if model.name == "employee":
            return model.names()
        elif model.name == "team":
            return model.names()


# Create a subclass of base_components/BaseComponent called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    def build_component(self, model=None, **kwargs):
        # Using the model argument for this method, return a fasthtml H1 object containing the model's name attribute
        return H1(model.name)


# Create a subclass of base_components/MatplotlibViz called `LineChart`
class LineChart(MatplotlibViz):

    # Overwrite the parent class's `visualization` method
    def visualization(self, model=None, asset_id=None, **kwargs):
        # Pass the `asset_id` argument to the model's `event_counts` method to receive the x (Day) and y (event count)
        data = model.event_counts(asset_id)

        # Use pandas to handle missing values
        data = data.fillna(0)

        # Set the date column as the index
        data.set_index('event_date', inplace=True)

        # Sort the index
        data.sort_index(inplace=True)

        # Change the data to cumulative counts
        data['positive_events'] = data['positive_events'].cumsum()
        data['negative_events'] = data['negative_events'].cumsum()

        # Initialize a pandas subplot and assign the figure and axis to variables
        fig, ax = plt.subplots()

        # Plot the cumulative counts
        data[['positive_events', 'negative_events']].plot(ax=ax)

        # Set the axis styling
        self.set_axis_styling(ax, border_color='black', font_color='black')

        # Set title and labels for x and y axis
        ax.set_title("Employee Event Counts", fontsize=20)
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Event Count")


# Create a subclass of base_components/MatplotlibViz called `BarChart`
class BarChart(MatplotlibViz):
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    def visualization(self, model=None, asset_id=None, **kwargs):
        # Using the model and asset_id arguments, pass the `asset_id` to the `.model_data` method
        data = model.model_data(asset_id)

        # Using the predictor class attribute, pass the data to the `predict_proba` method
        predictions = self.predictor.predict_proba(data)

        # Index the second column of predict_proba output
        pred = predictions[:, 1].mean() if model.name == "team" else predictions[0, 1]

        # Initialize a matplotlib subplot
        fig, ax = plt.subplots()

        # Plot the bar chart
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        # Set the axis styling
        self.set_axis_styling(ax, border_color='black', font_color='black')


# Create a subclass of combined_components/CombinedComponent called Visualizations
class Visualizations(CombinedComponent):

    # Set the `children` class attribute to a list containing initialized instances of `LineChart` and `BarChart`
    children = [
        LineChart(),
        BarChart()
    ]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')


# Create a subclass of base_components/DataTable called `NotesTable`
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    def component_data(self, model=None, entity_id=None, **kwargs):
        # Using the model and entity_id arguments, pass the entity_id to the model's .notes method
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection"
        )
    ]


# Create a subclass of CombinedComponents called `Report`
class Report(CombinedComponent):

    # Set the `children` class attribute to a list containing initialized instances of the header, dashboard filters, data visualizations, and notes table
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]


# Initialize a fasthtml app
app = FastHTML()

# Initialize the `Report` class
report = Report()

# Create a route for a GET request. Set the route's path to the root
@app.get('/')
def index(request):
    # Call the initialized report, pass the integer 1 and an instance of the Employee class as arguments
    return report(request, 1, Employee())

# Create a route for a GET request for an employee ID
@app.get('/employee/{id}')
def employee(request
