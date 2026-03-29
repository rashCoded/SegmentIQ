# SegmentIQ: Market Basket Analysis & Retail Analytics

SegmentIQ is a premium retail analytics application that helps businesses discover customer purchasing patterns through Market Basket Analysis (Apriori Algorithm) and interactive dashboards.

## 🚀 How to Run the App (Quick Start)

The easiest way to explore the project is using the interactive **Streamlit App**.

1.  **Open Terminal** in the project folder:
    ```bash
    cd d:\Projects\SegmentIQ
    ```

2.  **Install Dependencies** (One time setup):
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the App**:
    ```bash
    streamlit run app.py
    ```

   The app will automatically open in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

- **`app.py`**: The main application file (Streamlit). Contains the Dashboard, Recommender System, and Apriori Logic.
- **`run_project.py`**: Legacy script to run the raw analysis notebooks sequentially.
- **`RetailData.csv`**: Transaction dataset (will be downloaded automatically if missing).
- **Notebooks**:
    - `01-FeatureEngineering.ipynb`: Data cleaning and feature creation logic.
    - `02-ExploratoryDataAnalysis.ipynb`: In-depth EDA and plotting.
    - `03-MarketBasketAnalysis.ipynb`: Original logic for association rules.

## ✨ Key Features in the App

*   **Interactive Dashboard**: Real-time sales metrics and trends.
*   **Product Recommender**: Select a product -> Get "Frequently bought with" suggestions.
*   **Operational Insights**: Heatmap of busy hours (Day vs Hour).
*   **Smart Filtering**: Top 150 items only + High Confidence rules.
*   **Export**: Download resulting rules as CSV.

## 🛠 Troubleshooting

*   **`MemoryError`**: If you see this, the app works fine because we have already optimized it (Top 150 items limit, Max Length=2).
*   **Encoding Errors**: The app automatically fixes `ISO-8859-1` vs `UTF-8` issues on startup.
