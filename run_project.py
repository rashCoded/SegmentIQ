import os
import subprocess
import sys
import urllib.request

DATA_URL = "https://raw.githubusercontent.com/shricharan-ks/Retail-datasets/master/Online%20Retail.csv"

def install_dependencies():
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_and_download_data():
    if not os.path.exists("RetailData.csv"):
        print("'RetailData.csv' not found.")
        print(f"Downloading from {DATA_URL}...")
        try:
            urllib.request.urlretrieve(DATA_URL, "RetailData.csv")
            print("Download complete.")
            
            # Convert to UTF-8 to avoid encoding issues in notebooks
            print("Converting csv to UTF-8...")
            try:
                with open("RetailData.csv", "r", encoding="ISO-8859-1") as f:
                    content = f.read()
                with open("RetailData.csv", "w", encoding="utf-8") as f:
                    f.write(content)
                print("Conversion successful.")
            except Exception as e:
                print(f"Encoding conversion failed (might already be utf-8?): {e}")

        except Exception as e:
            print(f"Failed to download data: {e}")
            return False
            
    # Patch Notebook 01 to not drop 2010 data (since sample might be only 2010)
    try:
        with open("01-FeatureEngineering.ipynb", "r", encoding="utf-8") as f:
            nb_content = f.read()
        
        if 'retail.drop(index_names, inplace = True)' in nb_content:
            print("Patching 01-FeatureEngineering.ipynb to keep 2010 data...")
            nb_content = nb_content.replace(
                '"retail.drop(index_names, inplace = True)\\n",', 
                '"# retail.drop(index_names, inplace = True)\\n",'
            )
            with open("01-FeatureEngineering.ipynb", "w", encoding="utf-8") as f:
                f.write(nb_content)
            print("Patch applied.")
    except Exception as e:
        print(f"Failed to patch notebook: {e}")

    return True

def run_notebook(notebook_name):
    print(f"Running {notebook_name}...")
    try:
        import papermill as pm
        pm.execute_notebook(
            notebook_name,
            notebook_name.replace(".ipynb", "_output.ipynb"),
            kernel_name='python3'
        )
        print(f"Successfully ran {notebook_name}")
    except Exception as e:
        print(f"Error running {notebook_name}: {e}")
        return False
    return True

def main():
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found.")
        return

    install_dependencies()

    if not check_and_download_data():
        # We can try to proceed if CleanRetailData.csv exists, maybe?
        if os.path.exists("CleanRetailData.csv"):
            print("Found 'CleanRetailData.csv', skipping step 1 (Feature Engineering)...")
            notebooks = [
                "02-ExploratoryDataAnalysis.ipynb",
                "03-MarketBasketAnalysis.ipynb"
            ]
        else:
            print("Cannot proceed without data.")
            return
    else:
        notebooks = [
            "01-FeatureEngineering.ipynb",
            "02-ExploratoryDataAnalysis.ipynb",
            "03-MarketBasketAnalysis.ipynb"
        ]

    for nb in notebooks:
        if not run_notebook(nb):
            break
    
    print("Project run complete.")

if __name__ == "__main__":
    main()
