import cv2
import numpy as np
import uuid
import os

selected_label = {1, 2, 3, 4, 6, 8, 18, 19, 20, 21}

converted_label = {1: 1, 2: 2, 3: 2, 4: 2, 6: 2, 8: 2, 18: 3, 19: 3, 20: 3, 21: 3}

selected_label_map = {1: "insan", 2: "arac", 3: "hayvan"}

label_map = {
    0: "N/A",
    1: "person",
    2: "bicycle",
    3: "car",
    4: "motorcycle",
    5: "airplane",
    6: "bus",
    7: "train",
    8: "truck",
    9: "boat",
    10: "traffic light",
    11: "fire hydrant",
    12: "N/A",
    13: "stop sign",
    14: "parking meter",
    15: "bench",
    16: "bird",
    17: "cat",
    18: "dog",
    19: "horse",
    20: "sheep",
    21: "cow",
    22: "elephant",
    23: "bear",
    24: "zebra",
    25: "giraffe",
    26: "N/A",
    27: "backpack",
    28: "umbrella",
    29: "N/A",
    30: "N/A",
    31: "handbag",
    32: "tie",
    33: "suitcase",
    34: "frisbee",
    35: "skis",
    36: "snowboard",
    37: "sports ball",
    38: "kite",
    39: "baseball bat",
    40: "baseball glove",
    41: "skateboard",
    42: "surfboard",
    43: "tennis racket",
    44: "bottle",
    45: "N/A",
    46: "wine glass",
    47: "cup",
    48: "fork",
    49: "knife",
    50: "spoon",
    51: "bowl",
    52: "banana",
    53: "apple",
    54: "sandwich",
    55: "orange",
    56: "broccoli",
    57: "carrot",
    58: "hot dog",
    59: "pizza",
    60: "donut",
    61: "cake",
    62: "chair",
    63: "couch",
    64: "potted plant",
    65: "bed",
    66: "N/A",
    67: "dining table",
    68: "N/A",
    69: "N/A",
    70: "toilet",
    71: "N/A",
    72: "tv",
    73: "laptop",
    74: "mouse",
    75: "remote",
    76: "keyboard",
    77: "cell phone",
    78: "microwave",
    79: "oven",
    80: "toaster",
    81: "sink",
    82: "refrigerator",
    83: "N/A",
    84: "book",
    85: "clock",
    86: "vase",
    87: "scissors",
    88: "teddy bear",
    89: "hair drier",
    90: "toothbrush",
}


def draw_detections_with_threshold(
    img, result, label_map=label_map, score_threshold=0.5
):
    """
    Obje tespitlerini görüntüye çizer.

    Args:
        img (numpy.ndarray): Görüntü (BGR formatinda).
        result (dict): Modelden dönen sonuçlar (boxes, labels, scores).
        label_map (dict): Label numaralarini açiklayici isimlere dönüştürmek için kullanilan sözlük.
        score_threshold (float): Minimum skor eşiği (güven skoru).

    Returns:
        numpy.ndarray: Üzerine tespitler çizilmiş görüntü.
    """
    boxes = result["boxes"].cpu().detach().numpy()
    scores = result["scores"].cpu().detach().numpy()
    labels = result["labels"].cpu().detach().numpy()

    # Görüntüyü kopyala (orijinali değiştirmemek için)
    img_copy = img.copy()

    for box, score, label in zip(boxes, scores, labels):
        if score >= score_threshold:  # Skor eşiğine göre filtrele
            x1, y1, x2, y2 = map(int, box)  # Box koordinatlarini integer yap
            color = (0, 255, 0)  # Kutunun rengi (yeşil)
            thickness = 1  # Çizgi kalinliği

            # Kutuyu çiz
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)

            # Etiket ve skor bilgisini ekle
            label_name = (
                label_map.get(label, str(label)) if label_map else f"Label {label}"
            )
            text = f"{label_name}: {score:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1

            # Metin boyutunu al ve metni kutunun üzerine yerleştir
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            text_x, text_y = x1, y1 - 10  # Metin koordinatlari

            # Metnin arka planini çiz (okunabilirlik için)
            cv2.rectangle(
                img_copy,
                (text_x, text_y - text_size[1] - 2),
                (text_x + text_size[0], text_y + 2),
                (0, 255, 0),
                -1,
            )
            # Metni çiz
            cv2.putText(
                img_copy,
                text,
                (text_x, text_y),
                font,
                font_scale,
                (0, 0, 0),
                font_thickness,
            )

    return img_copy


