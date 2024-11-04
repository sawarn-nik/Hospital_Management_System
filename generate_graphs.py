import matplotlib.pyplot as plt
import numpy as np

# Data for plotting
x = np.arange(1, 11)
y1 = np.random.randint(1, 100, size=10)  # Random patient visits for 10 days
y2 = np.random.randint(1, 100, size=10)  # Random treatment outcomes

# Creating the first graph (Patient Visits)
plt.figure(figsize=(15, 5))
plt.subplot(1, 3, 1)  # First plot in a 1x3 grid
plt.bar(x, y1, color='#004d40')  # Dark teal color for the bars
plt.title('Patient Visits Over 10 Days', fontsize=16, color='#004d40', pad=20)  # Adding padding to the title
plt.xlabel('Days', fontsize=14)
plt.ylabel('Number of Patients', fontsize=14)
plt.xticks(x)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Creating the second graph (Treatment Outcomes)
plt.subplot(1, 3, 2)  # Second plot in a 1x3 grid
plt.plot(x, y2, marker='o', color='#00796b', linestyle='-', linewidth=2)  # Lighter shade of teal
plt.title('Treatment Outcomes', fontsize=16, color='#004d40', pad=20)  # Adding padding to the title
plt.xlabel('Days', fontsize=14)
plt.ylabel('Outcome Score', fontsize=14)
plt.xticks(x)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Data for the pie chart (Facilities Provided)
facilities = ['Emergency Care', 'Inpatient Services', 'Outpatient Services', 'Surgical Services', 'Diagnostic Imaging']
sizes = [25, 35, 20, 15, 5]  # Represents the percentage of each facility

# Define colors using a dark teal palette
pie_colors = ['#004d40', '#00796b', '#009688', '#80cbc4', '#b2dfdb']

# Creating the third graph (Facilities Pie Chart)
plt.subplot(1, 3, 3)  # Third plot in a 1x3 grid
wedges, texts, autotexts = plt.pie(
    sizes, labels=None, colors=pie_colors, startangle=140, explode=(0.1, 0, 0, 0, 0), autopct='%1.1f%%'
)

# Positioning labels outside the pie chart with adjusted spacing
label_distance = 1.5  # Increased radial distance for clearer label spacing
for i, wedge in enumerate(wedges):
    angle = (wedge.theta1 + wedge.theta2) / 2.0
    x = label_distance * wedge.r * np.cos(np.deg2rad(angle))  # Position labels further outside
    y = label_distance * wedge.r * np.sin(np.deg2rad(angle))
    ha = 'right' if angle > 90 else 'left'  # Adjust horizontal alignment based on position
    plt.text(x, y, facilities[i], ha=ha, va='center', color='#004d40', fontsize=10, fontweight='bold')

plt.axis('equal')
plt.title('Facilities Provided', fontsize=16, color='#004d40', pad=35)  # Additional padding for the title

# Save all graphs in a single row with a consistent style
plt.tight_layout()
plt.savefig('static/all_charts.png', bbox_inches='tight', dpi=300)
plt.show()