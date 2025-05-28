# app/utils/helpers.py
from typing import Dict

def map_labels(notification: Dict, label_map: Dict[int, str]) -> Dict:
    """
    Maps numerical labels in a notification to their corresponding string representations.

    Args:
        notification (Dict): The notification dictionary containing labels.
        label_map (Dict[int, str]): Mapping of label IDs to names.

    Returns:
        Dict: Notification with mapped labels.
    """
    mapped_labels = []
    for label_obj in notification.get("labels", []):
        mapped_label = {label_map.get(int(k), k): v for k, v in label_obj.items()}
        mapped_labels.append(mapped_label)
    notification["labels"] = mapped_labels
    return notification