def draw_detections(img, result, label_map=label_map) -> np.ndarray:
    """
    Obje tespitlerini görüntüye çizer.

    Args:
        img (numpy.ndarray): Görüntü (BGR formatinda).
        result (dict): Modelden dönen sonuçlar (boxes, labels, scores).
        label_map (dict): Label numaralarini açiklayici isimlere dönüştürmek için kullanilan sözlük.

    Returns:
        numpy.ndarray: Üzerine tespitler çizilmiş görüntü.
    """
    boxes = result["boxes"].cpu().detach().numpy()
    scores = result["scores"].cpu().detach().numpy()
    labels = result["labels"].cpu().detach().numpy()

    # Görüntüyü kopyala (orijinali değiştirmemek için)
    img_copy = img.copy()

    for box, score, label in zip(boxes, scores, labels):
        x1, y1, x2, y2 = map(int, box)  # Box koordinatlarini integer yap
        color = (0, 255, 0)  # Kutunun rengi (yeşil)
        thickness = 2  # Çizgi kalinliği

        # Kutuyu çiz
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)

        # Etiket ve skor bilgisini ekle
        label_name = label_map.get(label, str(label)) if label_map else f"Label {label}"
        text = f"{label_name}: {score:.2f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1

        # Metin boyutunu al ve metni kutunun üzerine yerleştir
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x, text_y = x1, y1 - 10  # Metin koordinatlari

        # Metnin arka planini çiz (okunabilirlik için)
        cv2.rectangle(
            img_copy,
            (text_x, text_y - text_size[1] - 2),
            (text_x + text_size[0], text_y + 2),
            (0, 255, 0),
            -1,
        )
        # Metni çiz
        cv2.putText(
            img_copy,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (0, 0, 0),
            font_thickness,
        )

    return img_copy


def draw_detections_batch(imgs, results, label_map=label_map):
    """
    Birden fazla görüntü ve sonuçlari işleyerek obje tespitlerini çizer.

    Args:
        imgs (list of numpy.ndarray): Görüntülerin listesi (BGR formatinda).
        results (list of dict): Her görüntü için modelden dönen sonuçlar (boxes, labels, scores).
        label_map (dict, optional): Label numaralarini açiklayici isimlere dönüştürmek için kullanilan sözlük.

    Returns:
        list of numpy.ndarray: Üzerine tespitler çizilmiş görüntülerin listesi.
    """
    assert len(imgs) == len(
        results
    ), "Görüntüler ve sonuçlar listesi ayni uzunlukta olmali."

    output_imgs = []

    for img, result in zip(imgs, results):
        boxes = result["boxes"].cpu().detach().numpy()
        scores = result["scores"].cpu().detach().numpy()
        labels = result["labels"].cpu().detach().numpy()

        # Görüntüyü kopyala (orijinali değiştirmemek için)
        img_copy = img.copy()

        for box, score, label in zip(boxes, scores, labels):
            x1, y1, x2, y2 = map(int, box)  # Box koordinatlarini integer yap
            color = (0, 255, 0)  # Kutunun rengi (yeşil)
            thickness = 2  # Çizgi kalinliği

            # Kutuyu çiz
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)

            # Etiket ve skor bilgisini ekle
            label_name = (
                label_map.get(label, str(label)) if label_map else f"Label {label}"
            )
            text = f"{label_name}: {score:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1

            # Metin boyutunu al ve metni kutunun üzerine yerleştir
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            text_x, text_y = x1, y1 - 10  # Metin koordinatlari

            # Metnin arka planini çiz (okunabilirlik için)
            cv2.rectangle(
                img_copy,
                (text_x, text_y - text_size[1] - 2),
                (text_x + text_size[0], text_y + 2),
                (0, 255, 0),
                -1,
            )
            # Metni çiz
            cv2.putText(
                img_copy,
                text,
                (text_x, text_y),
                font,
                font_scale,
                (0, 0, 0),
                font_thickness,
            )

        # İşlenmiş görüntüyü listeye ekle
        output_imgs.append(img_copy)

    return output_imgs


