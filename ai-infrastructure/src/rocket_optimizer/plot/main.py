from rocket_optimizer.DynamicDatabase import Results
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from matplotlib.ticker import ScalarFormatter
import numpy as np
import io


def plot(fold, num_iterations):
    # Create a PDF file and add the plots
    pdf_file = fold + "/plots.pdf"
    pdf = canvas.Canvas(pdf_file, pagesize=letter)

    for key in Results._data:
        # Create a plot
        plt.figure()
        print(Results._data[key])
        plt.plot(Results._data[key])
        plt.xlabel("Iteration")

        # Get the unit, description, and variable name for the current key
        unit = Results.get_units(key)
        description = Results.get_description(key)
        variable_name = Results.get_variable_name(key)

        # Use LaTeX formatting for the ylabel
        plt.ylabel(f"${variable_name}$ [${unit}$]")
        plt.title(description)
        plt.grid(True)

        # Set exactly num_iterations ticks on the x-axis
        max_index = len(Results._data[key]) - 1
        ticks = np.linspace(0, max_index, num=num_iterations+1, dtype=int)
        plt.xticks(ticks=ticks, labels=[str(i) for i in range(num_iterations+1)])

        # Adjust the y-axis scale formatting to avoid scientific notation or offsets
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False))

        # Optional: Set y-axis limits if needed
        plt.ylim(min(Results._data[key]) - 1, max(Results._data[key]) + 1)

        # Adjust layout to prevent cutting off labels
        plt.tight_layout()

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        # Add the plot to the PDF
        pdf.drawImage(ImageReader(buf), 100, 500, width=400, height=300)
        pdf.showPage()

    # Save the PDF
    pdf.save()
