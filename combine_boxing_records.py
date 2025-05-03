import pandas as pd
import os
import glob

# Load bios if available
bio_data = {}
if os.path.exists("fighter_bios.csv"):
    bios_df = pd.read_csv("fighter_bios.csv")
    bios_df.columns = [col.strip() for col in bios_df.columns]
    for _, row in bios_df.iterrows():
        bio_data[row["Name"]] = {
            "Height": row.get("Height", None),
            "Reach": row.get("Reach", None),
            "Stance": row.get("Stance", None),
            "Weight": row.get("Weight", None)
        }

# Collect all fight records
all_records = []

for file_path in glob.glob("records/*_record.csv"):
    filename = os.path.basename(file_path)
    name = filename.replace("_record.csv", "").replace("_", " ")

    try:
        df = pd.read_csv(file_path)
        df.columns = [col.strip() for col in df.columns]

        if "Opponent" not in df.columns:
            print(f"⚠️ 'Opponent' column not found in: {filename}")
            continue

        df.insert(0, "Name", name)

        # Add bio fields
        bio = bio_data.get(name, {})
        df["Height"] = bio.get("Height", None)
        df["Reach"] = bio.get("Reach", None)
        df["Stance"] = bio.get("Stance", None)
        df["Weight"] = bio.get("Weight", None)

        # Reorder columns for clarity
        core_cols = ["Name", "Height", "Reach", "Stance", "Weight", "Opponent"]
        other_cols = [col for col in df.columns if col not in core_cols]
        df = df[core_cols + other_cols]

        all_records.append(df)
        print(f"✅ Processed: {name}")

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")

# Save the merged file
if all_records:
    combined_df = pd.concat(all_records, ignore_index=True)
    combined_df.to_csv("all_fighter_records.csv", index=False)
    print("\n🎉 Combined CSV saved as all_fighter_records.csv")
else:
    print("🚫 No valid record files found.")
