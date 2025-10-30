import argparse
import os
import glob
import h5py
import csv
import json
from datetime import datetime
from tqdm import tqdm


def analyze_hdf5_files(data_dir):
    """Analyze HDF5 files and aggregate action steps and segment counts"""
    hdf5_files = glob.glob(os.path.join(data_dir, "**", "*.hdf5"), recursive=True)
    if not hdf5_files:
        print("No HDF5 files found in the specified directory at {path}.".format(path=data_dir))
        exit(1)

    total_action_steps = 0
    total_action_segments = 0

    for file_path in hdf5_files:
        try:
            with h5py.File(file_path, "r") as f:
                action_shape = f['action'].shape
                total_action_steps += action_shape[0]
                if 'label/task_timestep' in f:
                    label_shape = f['label/task_timestep'].shape
                    total_action_segments += label_shape[0]
                else:
                    total_action_segments += 0
        except Exception as e:
            print(f"Error opening {file_path}: {e}")
            continue
    return len(hdf5_files), total_action_steps, total_action_segments

def load_meta_info():
    """Get information from meta.json"""
    meta_path = os.path.join(os.path.dirname(__file__), "../", "config", "meta.json")
    with open(meta_path, 'r') as meta_file:
        meta_info = json.load(meta_file)
        return {
            "robot_id": meta_info.get("ROBOT_ID", ""),
            "operator_id": meta_info.get("OPERATOR_ID", ""),
            "link": meta_info.get("LINK", ""),
            "note": meta_info.get("NOTE", ""),
            "environment": meta_info.get("ENVIRONMENT", ""),
            "software_version": meta_info.get("SOFTWARE_VERSION", ""),
            "frame_rate": meta_info.get("FRAME_RATE", 50),
            "target_item": meta_info.get("TARGET_ITEM", ""),
            "target_area": meta_info.get("TARGET_AREA", ""),
            "data_type": meta_info.get("DATA_TYPE", ""),
            "data_description": meta_info.get("DATA_DESCRIPTION", ""),
        }


def analyze_codebase_and_save_csv(codebase_dir, output_dir="./data"):
    """
    List up folders in codebase_dir, analyze HDF5 files in each folder,
    and save a CSV summary list to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    meta_info = load_meta_info()
    folder_paths = [
        os.path.join(codebase_dir, d)
        for d in os.listdir(codebase_dir)
        if os.path.isdir(os.path.join(codebase_dir, d))
    ]

    folder_paths = [
        path for path in folder_paths
        if not any([
            os.path.basename(path).startswith('.'),
            '.Trash' in os.path.basename(path),
            os.path.basename(path).lower().startswith('temp'),
            os.path.basename(path).lower().startswith('test'),
            os.path.basename(path).lower().startswith('backup'),
            'temp' in os.path.basename(path).lower(),
            'test' in os.path.basename(path).lower(),
            'backup' in os.path.basename(path).lower(),
        ])
    ]

    summary_rows = []
    with tqdm(folder_paths, desc="Analyzing folders") as pbar:
        for folder in pbar:
            num_datasets, total_action_steps, total_action_segments = analyze_hdf5_files(folder)

            if total_action_segments == 0:
                tqdm.write(f"Warning: 'label/task_timestep' not found in {folder}. Skipping segment count for this file.")

            total_seconds = total_action_steps / meta_info["frame_rate"]
            total_hours = total_seconds / 3600.0
            summary_rows.append([
                os.path.basename(folder),
                total_seconds,
                total_hours,
                total_action_steps,
                total_action_segments,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                meta_info["robot_id"],
                meta_info["operator_id"],
                meta_info["environment"],
                meta_info["software_version"],
                meta_info["target_item"],
                "",
                "",
                meta_info["data_description"],
            ])

            pbar.set_postfix({
                "Folder": os.path.basename(folder),
                "Datasets": num_datasets,
                "Action Steps": total_action_steps,
                "Action Segments": total_action_segments,
            })
            pbar.refresh()

    csv_path = os.path.join(output_dir, "summary_hdf5.csv")
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Task Name (Identifier)",
            "Total Time (seconds)",
            "Total Time (hours)",
            "Frame Count",
            "Frame Rate",
            "Robot ID",
            "Operator ID",
            "Segment Count",
            "Record Time",
            "Environment",
            "Software Version",
            "Target Item",
            "Link",
            "Note",
            "Data Description",
        ])
        writer.writerows(summary_rows)
    print(f"Summary CSV saved to: {csv_path}")

    # Print summary statistics to console
    print("\n=== Summary Statistics ===")
    print(f"Total folders analyzed: {len(folder_paths)}")
    print(f"Total action frames: {sum(row[3] for row in summary_rows)}")
    print(f"Total action segments: {sum(row[4] for row in summary_rows)}")
    print(f"Total time (seconds): {sum(row[1] for row in summary_rows):.2f}")
    print(f"Total time (hours): {sum(row[2] for row in summary_rows):.2f}")

    # Save summary statistics as JSON
    summary_json = {
        "total_folders_analyzed": len(folder_paths),
        # "total_datasets": sum(row[1] for row in summary_rows),
        "total_action_steps": sum(row[3] for row in summary_rows),
        "total_action_segments": sum(row[4] for row in summary_rows),
        "total_time_seconds": round(sum(row[1] for row in summary_rows), 2),
        "total_time_hours": round(sum(row[2] for row in summary_rows), 2),
        "record_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    json_path = os.path.join(output_dir, "hdf5_total_summary.json")
    with open(json_path, "w") as jf:
        json.dump(summary_json, jf, ensure_ascii=False, indent=2)
    print(f"Summary JSON saved to: {json_path}")

def main():
    parser = argparse.ArgumentParser(description="Analyze HDF5 file for compression and chunking information.")
    parser.add_argument("all", type=str, help="Path to folder for batch analysis.")
    args = parser.parse_args()

    if args.all:
        analyze_codebase_and_save_csv(args.all, output_dir=os.path.join(os.path.dirname(__file__), "../../data"))
        return

if __name__ == "__main__":
    main()