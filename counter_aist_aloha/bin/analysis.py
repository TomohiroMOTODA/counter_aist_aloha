import argparse
import os
import glob
import h5py
import csv
import json
from datetime import datetime

def analyze_hdf5_files(data_dir):
    """Analyze HDF5 files and aggregate action steps and segment counts"""
    hdf5_files = glob.glob(os.path.join(data_dir, "**", "*.hdf5"), recursive=True)
    if not hdf5_files:
        print("No HDF5 files found in the specified directory.")
        exit(1)

    total_action_steps = 0
    total_action_segments = 0

    for file_path in hdf5_files:
        with h5py.File(file_path, "r") as f:
            action_shape = f['action'].shape
            total_action_steps += action_shape[0]
            label_shape = f['label/task_timestep'].shape
            total_action_segments += label_shape[0]

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

def write_summary_csv(data_dir, summary):
    """Write summary results to CSV and display contents"""
    csv_path = os.path.join(data_dir, "hdf5_analysis_summary.csv")
    with open(csv_path, mode='w', newline='') as summary_file:
        summary_writer = csv.writer(summary_file)
        summary_writer.writerow([
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
        summary_writer.writerow([
            summary["task_name"],
            summary["total_seconds"],
            summary["total_hours"],
            summary["frame_count"],
            summary["frame_rate"],
            summary["robot_id"],
            summary["operator_id"],
            summary["segment_count"],
            summary["record_time"],
            summary["environment"],
            summary["software_version"],
            summary["target_item"],
            "",
            "", 
            summary["data_description"],
        ])
    with open(csv_path, 'r') as summary_file:
        print(summary_file.read())

def main():
    parser = argparse.ArgumentParser(description="Analyze HDF5 file for compression and chunking information.")
    parser.add_argument("data_dir", type=str, help="Path to the HDF5 file to analyze.")
    args = parser.parse_args()

    meta_info = load_meta_info()
    num_datasets, total_action_steps, total_action_segments = analyze_hdf5_files(args.data_dir)
    total_seconds = total_action_steps / meta_info["frame_rate"]
    total_hours = total_seconds / 3600.0

    print("Total number of datasets:", num_datasets)
    print("Total action steps across all datasets:", total_action_steps)
    print(f" total time: {total_seconds} seconds")
    print(f" total action steps per dataset: {total_hours} hours")
    print(f"Total action segments across all datasets:", total_action_segments)
    print("Analysis complete.")

    
    summary = {
        "task_name": os.path.basename(args.data_dir),
        "total_seconds": total_seconds,
        "total_hours": total_hours,
        "frame_count": total_action_steps,
        "robot_id": meta_info["robot_id"],
        "operator_id": meta_info["operator_id"],
        "segment_count": total_action_segments,
        "record_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": meta_info["environment"],
        "software_version": meta_info["software_version"],
        "frame_rate": meta_info["frame_rate"],
        "target_item": meta_info["target_item"],
        "data_description": meta_info["data_description"],
    }
    write_summary_csv(args.data_dir, summary)

if __name__ == "__main__":
    main()