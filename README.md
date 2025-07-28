# AutoEDA - Automated Exploratory Data Analysis

A modern web application for automated exploratory data analysis (EDA) that allows users to upload CSV files and generate various types of visualizations with an intuitive interface.

## Features

- **File Upload**: Drag-and-drop CSV file upload with validation
- **Multiple Plot Types**: Support for 8 different visualization types:
  - Histogram (distribution analysis)
  - Boxplot (outlier detection)
  - Countplot (categorical frequency)
  - Barplot (categorical vs numeric)
  - Lineplot (trends over time/categories)
  - Scatterplot (correlation analysis)
  - Heatmap (correlation matrix)
  - Pairplot (pairwise relationships)
- **Modern UI**: Responsive design with beautiful gradients and animations
- **Error Handling**: Comprehensive error handling and user feedback
- **Download Plots**: Save generated visualizations as PNG files
- **Session Management**: Maintains data across different analysis steps

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AutoEDA
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to `http://localhost:5000`

## Usage

1. **Upload Data**: 
   - Click "Choose a CSV file" or drag and drop your CSV file
   - Supported format: CSV files only (max 16MB)

2. **Select Columns**: 
   - Choose the columns you want to analyze
   - You can select multiple columns

3. **Choose Plot Type**: 
   - Select from 8 different visualization types
   - Each plot type has specific requirements (e.g., numeric columns for histograms)

4. **Generate Plot**: 
   - Click "Generate Plot" to create your visualization
   - View, download, or generate another plot

## Plot Type Requirements

| Plot Type | Requirements | Description |
|-----------|-------------|-------------|
| Histogram | 1+ numeric column | Distribution analysis |
| Boxplot | 1+ numeric column | Outlier detection |
| Countplot | 1+ categorical column | Frequency analysis |
| Barplot | 1 categorical + 1 numeric | Categorical vs numeric |
| Lineplot | 2 columns (1+ numeric) | Trend analysis |
| Scatterplot | 2 numeric columns | Correlation analysis |
| Heatmap | 2+ numeric columns | Correlation matrix |
| Pairplot | 2+ numeric columns | Pairwise relationships |

## File Structure

```
AutoEDA/
├── app.py                 # Main Flask application
├── autoeda_engine.py      # Plot generation engine
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── plots/            # Generated plot storage
├── templates/
│   ├── upload.html       # File upload page
│   ├── options.html      # Plot options page
│   ├── results.html      # Results display page
│   ├── 404.html          # 404 error page
│   └── 500.html          # 500 error page
└── uploads/              # Uploaded file storage
```

## Technical Details

### Backend
- **Framework**: Flask (Python)
- **Data Processing**: Pandas
- **Visualization**: Matplotlib + Seaborn
- **Session Management**: Flask sessions

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Interactive features and form validation
- **Font Awesome**: Icons
- **Responsive Design**: Mobile-friendly interface

### Data Processing
- Automatic data type detection and conversion
- Missing value handling
- Data validation for plot requirements
- Error handling for invalid data

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Empty or corrupted files
- Missing required columns
- Data type mismatches
- Plot generation failures
- File size limits

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please:
1. Check the error messages in the application
2. Ensure your CSV file is properly formatted
3. Verify that your data meets the requirements for the selected plot type
4. Check the browser console for any JavaScript errors

## Future Enhancements

- Support for more file formats (Excel, JSON)
- Additional plot types (violin plots, 3D plots)
- Interactive plots with Plotly
- Data preprocessing options
- Export analysis reports
- User accounts and saved analyses 