def filter_results(result, threshold=0.5):
    """
    Tespit sonuçlarini skor eşiğine göre filtreler.

    Args:
        result (dict): Modelin döndürdüğü sonuçlar (boxes, labels, scores).
        threshold (float): Skor eşiği.

    Returns:
        dict: Filtrelenmiş sonuçlar.
    """
    scores = result["scores"].cpu().detach().numpy()
    boxes = result["boxes"].cpu().detach().numpy()
    labels = result["labels"].cpu().detach().numpy()

    # Skor eşiğine göre filtreleme
    indices = scores >= threshold
    return {
        "scores": scores[indices],
        "boxes": boxes[indices],
        "labels": labels[indices],
    }


def decode_img(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def write_image(image):
    if isinstance(image, bytes):
        img = decode_img(image)

        unique_id = str(uuid.uuid4())
        cv2.imwrite(f"output/{unique_id}.jpg", img)
    elif isinstance(image, list):
        print("Received a list instead of a frame byte array.")
        for _img in image:
            img = decode_img(_img)
            unique_id = str(uuid.uuid4())
            cv2.imwrite(f"output/{unique_id}.jpg", img)

    elif isinstance(image, np.ndarray):
        unique_id = str(uuid.uuid4())
        cv2.imwrite(f"output/{unique_id}.jpg", image)
    else:
        raise TypeError(
            f"Expected 'frame' to be of type 'bytes' or 'list[bytes]', but got {type(image)}."
        )


def save_images(output_dir, processed_images):
    """
    İşlenmiş görüntüleri belirtilen bir dizine kaydeder.

    Args:
        output_dir (str): Görüntülerin kaydedileceği dizin yolu.
        processed_images (list of numpy.ndarray): Kaydedilecek işlenmiş görüntülerin listesi.
        prefix (str): Dosya adlari için ön ek.

    Returns:
        None
    """
    # Çikiş dizini yoksa oluştur
    os.makedirs(output_dir, exist_ok=True)

    for i, img in enumerate(processed_images):
        unique_id = str(uuid.uuid4())
        filename = os.path.join(output_dir, f"{unique_id}.jpg")
        success = cv2.imwrite(filename, img)
        if not success:
            print(f"Failed to save: {filename}")


def draw_detection_with_det(img, det, label_map=selected_label_map) -> np.ndarray:
    """
    `det` değişkenindeki bilgileri kullanarak tespit edilen objeyi görüntüye çizer.

    Args:
        img (numpy.ndarray): Görüntü (BGR formatinda).
        det (list): Tespit bilgisi [x1, y1, x2, y2, obje_id, etiket].
        label_map (dict, optional): Etiket numaralarini açiklayici isimlere dönüştürmek için kullanilir.

    Returns:
        numpy.ndarray: Üzerine tespit çizilmiş görüntü.
    """
    # Koordinatlari ve diğer bilgileri al
    x1, y1, x2, y2, obj_id, label = det
    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])  # Koordinatlari tam sayiya dönüştür
    color = (0, 255, 0)  # Kutunun rengi (yeşil)
    thickness = 2  # Çizgi kalinliği

    # if isinstance(img, bytes):
    #     img = decode_img(img)

    # Görüntüyü kopyala (orijinali değiştirmemek için)
    # img_copy = img.copy()

    # Kutuyu çiz
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

    # Etiket bilgisini ekle
    label_name = (
        label_map.get(label, f"Label {label}") if label_map else f"Label {label}"
    )
    text = f"{label_name} (ID: {int(obj_id)})"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1

    # Metin boyutunu al ve metni kutunun üzerine yerleştir
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_x, text_y = x1, y1 - 10  # Metin koordinatlari

    # Metnin arka planini çiz (okunabilirlik için)
    cv2.rectangle(
        img,
        (text_x, text_y - text_size[1] - 2),
        (text_x + text_size[0], text_y + 2),
        (0, 255, 0),
        -1,
    )
    # Metni çiz
    cv2.putText(
        img, text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness
    )

    return img
